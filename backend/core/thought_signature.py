"""
Thought Signature Verification System
Detects agent hijacking by comparing behavioral signatures.
"""

import hashlib
import json
from typing import Dict, Optional, List
from datetime import datetime
from collections import deque


class ThoughtSignatureVerifier:
    """
    Verifies Gemini 3 Thought Signatures to detect agent hijacking.
    
    Core Concept:
    - Each AI agent develops a consistent "thinking style"
    - This style produces recognizable patterns in responses
    - Sudden changes indicate potential hijacking/injection
    """
    
    def __init__(self, baseline_size: int = 100, deviation_threshold: float = 0.65):
        """
        Initialize verifier.
        
        Args:
            baseline_size: Number of signatures to maintain per agent
            deviation_threshold: Minimum similarity required (0-1)
        """
        self.baseline_signatures: Dict[str, deque] = {}  # agent_id -> deque of signatures
        self.baseline_patterns: Dict[str, Dict] = {}  # agent_id -> pattern statistics
        self.baseline_size = baseline_size
        self.deviation_threshold = deviation_threshold
        
        # Statistics tracking
        self.verification_count = 0
        self.threats_detected = 0
    
    def extract_signature(self, gemini_response: Dict) -> Optional[str]:
        """
        Extract Thought Signature from Gemini API response.
        
        Args:
            gemini_response: Response dict from GeminiClient
            
        Returns:
            Signature string or None if not available
        """
        if not gemini_response:
            return None
        
        # Try direct signature first
        if 'thought_signature' in gemini_response:
            return gemini_response['thought_signature']
        
        # Try to extract from nested structure
        if 'candidates' in gemini_response:
            try:
                candidate = gemini_response['candidates'][0]
                if 'thinking_signature' in candidate:
                    return candidate['thinking_signature']
            except (IndexError, KeyError):
                pass
        
        # Generate from content if available
        if 'content' in gemini_response and gemini_response['content']:
            content = gemini_response['content']
            return self._generate_fallback_signature(content)
        
        return None
    
    def _generate_fallback_signature(self, content: str) -> str:
        """Generate a signature from content when API signature unavailable."""
        # Extract structural features
        features = {
            'length': len(content),
            'word_count': len(content.split()),
            'avg_word_length': sum(len(w) for w in content.split()) / max(len(content.split()), 1),
            'punctuation_ratio': sum(1 for c in content if c in '.,!?;:') / max(len(content), 1),
            'caps_ratio': sum(1 for c in content if c.isupper()) / max(len(content), 1),
            'unique_words': len(set(content.lower().split())),
        }
        
        return hashlib.sha256(json.dumps(features, sort_keys=True).encode()).hexdigest()
    
    def build_baseline(self, agent_id: str, signatures: List[str]) -> Dict:
        """
        Build behavioral baseline from historical signatures.
        
        Args:
            agent_id: Unique agent identifier
            signatures: List of historical signature strings
            
        Returns:
            Baseline statistics
        """
        if agent_id not in self.baseline_signatures:
            self.baseline_signatures[agent_id] = deque(maxlen=self.baseline_size)
        
        # Add signatures to baseline
        for sig in signatures[-self.baseline_size:]:
            self.baseline_signatures[agent_id].append(sig)
        
        # Calculate pattern statistics
        pattern_stats = self._calculate_pattern_stats(agent_id)
        self.baseline_patterns[agent_id] = pattern_stats
        
        return {
            'agent_id': agent_id,
            'baseline_size': len(self.baseline_signatures[agent_id]),
            'patterns': pattern_stats,
            'established_at': datetime.utcnow().isoformat()
        }
    
    def add_to_baseline(self, agent_id: str, signature: str) -> None:
        """Add a single verified signature to an agent's baseline."""
        if agent_id not in self.baseline_signatures:
            self.baseline_signatures[agent_id] = deque(maxlen=self.baseline_size)
        
        self.baseline_signatures[agent_id].append(signature)
        
        # Update pattern stats periodically
        if len(self.baseline_signatures[agent_id]) % 10 == 0:
            self.baseline_patterns[agent_id] = self._calculate_pattern_stats(agent_id)
    
    def verify_signature(self, agent_id: str, new_signature: str) -> Dict:
        """
        Verify if new signature matches agent's baseline.
        
        Args:
            agent_id: Agent to verify against
            new_signature: The new signature to check
            
        Returns:
            {
                'is_valid': bool,
                'confidence': float (0-1),
                'threat_level': str ('none', 'low', 'medium', 'high'),
                'reason': str,
                'match_score': float
            }
        """
        self.verification_count += 1
        
        # Check if baseline exists
        if agent_id not in self.baseline_signatures or len(self.baseline_signatures[agent_id]) < 5:
            # New agent - add to baseline and allow
            self.add_to_baseline(agent_id, new_signature)
            return {
                'is_valid': True,
                'confidence': 0.5,
                'threat_level': 'none',
                'reason': 'New agent - building baseline',
                'match_score': 1.0,
                'baseline_status': 'building'
            }
        
        # Calculate similarity to baseline
        match_score = self._calculate_similarity(new_signature, agent_id)
        
        # Determine validity and threat level
        is_valid = match_score >= self.deviation_threshold
        threat_level = self._assess_threat(match_score)
        
        # Calculate confidence based on baseline size and score
        baseline_size = len(self.baseline_signatures[agent_id])
        confidence = min(0.99, 0.5 + (baseline_size / 200) + (match_score * 0.3))
        
        # Generate reason
        if is_valid:
            reason = f"Signature matches baseline (score: {match_score:.2%})"
        else:
            self.threats_detected += 1
            reason = f"Signature deviation detected (score: {match_score:.2%}, threshold: {self.deviation_threshold:.2%})"
        
        result = {
            'is_valid': is_valid,
            'confidence': round(confidence, 3),
            'threat_level': threat_level,
            'reason': reason,
            'match_score': round(match_score, 4),
            'baseline_size': baseline_size,
            'verified_at': datetime.utcnow().isoformat()
        }
        
        # Add valid signatures to baseline
        if is_valid and threat_level == 'none':
            self.add_to_baseline(agent_id, new_signature)
        
        return result
    
    def _calculate_similarity(self, signature: str, agent_id: str) -> float:
        """
        Calculate similarity between signature and baseline.
        
        Uses multiple comparison methods:
        1. Hash prefix matching (fast)
        2. Character distribution analysis
        3. Structural similarity
        """
        baseline = list(self.baseline_signatures[agent_id])
        
        if not baseline:
            return 1.0
        
        # Method 1: Hash prefix matching
        prefix_scores = []
        for base_sig in baseline[-20:]:  # Compare to recent signatures
            matching_chars = sum(1 for a, b in zip(signature, base_sig) if a == b)
            prefix_scores.append(matching_chars / max(len(signature), len(base_sig)))
        
        avg_prefix_score = sum(prefix_scores) / len(prefix_scores) if prefix_scores else 0
        
        # Method 2: Character frequency analysis
        sig_freq = self._get_char_frequency(signature)
        baseline_freqs = [self._get_char_frequency(s) for s in baseline[-10:]]
        
        freq_similarities = []
        for base_freq in baseline_freqs:
            similarity = self._compare_frequencies(sig_freq, base_freq)
            freq_similarities.append(similarity)
        
        avg_freq_score = sum(freq_similarities) / len(freq_similarities) if freq_similarities else 0
        
        # Method 3: Length-based similarity
        sig_len = len(signature)
        baseline_lengths = [len(s) for s in baseline]
        avg_baseline_len = sum(baseline_lengths) / len(baseline_lengths)
        length_score = 1 - abs(sig_len - avg_baseline_len) / max(sig_len, avg_baseline_len)
        
        # Combined score (weighted)
        combined_score = (
            avg_prefix_score * 0.4 +
            avg_freq_score * 0.4 +
            length_score * 0.2
        )
        
        return max(0, min(1, combined_score))
    
    def _get_char_frequency(self, s: str) -> Dict[str, float]:
        """Get normalized character frequency distribution."""
        freq = {}
        for c in s:
            freq[c] = freq.get(c, 0) + 1
        total = len(s)
        return {k: v / total for k, v in freq.items()}
    
    def _compare_frequencies(self, freq1: Dict, freq2: Dict) -> float:
        """Compare two frequency distributions."""
        all_chars = set(freq1.keys()) | set(freq2.keys())
        if not all_chars:
            return 1.0
        
        diff_sum = sum(abs(freq1.get(c, 0) - freq2.get(c, 0)) for c in all_chars)
        return 1 - (diff_sum / 2)  # Normalize to 0-1
    
    def _assess_threat(self, match_score: float) -> str:
        """Determine threat level based on deviation severity."""
        if match_score >= 0.85:
            return 'none'
        elif match_score >= 0.70:
            return 'low'
        elif match_score >= 0.50:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_pattern_stats(self, agent_id: str) -> Dict:
        """Calculate statistical patterns from baseline signatures."""
        baseline = list(self.baseline_signatures.get(agent_id, []))
        
        if not baseline:
            return {}
        
        lengths = [len(s) for s in baseline]
        
        return {
            'avg_length': sum(lengths) / len(lengths),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'signature_count': len(baseline),
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def get_stats(self) -> Dict:
        """Get verifier statistics."""
        return {
            'agents_tracked': len(self.baseline_signatures),
            'total_verifications': self.verification_count,
            'threats_detected': self.threats_detected,
            'detection_rate': round(self.threats_detected / max(self.verification_count, 1), 4)
        }
    
    def get_agent_baseline_info(self, agent_id: str) -> Optional[Dict]:
        """Get baseline information for a specific agent."""
        if agent_id not in self.baseline_signatures:
            return None
        
        return {
            'agent_id': agent_id,
            'baseline_size': len(self.baseline_signatures[agent_id]),
            'patterns': self.baseline_patterns.get(agent_id, {}),
            'deviation_threshold': self.deviation_threshold
        }


# Global instance
_verifier_instance: Optional[ThoughtSignatureVerifier] = None

def get_verifier() -> ThoughtSignatureVerifier:
    """Get or create the singleton verifier instance."""
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = ThoughtSignatureVerifier()
    return _verifier_instance
