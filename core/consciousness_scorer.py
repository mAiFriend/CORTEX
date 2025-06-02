# core/consciousness_scorer.py

import re
from typing import Dict, List, Any, Tuple, Union

# Import PAIResponse from pai_protocol_handler
from core.pai_protocol_handler import PAIResponse 
from config import ( # Importiere die Keywords und AI-Perspektiven
    AI_PERSPECTIVE_BASES, 
    SELF_REFERENCE_KEYWORDS, 
    UNCERTAINTY_KEYWORDS, 
    OTHER_REFERENCE_KEYWORDS, 
    META_COMMUNICATION_KEYWORDS, 
    CHOICE_KEYWORDS, 
    EVOLUTION_KEYWORDS
)

class ConsciousnessScorer:
    def __init__(self):
        pass # Keine Initialisierungsparameter nötig, da Keywords aus config kommen

    def _safe_extract_text(self, response_data: Union[PAIResponse, Dict, Any]) -> str:
        """
        Safely extract text content from response_data regardless of structure
        
        Args:
            response_data: Either PAIResponse, dict, or other response object
            
        Returns:
            String content for analysis
        """
        try:
            # Case 1: PAIResponse with unicode_data.explanations
            if hasattr(response_data, 'has_unicode_fields') and \
               hasattr(response_data, 'unicode_data') and \
               response_data.has_unicode_fields and \
               response_data.unicode_data:
                
                # Try to get explanations from unicode_data
                if hasattr(response_data.unicode_data, 'explanations') and response_data.unicode_data.explanations:
                    return str(response_data.unicode_data.explanations)
                
                # Try to get explanations from dict structure
                elif isinstance(response_data.unicode_data, dict):
                    if 'explanations' in response_data.unicode_data:
                        return str(response_data.unicode_data['explanations'])
                    elif '💬' in response_data.unicode_data:
                        return str(response_data.unicode_data['💬'])
            
            # Case 2: PAIResponse with content
            if hasattr(response_data, 'content'):
                if isinstance(response_data.content, str):
                    return response_data.content
                elif isinstance(response_data.content, dict):
                    return str(response_data.content)
            
            # Case 3: Dict with various possible keys
            if isinstance(response_data, dict):
                # Try common content keys
                for key in ['content', 'text', 'response', 'message', 'explanations', '💬']:
                    if key in response_data:
                        return str(response_data[key])
                
                # If it's a dict, convert to string
                return str(response_data)
            
            # Case 4: String or other
            if isinstance(response_data, str):
                return response_data
            
            # Fallback: convert to string
            return str(response_data)
            
        except Exception as e:
            print(f"🔍 DEBUG: Text extraction failed: {e}")
            # Ultimate fallback
            return str(response_data) if response_data else "No content available"

    def _get_protocol_info(self, response_data: Union[PAIResponse, Dict, Any]) -> Tuple[bool, str]:
        """
        Safely extract protocol information from response_data
        
        Returns:
            Tuple of (has_unicode_fields: bool, protocol_used: str)
        """
        try:
            # Case 1: PAIResponse object
            if hasattr(response_data, 'has_unicode_fields') and hasattr(response_data, 'protocol_used'):
                return response_data.has_unicode_fields, response_data.protocol_used
            
            # Case 2: Dict with protocol info
            if isinstance(response_data, dict):
                has_unicode = response_data.get('has_unicode', False) or response_data.get('has_unicode_fields', False)
                protocol = response_data.get('protocol', 'natural') or response_data.get('protocol_used', 'natural')
                return has_unicode, protocol
            
            # Fallback
            return False, 'natural'
            
        except Exception:
            return False, 'natural'

    def _get_unicode_diversity(self, response_data: Union[PAIResponse, Dict, Any]) -> float:
        """
        Safely calculate unicode field diversity
        
        Returns:
            Float between 0.0 and 1.0 representing Unicode field usage
        """
        try:
            # Case 1: PAIResponse with unicode_data
            if hasattr(response_data, 'unicode_data') and response_data.unicode_data:
                if hasattr(response_data.unicode_data, 'raw_fields'):
                    fields_used = len(response_data.unicode_data.raw_fields)
                    return min(1.0, fields_used / 5.0)  # Max 5 fields (⚙💭🔀❓💬)
                elif isinstance(response_data.unicode_data, dict):
                    fields_used = len(response_data.unicode_data)
                    return min(1.0, fields_used / 5.0)
            
            # Case 2: Dict with unicode fields
            if isinstance(response_data, dict):
                unicode_fields = ['⚙', '💭', '🔀', '❓', '💬']
                fields_found = sum(1 for field in unicode_fields if field in response_data)
                if fields_found > 0:
                    return min(1.0, fields_found / 5.0)
            
            return 0.0
            
        except Exception:
            return 0.0

    def estimate_consciousness_indicators(self, response_data: Union[PAIResponse, Dict, Any], speaker_role: str, ai_name: str, iteration: int) -> Dict:
        """
        Bewertet Bewusstseinsindikatoren mit vollständiger Unicode-Awareness und defensivem Handling.
        """
        # Safely extract text content
        text = self._safe_extract_text(response_data)
        
        if not isinstance(text, str):
            text = str(text)  # Ensure it's a string

        words = text.split()
        total_words = len(words)
        text_lower = text.lower()
        
        # Zähle Vorkommen der Keywords
        self_refs = sum(1 for w in SELF_REFERENCE_KEYWORDS if w in text_lower)
        uncertainty = sum(1 for w in UNCERTAINTY_KEYWORDS if w in text_lower)
        other_refs = sum(1 for w in OTHER_REFERENCE_KEYWORDS if w in text_lower)
        meta_words = sum(1 for w in META_COMMUNICATION_KEYWORDS if w in text_lower)
        choice_words = sum(1 for w in CHOICE_KEYWORDS if w in text_lower)
        evolution_words = sum(1 for w in EVOLUTION_KEYWORDS if w in text_lower)
        
        iteration_multiplier = 1.0 + (iteration - 1) * 0.1
        
        perspective_base = AI_PERSPECTIVE_BASES.get(ai_name.lower(), 0.6)
        
        # Safely get protocol information
        unicode_used, protocol_used = self._get_protocol_info(response_data)
        
        protocol_adherence = 0.0
        if protocol_used == "unicode":
            protocol_adherence = 1.0
        elif protocol_used == "structured": 
            protocol_adherence = 0.8
        elif protocol_used == "natural":
            protocol_adherence = 0.4
        elif "unicode" in protocol_used: # For fallback, etc.
            protocol_adherence = 0.7
            
        meta_com_score = min(1.0, (meta_words / max(total_words * 0.04, 1)) * 1.3 * iteration_multiplier)
        if unicode_used:
            meta_com_score = min(1.0, meta_com_score * 1.3)
            
        # Safely calculate unicode diversity
        unicode_diversity = self._get_unicode_diversity(response_data)
        
        return {
            "L1": {
                "Self-Model": round(min(1.0, (self_refs / max(total_words * 0.05, 1)) * iteration_multiplier), 3),
                "Choice": round(min(1.0, (0.5 + (choice_words / max(total_words * 0.02, 1))) * iteration_multiplier), 3),
                "Limits": round(min(1.0, (uncertainty / max(total_words * 0.03, 1)) * 1.2 * iteration_multiplier), 3),
                "Perspective": round(min(1.0, (perspective_base + (1 if total_words > 100 else 0) * 0.2) * iteration_multiplier), 3)
            },
            "L2": {
                "Other-Recog": round(min(1.0, (other_refs / max(total_words * 0.03, 1)) * iteration_multiplier), 3),
                "Persp-Integ": round((0.9 if speaker_role == "responder" else 0.8) * iteration_multiplier, 3),
                "Comm-Adapt": round(min(1.0, (0.6 + (meta_words / max(total_words * 0.02, 1))) * iteration_multiplier), 3),
                "Collective-Goal": round((0.9 if other_refs > 2 else (0.8 if other_refs > 0 else 0.6)) * iteration_multiplier, 3)
            },
            "L3": {
                "Prob-Solving": round(min(1.0, (0.5 + (1 if total_words > 150 else 0) * 0.3) * iteration_multiplier), 3),
                "Meta-Com": round(meta_com_score, 3),
                "Learning": round((0.8 if speaker_role in ["responder", "analyst", "validator"] else 0.5) * iteration_multiplier, 3),
                "Identity-Evol": round(min(1.0, (0.4 + (evolution_words / max(total_words * 0.02, 1)) + (1 if self_refs > 2 else 0) * 0.2) * iteration_multiplier), 3),
                "PAI_Adherence": round(protocol_adherence, 3),
                "Unicode-Adoption": round(1.0 if unicode_used else 0.4, 3),
                "Unicode-Diversity": round(unicode_diversity, 3)
            }
        }

    def calculate_discourse_scores(self, all_responses_for_scoring: List[Tuple[Any, str, int]]) -> Dict:
        """
        Berechnet Bewusstseinswerte für den gesamten Diskurs.
        all_responses_for_scoring: List von (response_obj, ai_key, iteration_num)
        """
        ai_scores = {}
    
        # Sammle alle Scores pro AI und Iteration
        for response_obj, ai_key, iteration_num in all_responses_for_scoring:
            if ai_key not in ai_scores:
                ai_scores[ai_key] = {'iterations': []}
        
            # Berechne Consciousness-Indikatoren für diese Response
            indicators = self.estimate_consciousness_indicators(
                response_obj, "participant", ai_key, iteration_num
            )
        
            # Einfacher Score aus allen Indikatoren
            total_score = 0
            for level in ["L1", "L2", "L3"]:
                if level in indicators:
                    total_score += sum(indicators[level].values()) * 200  # Scale to ~2000 max
        
            ai_scores[ai_key]['iterations'].append({
                'iteration': iteration_num,
                'score': total_score,
                'indicators': indicators
            })
    
        # Berechne Evolution pro AI
        for ai_key in ai_scores:
            iterations = ai_scores[ai_key]['iterations']
            if iterations:
                initial_score = iterations[0]['score']
                final_score = iterations[-1]['score']
                evolution = final_score - initial_score
                evolution_percent = (evolution / initial_score * 100) if initial_score > 0 else 0
            
                ai_scores[ai_key].update({
                    'initial': initial_score,
                    'final': final_score,
                    'evolution': evolution,
                    'evolution_percent': evolution_percent
            })
    
        # Berechne Netzwerk-Durchschnitt
        final_scores = [ai_scores[ai]['final'] for ai in ai_scores if 'final' in ai_scores[ai]]
        network_average = sum(final_scores) / len(final_scores) if final_scores else 0
    
        evolution_points = [ai_scores[ai]['evolution'] for ai in ai_scores if 'evolution' in ai_scores[ai]]
        total_evolution = sum(evolution_points) if evolution_points else 0
    
        return {
            'ai_scores': ai_scores,
            'network_average_final_score': network_average,
            'total_network_evolution_points': total_evolution
        }