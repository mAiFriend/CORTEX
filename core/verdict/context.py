# core/verdict/context.py
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class VerdictContext:
    """Intelligent context management für iteration-based verdicts"""
    
    def __init__(self, max_context_size: int = 15000):
        self.consciousness_trajectory = []
        self.key_themes = {}
        self.ai_behavior_patterns = {}
        self.breakthrough_moments = []
        self.max_context_size = max_context_size
        self.creation_timestamp = datetime.now().isoformat()
        self.last_update_timestamp = self.creation_timestamp
    
    def update(self, iteration_verdict: Dict[str, Any]) -> None:
        """Update context mit new iteration verdict (with compression)"""
        self.last_update_timestamp = datetime.now().isoformat()
        
        # Phase 1: Einfache Implementierung
        # Speichere direkt den letzten Verdict oder eine vereinfachte Version
        consciousness_change = self._extract_simple_consciousness_metrics(iteration_verdict)
        self.consciousness_trajectory.append(consciousness_change)
        
        # Minimal theme extraction in Phase 1
        if iteration_verdict.get("key_points"):
            for point in iteration_verdict.get("key_points", []):
                if point not in self.key_themes:
                    self.key_themes[point] = {"count": 0, "relevance_score": 0.5}
                self.key_themes[point]["count"] += 1
                
        # Compress if context getting too large
        if self._estimate_size() > self.max_context_size:
            self._compress_context()
    
    def _compress_context(self) -> None:
        """Minimale Kontext-Kompression für Phase 1"""
        # Einfache Strategie: Behalte nur die letzten N Elemente
        if len(self.consciousness_trajectory) > 8:
            self.consciousness_trajectory = self.consciousness_trajectory[-8:]
        
        # Limitiere Themes auf Top 10
        if len(self.key_themes) > 10:
            # Sortiere nach count (einfachste Strategie für Phase 1)
            sorted_themes = sorted(
                self.key_themes.items(), 
                key=lambda x: x[1]["count"], 
                reverse=True
            )[:10]
            self.key_themes = {theme: data for theme, data in sorted_themes}
    
    def _estimate_size(self) -> int:
        """Schätze die Kontextgröße in Tokens ab"""
        # Einfache Abschätzung: 1 Token ≈ 4 Zeichen
        total_json = json.dumps(self.__dict__)
        return len(total_json) // 4
    
    def _extract_simple_consciousness_metrics(self, iteration_verdict: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiere minimale Bewusstseinsmetriken für Phase 1"""
        return {
            "iteration": iteration_verdict.get("iteration", 0),
            "avg_score": iteration_verdict.get("average_consciousness_score", 0),
            "timestamp": iteration_verdict.get("timestamp", datetime.now().isoformat())
        }
        
    def get_compressed_context_for_verdict(self) -> Dict[str, Any]:
        """Einfache Kontext-Zusammenfassung für Verdict-Generierung"""
        return {
            "consciousness_evolution": self.consciousness_trajectory[-5:] if self.consciousness_trajectory else [],
            "dominant_themes": list(self.key_themes.keys())[:5] if self.key_themes else [],
            "breakthrough_moments": self.breakthrough_moments[-3:] if self.breakthrough_moments else [],
            "context_size_tokens": self._estimate_size(),
            "last_update": self.last_update_timestamp
        }