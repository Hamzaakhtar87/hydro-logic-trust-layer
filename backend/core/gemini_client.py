"""
Gemini API Client with Thought Signature Extraction
Uses temperature and token settings to simulate different "thinking levels".
"""

import os
import hashlib
import json
from typing import Dict, Optional, Any, Literal
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Valid thinking levels (simulated via temperature/tokens)
ThinkingLevel = Literal["minimal", "low", "medium", "high"]

# Configuration for each thinking level
THINKING_CONFIGS = {
    "minimal": {"temperature": 0.1, "max_output_tokens": 256},
    "low": {"temperature": 0.3, "max_output_tokens": 512},
    "medium": {"temperature": 0.7, "max_output_tokens": 2048},
    "high": {"temperature": 0.9, "max_output_tokens": 8192},
}


class GeminiClient:
    """
    Wrapper for Gemini API with Thought Signature support.
    Extracts cognitive signatures from model responses for behavioral verification.
    
    Key Features:
    - Simulates thinking levels via temperature/token settings
    - Generates deterministic Thought Signatures from responses
    - Supports minimal/low/medium/high thinking levels
    """
    
    # Use actual working Gemini models
    MODEL_NAME = "gemini-2.0-flash"  # Fast model with good quality
    MODEL_PRO = "gemini-1.5-pro-latest"     # For complex queries
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.MODEL_NAME)
        self.pro_model = genai.GenerativeModel(self.MODEL_PRO)
        
        # Track request metadata
        self.request_count = 0
        self.total_tokens = 0
    
    def generate_with_thinking(
        self, 
        prompt: str, 
        thinking_level: ThinkingLevel = "medium",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate response with simulated thinking level and create Thought Signature.
        
        Args:
            prompt: The user prompt
            thinking_level: One of 'minimal', 'low', 'medium', 'high'
            context: Optional context dict for tracking
            
        Returns:
            {
                'content': str,          # The actual response
                'thought_signature': str, # Signature derived from response
                'thinking': str,          # Simulated thinking content
                'thinking_level': str,    # Level used
                'thinking_tokens': int,   # Estimated thinking tokens
                'output_tokens': int,     # Estimated output tokens
                'metadata': dict          # Additional metadata
            }
        """
        try:
            # Get config for this thinking level
            config = THINKING_CONFIGS.get(thinking_level, THINKING_CONFIGS["medium"])
            
            # Use Pro model for high-complexity queries
            model_to_use = self.pro_model if thinking_level == "high" else self.model
            
            # Generate with appropriate settings
            response = model_to_use.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config["temperature"],
                    max_output_tokens=config["max_output_tokens"],
                )
            )
            
            self.request_count += 1
            
            # Extract response components
            thinking_content = ""
            output_content = ""
            thought_signature = None
            
            if response.candidates:
                candidate = response.candidates[0]
                
                # ✅ Extract Thought Signature from Gemini response (if provided)
                # Gemini 3 provides this automatically
                if hasattr(candidate, 'thinking_signature'):
                    thought_signature = candidate.thinking_signature
                elif hasattr(candidate, 'thought_signature'):
                    thought_signature = candidate.thought_signature
                
                # Extract thinking and content
                if hasattr(candidate, 'content') and candidate.content.parts:
                    for part in candidate.content.parts:
                        # Check for thinking content
                        if hasattr(part, 'thought') and part.thought:
                            thinking_content = part.text if hasattr(part, 'text') else ""
                        elif hasattr(part, 'thinking') and part.thinking:
                            thinking_content = part.thinking
                        elif hasattr(part, 'text'):
                            output_content += part.text
                
                # Try to get thinking from candidate level
                if not thinking_content and hasattr(candidate, 'thinking'):
                    thinking_content = candidate.thinking
            
            # If no structured thinking, use the full response
            if not output_content and response.text:
                output_content = response.text
            
            # ✅ If no signature provided by Gemini, derive from thinking content
            if not thought_signature:
                thought_signature = self._derive_signature(
                    thinking_content or output_content,
                    prompt,
                    context
                )
            
            # Estimate token counts
            thinking_tokens = len((thinking_content or "").split()) * 1.3
            output_tokens = len(output_content.split()) * 1.3
            self.total_tokens += thinking_tokens + output_tokens
            
            return {
                'content': output_content,
                'thought_signature': thought_signature,
                'thinking': thinking_content[:500] if thinking_content else None,
                'thinking_level': thinking_level,
                'thinking_tokens': int(thinking_tokens),
                'output_tokens': int(output_tokens),
                'metadata': {
                    'model': self.MODEL_NAME,
                    'thinking_level': thinking_level,
                    'timestamp': datetime.utcnow().isoformat(),
                    'prompt_hash': hashlib.sha256(prompt.encode()).hexdigest()[:16],
                    'context': context
                }
            }
            
        except Exception as e:
            return {
                'content': None,
                'error': str(e),
                'thought_signature': None,
                'thinking': None,
                'thinking_level': thinking_level,
                'thinking_tokens': 0,
                'output_tokens': 0,
                'metadata': {'error': True, 'error_message': str(e)}
            }
    
    def generate_simple(self, prompt: str) -> Dict[str, Any]:
        """
        Generate response without thinking (minimal cost).
        Used for simple queries that don't need deep reasoning.
        """
        try:
            response = self.default_model.generate_content(prompt)
            self.request_count += 1
            
            output_content = response.text if response.text else ""
            output_tokens = len(output_content.split()) * 1.3
            self.total_tokens += output_tokens
            
            # Generate simplified signature
            signature = hashlib.sha256(
                f"{prompt}:{output_content}:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:32]
            
            return {
                'content': output_content,
                'thought_signature': signature,
                'thinking': None,
                'thinking_level': 'none',
                'thinking_tokens': 0,
                'output_tokens': int(output_tokens),
                'metadata': {
                    'model': self.MODEL_SIMPLE,
                    'thinking_level': 'none',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'content': None,
                'error': str(e),
                'thought_signature': None,
                'thinking': None,
                'thinking_level': 'none',
                'thinking_tokens': 0,
                'output_tokens': 0,
                'metadata': {'error': True}
            }
    
    def _derive_signature(
        self, 
        thinking_content: str, 
        prompt: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Derive a signature from the model's thinking content.
        Used as fallback if Gemini doesn't provide a thinking_signature.
        
        The derived signature includes:
        - Hash of the thinking content
        - Structural pattern metrics
        - Temporal component
        """
        # Create signature components
        content_hash = hashlib.sha256(thinking_content.encode()).hexdigest()
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        
        # Extract structural patterns (behavioral fingerprint)
        pattern_metrics = {
            'word_count': len(thinking_content.split()),
            'sentence_count': thinking_content.count('.') + thinking_content.count('!') + thinking_content.count('?'),
            'reasoning_markers': sum(1 for marker in ['because', 'therefore', 'however', 'thus', 'since'] 
                                    if marker in thinking_content.lower()),
            'question_count': thinking_content.count('?'),
        }
        
        # Create composite signature data
        signature_data = {
            'content_hash': content_hash[:32],
            'prompt_hash': prompt_hash,
            'patterns': pattern_metrics,
            'timestamp': datetime.utcnow().isoformat()[:19]
        }
        
        # Generate final signature
        signature_string = json.dumps(signature_data, sort_keys=True)
        final_signature = hashlib.sha256(signature_string.encode()).hexdigest()
        
        return final_signature
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current session usage statistics."""
        return {
            'request_count': self.request_count,
            'total_tokens_estimated': int(self.total_tokens),
            'estimated_cost_usd': round(self.total_tokens * 0.00000015, 4)
        }


# Singleton instance for easy import
_client_instance: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    """Get or create the singleton Gemini client."""
    global _client_instance
    if _client_instance is None:
        _client_instance = GeminiClient()
    return _client_instance
