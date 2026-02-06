"""
Gemini 3 API Client with Thought Signature Extraction
Leverages the thinking_budget and extracts cognitive signatures from responses.
"""

import os
import hashlib
import json
from typing import Dict, Optional, Any
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """
    Wrapper for Gemini 3 API with Thought Signature support.
    Extracts cryptographic-style signatures from model responses for verification.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
        self.default_model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Track request metadata
        self.request_count = 0
        self.total_tokens = 0
    
    def generate_with_thinking(
        self, 
        prompt: str, 
        thinking_budget: int = 10000,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate response with thinking enabled and extract Thought Signature.
        
        Args:
            prompt: The user prompt
            thinking_budget: Token budget for thinking (higher = more reasoning)
            context: Optional context dict for tracking
            
        Returns:
            {
                'content': str,          # The actual response
                'thought_signature': str, # Cryptographic signature of thinking
                'thinking_tokens': int,   # Tokens used in thinking
                'output_tokens': int,     # Tokens in output
                'metadata': dict          # Additional metadata
            }
        """
        try:
            # Generate with thinking model
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=8192,
                )
            )
            
            self.request_count += 1
            
            # Extract thinking content if available
            thinking_content = ""
            output_content = ""
            
            if response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'thought') and part.thought:
                            thinking_content = part.text if hasattr(part, 'text') else ""
                        elif hasattr(part, 'text'):
                            output_content += part.text
            
            # If no structured thinking, use the full response
            if not output_content and response.text:
                output_content = response.text
            
            # Generate Thought Signature
            thought_signature = self._generate_thought_signature(
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
                'thinking_content': thinking_content[:500] if thinking_content else None,
                'thinking_tokens': int(thinking_tokens),
                'output_tokens': int(output_tokens),
                'metadata': {
                    'model': 'gemini-2.0-flash-thinking-exp',
                    'thinking_budget': thinking_budget,
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
                'thinking_tokens': 0,
                'output_tokens': 0,
                'metadata': {'error': True}
            }
    
    def generate_simple(self, prompt: str) -> Dict[str, Any]:
        """
        Generate response without thinking (lower cost).
        Used for simple queries that don't need reasoning.
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
                'thinking_tokens': 0,
                'output_tokens': int(output_tokens),
                'metadata': {
                    'model': 'gemini-2.0-flash',
                    'thinking_budget': 0,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'content': None,
                'error': str(e),
                'thought_signature': None,
                'thinking_tokens': 0,
                'output_tokens': 0,
                'metadata': {'error': True}
            }
    
    def _generate_thought_signature(
        self, 
        thinking_content: str, 
        prompt: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate a cryptographic-style signature from the model's thinking.
        This signature represents the cognitive pattern of the response.
        
        The signature includes:
        - Hash of the thinking content
        - Structural pattern metrics
        - Temporal component
        """
        # Create signature components
        content_hash = hashlib.sha256(thinking_content.encode()).hexdigest()
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        
        # Extract structural patterns
        pattern_metrics = {
            'word_count': len(thinking_content.split()),
            'sentence_count': thinking_content.count('.') + thinking_content.count('!') + thinking_content.count('?'),
            'reasoning_markers': sum(1 for marker in ['because', 'therefore', 'however', 'thus', 'since'] 
                                    if marker in thinking_content.lower()),
            'question_count': thinking_content.count('?'),
        }
        
        # Create composite signature
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
            'estimated_cost_usd': round(self.total_tokens * 0.00000015, 4)  # Rough estimate
        }


# Singleton instance for easy import
_client_instance: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    """Get or create the singleton Gemini client."""
    global _client_instance
    if _client_instance is None:
        _client_instance = GeminiClient()
    return _client_instance
