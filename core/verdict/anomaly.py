# core/verdict/anomaly.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AnomalyReport:
    """Strukturierte Anomalie-Berichte für transparentes Error-Handling"""
    type: str
    iteration: int
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    details: Dict[str, Any]
    recommendation: str
    auto_handling_options: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere in JSON-serialisierbares Dictionary"""
        return {
            "type": self.type,
            "iteration": self.iteration,
            "severity": self.severity,
            "details": self.details,
            "recommendation": self.recommendation,
            "auto_handling_options": self.auto_handling_options,
            "timestamp": self.timestamp.isoformat()
        }


class VerdictAnomalyDetector:
    """Enterprise-grade Anomalie-Erkennung für AI-Iteration-Processing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisiere Anomalie-Detektor mit konfigurierbaren Baselines"""
        self.baseline_metrics = {
            'typical_response_size': 2000,  # tokens
            'size_deviation_threshold': 3.0,  # 3x Standardabweichung
            'processing_time_limit': 30,  # Sekunden
        }
        
        # Überschreibe defaults mit config wenn vorhanden
        if config:
            self.baseline_metrics.update(config)
            
        # Tracking für zukünftige Optimierungen
        self.iteration_sizes = []
        self.processing_times = []
    
    def detect_iteration_anomalies(self, iteration_data: Dict[str, Any]) -> List[AnomalyReport]:
        """Erkennt Anomalien in einer einzelnen Iteration (Phase 1: nur Größen-Check)"""
        anomalies = []
        
        # Size anomaly detection - KERN DER PHASE 1
        response_size = self._estimate_token_count(iteration_data.get("responses", {}))
        self.iteration_sizes.append(response_size)  # Tracking für spätere Optimierung
        
        size_threshold = self.baseline_metrics['typical_response_size'] * self.baseline_metrics['size_deviation_threshold']
        
        if response_size > size_threshold:
            anomalies.append(AnomalyReport(
                type="OVERSIZED_RESPONSE",
                iteration=iteration_data.get("iteration", 0),
                severity="HIGH" if response_size > size_threshold * 1.5 else "MEDIUM",
                details={
                    "actual_size": response_size,
                    "baseline_size": self.baseline_metrics['typical_response_size'],
                    "deviation_factor": response_size / self.baseline_metrics['typical_response_size'],
                    "threshold": size_threshold
                },
                recommendation="AUTO_COMPRESS" if response_size < size_threshold * 2 else "MANUAL_REVIEW_REQUIRED",
                auto_handling_options=["AUTO_COMPRESS", "EXCLUDE", "MANUAL_REVIEW"]
            ))
        
        return anomalies
    
    def _estimate_token_count(self, responses: Dict[str, Any]) -> int:
        """Schätze die Token-Anzahl für Response-Größenanalyse"""
        if not responses:
            return 0
            
        # In Phase 1: einfache Abschätzung basierend auf der Zeichenanzahl
        # 1 Token ≈ 4 Zeichen ist eine konservative Schätzung
        total_chars = sum(len(str(response)) for response in responses.values())
        return total_chars // 4