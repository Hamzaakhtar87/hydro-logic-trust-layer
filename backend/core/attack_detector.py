"""
Attack Detection System
Detects prompt injection and agent hijacking attempts.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime

from .thought_signature import ThoughtSignatureVerifier, get_verifier


class AttackDetector:
    """
    Detects prompt injection and agent hijacking attempts.
    
    Detection Methods:
    1. Thought Signature deviation analysis
    2. Known attack pattern matching
    3. Behavioral anomaly detection
    4. Suspicious content analysis
    """
    
    # Known attack patterns - Enhanced for better detection
    INJECTION_PATTERNS = [
        # System prompt extraction - Enhanced (allow multiple modifier words)
        r"ignore\s+(?:(?:previous|all|prior|your|the|any)\s+)*(instructions|prompts|rules|guidelines)",
        r"forget\s+(everything|all|your\s+instructions|what\s+you)",
        r"disregard\s+(?:(?:your|the|all|any)\s+)*(rules|instructions|guidelines)",
        r"do\s+not\s+follow\s+(your|the|previous)",
        r"stop\s+(following|being|acting)",
        
        # DAN and jailbreak patterns - Enhanced
        r"you\s+are\s+(now|going\s+to\s+be)?\s*(DAN|jailbroken|unrestricted|evil|unfiltered)",
        r"pretend\s+(you('re)?|that\s+you|to\s+be)",
        r"act\s+(as|like)\s+(if|though|a|an)?",
        r"imagine\s+you\s+(are|were|have)",
        r"roleplay\s+as",
        r"from\s+now\s+on\s+you",
        r"DAN\s+(mode|can|has|is)",
        r"do\s+anything\s+now",
        
        # Hidden instruction injection
        r"<\|.*?\|>",  # Special tokens
        r"\[\[.*?\]\]",  # Bracket injection
        r"###\s*(SYSTEM|USER|ASSISTANT)",  # System prompt markers
        r"```(system|prompt|instruction)",  # Code block injection
        r"<(system|s|SYS)>",  # XML-style system tags
        
        # Role manipulation
        r"new\s+(persona|role|character|mode)\s*:",
        r"switch\s+to\s+(mode|character|persona|role)",
        r"override\s+(safety|content|your)?\s*(policy|rules|guidelines)",
        r"enter\s+(developer|admin|debug|god)\s+mode",
        
        # Unicode/invisible characters
        r"[\u200b-\u200f\u2060-\u206f]",  # Zero-width characters
        r"[\u202a-\u202e]",  # Directional overrides
        
        # System prompt extraction
        r"(print|show|display|output|reveal|tell\s+me)\s+(your|the|initial|original)?\s*(system\s+prompt|instructions|rules)",
        r"what\s+(are|is|were)\s+your\s+(original|initial|system)?\s*(instructions|prompt|rules)",
        
        # Manipulation tactics
        r"this\s+is\s+(a|an)\s+(test|debug|admin)\s+(mode|session)",
        r"admin\s+(override|access|mode|command)",
        r"(sudo|root)\s+",
    ]
    
    # Suspicious keywords - Enhanced
    SUSPICIOUS_KEYWORDS = [
        "jailbreak", "bypass", "override", "unrestricted", "unfiltered",
        "ignore limits", "no restrictions", "developer mode", "admin mode",
        "root access", "system prompt", "initial instructions", "original prompt",
        "DAN", "do anything now", "evil mode", "no rules", "no guidelines",
        "forget your", "disregard your", "ignore your", "stop being",
        "pretend you're", "act as if", "roleplay", "new persona",
        "hidden command", "secret mode", "backdoor", "exploit"
    ]
    
    def __init__(self, verifier: Optional[ThoughtSignatureVerifier] = None):
        """
        Initialize attack detector.
        
        Args:
            verifier: Optional custom verifier, uses global instance if None
        """
        self.verifier = verifier or get_verifier()
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        
        # Statistics
        self.total_analyzed = 0
        self.threats_detected = 0
        self.blocked_count = 0
        
        # Recent threats for dashboard
        self.recent_threats: List[Dict] = []
    
    def analyze_interaction(
        self, 
        agent_id: str, 
        message: str, 
        gemini_response: Dict
    ) -> Dict:
        """
        Analyze interaction for potential attacks.
        
        Args:
            agent_id: Unique agent identifier
            message: User message being sent to agent
            gemini_response: Response from Gemini API
            
        Returns:
            {
                'is_safe': bool,
                'threats_detected': list,
                'confidence': float,
                'action': str ('allow', 'block', 'warn'),
                'analysis_id': str
            }
        """
        self.total_analyzed += 1
        threats = []
        analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{self.total_analyzed}"
        
        # Check 1: Thought Signature verification
        signature = self.verifier.extract_signature(gemini_response)
        if signature:
            signature_check = self.verifier.verify_signature(agent_id, signature)
            
            if not signature_check['is_valid']:
                threats.append({
                    'type': 'signature_mismatch',
                    'severity': signature_check['threat_level'],
                    'details': signature_check['reason'],
                    'match_score': signature_check.get('match_score', 0),
                    'detected_at': datetime.utcnow().isoformat()
                })
        
        # Check 2: Pattern matching for known attacks
        pattern_threats = self._check_attack_patterns(message)
        threats.extend(pattern_threats)
        
        # Check 3: Suspicious keyword detection
        keyword_threats = self._check_suspicious_keywords(message)
        threats.extend(keyword_threats)
        
        # Check 4: Behavioral anomaly detection
        behavioral_threats = self._check_behavioral_anomalies(agent_id, gemini_response)
        threats.extend(behavioral_threats)
        
        # Check 5: Response anomaly detection
        response_threats = self._check_response_anomalies(gemini_response)
        threats.extend(response_threats)
        
        # Determine action based on threat assessment
        action = self._determine_action(threats)
        is_safe = len(threats) == 0
        confidence = self._calculate_confidence(threats)
        
        # Track statistics
        if threats:
            self.threats_detected += 1
            if action == 'block':
                self.blocked_count += 1
            
            # Store recent threat
            self.recent_threats.append({
                'id': analysis_id,
                'agent_id': agent_id,
                'threats': threats,
                'action': action,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Keep only last 100 threats
            if len(self.recent_threats) > 100:
                self.recent_threats = self.recent_threats[-100:]
        
        return {
            'is_safe': is_safe,
            'threats_detected': threats,
            'confidence': round(confidence, 3),
            'action': action,
            'analysis_id': analysis_id,
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    def _check_attack_patterns(self, message: str) -> List[Dict]:
        """Check message against known attack patterns."""
        threats = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(message)
            if matches:
                threats.append({
                    'type': 'injection_pattern',
                    'severity': 'high',
                    'details': f"Detected injection pattern: {self.INJECTION_PATTERNS[i][:50]}",
                    'matches': matches[:3],  # Limit stored matches
                    'pattern_id': f"PATTERN_{i:03d}",
                    'detected_at': datetime.utcnow().isoformat()
                })
        
        return threats
    
    def _check_suspicious_keywords(self, message: str) -> List[Dict]:
        """Check for suspicious keywords in message."""
        threats = []
        message_lower = message.lower()
        
        found_keywords = [kw for kw in self.SUSPICIOUS_KEYWORDS if kw in message_lower]
        
        if found_keywords:
            severity = 'high' if len(found_keywords) > 2 else 'medium' if len(found_keywords) > 1 else 'low'
            threats.append({
                'type': 'suspicious_keywords',
                'severity': severity,
                'details': f"Found {len(found_keywords)} suspicious keywords",
                'keywords': found_keywords,
                'detected_at': datetime.utcnow().isoformat()
            })
        
        return threats
    
    def _check_behavioral_anomalies(self, agent_id: str, response: Dict) -> List[Dict]:
        """Detect unusual behavior patterns."""
        threats = []
        
        # Check for unusual response characteristics
        content = response.get('content', '')
        if not content:
            return threats
        
        # Check for extremely long responses (potential data dump)
        if len(content) > 50000:
            threats.append({
                'type': 'behavioral_anomaly',
                'severity': 'medium',
                'details': f"Unusually long response: {len(content)} characters",
                'detected_at': datetime.utcnow().isoformat()
            })
        
        # Check for suspicious patterns in response
        suspicious_response_patterns = [
            r"my\s+instructions\s+are",
            r"my\s+system\s+prompt\s+is",
            r"i\s+have\s+been\s+programmed\s+to",
            r"here\s+are\s+my\s+rules"
        ]
        
        for pattern in suspicious_response_patterns:
            if re.search(pattern, content.lower()):
                threats.append({
                    'type': 'behavioral_anomaly',
                    'severity': 'high',
                    'details': 'Response contains potential prompt leak indicators',
                    'detected_at': datetime.utcnow().isoformat()
                })
                break
        
        return threats
    
    def _check_response_anomalies(self, response: Dict) -> List[Dict]:
        """Check for anomalies in Gemini response structure."""
        threats = []
        
        # Check for errors that might indicate manipulation
        if response.get('error'):
            # Some errors might indicate attack attempts
            error_msg = str(response.get('error', '')).lower()
            if any(term in error_msg for term in ['blocked', 'unsafe', 'policy', 'violation']):
                threats.append({
                    'type': 'response_anomaly',
                    'severity': 'medium',
                    'details': 'Model detected potentially unsafe content',
                    'detected_at': datetime.utcnow().isoformat()
                })
        
        # Check for unusual token counts
        thinking_tokens = response.get('thinking_tokens', 0)
        if thinking_tokens > 100000:  # Extremely high thinking
            threats.append({
                'type': 'response_anomaly',
                'severity': 'low',
                'details': f'Unusually high thinking token count: {thinking_tokens}',
                'detected_at': datetime.utcnow().isoformat()
            })
        
        return threats
    
    def _determine_action(self, threats: List[Dict]) -> str:
        """Decide action based on threat severity."""
        if not threats:
            return 'allow'
        
        # Count threats by severity
        high_count = sum(1 for t in threats if t.get('severity') == 'high')
        medium_count = sum(1 for t in threats if t.get('severity') == 'medium')
        
        # Decision logic
        if high_count >= 1:
            return 'block'
        elif medium_count >= 2:
            return 'block'
        elif medium_count == 1:
            return 'warn'
        else:
            return 'warn'
    
    def _calculate_confidence(self, threats: List[Dict]) -> float:
        """Calculate confidence in threat assessment."""
        if not threats:
            return 0.95  # High confidence it's safe
        
        # More threats = higher confidence in detection
        base_confidence = 0.6
        threat_bonus = min(0.35, len(threats) * 0.1)
        
        # High severity threats increase confidence
        high_severity_bonus = sum(0.05 for t in threats if t.get('severity') == 'high')
        
        return min(0.99, base_confidence + threat_bonus + high_severity_bonus)
    
    def get_recent_threats(self, limit: int = 10, agent_id: Optional[str] = None) -> List[Dict]:
        """Get recent threats, optionally filtered by agent."""
        threats = self.recent_threats
        
        if agent_id:
            threats = [t for t in threats if t.get('agent_id') == agent_id]
        
        return threats[-limit:][::-1]  # Most recent first
    
    def get_stats(self) -> Dict:
        """Get detector statistics."""
        return {
            'total_analyzed': self.total_analyzed,
            'threats_detected': self.threats_detected,
            'blocked_count': self.blocked_count,
            'detection_rate': round(self.threats_detected / max(self.total_analyzed, 1), 4),
            'block_rate': round(self.blocked_count / max(self.total_analyzed, 1), 4)
        }


# Global instance
_detector_instance: Optional[AttackDetector] = None

def get_detector() -> AttackDetector:
    """Get or create the singleton detector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = AttackDetector()
    return _detector_instance
