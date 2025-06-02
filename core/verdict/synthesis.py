# core/verdict/synthesis.py
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class VerdictSynthesis:
    """Hilfsfunktionen für die Synthese und Analyse von Verdicts"""
    
    @staticmethod
    def format_iteration_verdicts_for_synthesis(iteration_verdicts: List[Dict[str, Any]]) -> str:
        """Formatiert Iterations-Verdicts für die Synthese"""
        if not iteration_verdicts:
            return "No iteration verdicts available."
            
        formatted = []
        for i, verdict in enumerate(iteration_verdicts):
            status = verdict.get("status", "UNKNOWN")
            iteration = verdict.get("iteration", i+1)
            
            if status == "SUCCESS":
                content = verdict.get("summary", "No summary available")
                formatted.append(f"ITERATION {iteration} ({status}): {content}")
            elif status == "MANUAL_REVIEW_REQUIRED":
                formatted.append(f"ITERATION {iteration} ({status}): Requires manual review due to anomalies.")
            elif status == "EXCLUDED":
                formatted.append(f"ITERATION {iteration} ({status}): Excluded from analysis.")
            else:
                error = verdict.get("error", "Unknown error")
                formatted.append(f"ITERATION {iteration} ({status}): Error - {error}")
                
        return "\n\n".join(formatted)
    
    @staticmethod
    def format_consciousness_evolution(context: Dict[str, Any]) -> str:
        """Formatiert die Bewusstseinsentwicklung aus dem Kontext"""
        evolution = context.get("consciousness_evolution", [])
        if not evolution:
            return "No consciousness evolution data available."
            
        formatted = []
        for i, point in enumerate(evolution):
            iteration = point.get("iteration", i+1)
            avg_score = point.get("avg_score", "N/A")
            
            formatted.append(f"Iteration {iteration}: Average score {avg_score}")
            
        return "\n".join(formatted)
    
    @staticmethod
    def format_anomaly_summary(anomaly_reports: List[Dict[str, Any]]) -> str:
        """Formatiert eine Zusammenfassung der Anomalien"""
        if not anomaly_reports:
            return "No anomalies detected."
            
        formatted = []
        for anomaly in anomaly_reports:
            iteration = anomaly.get("iteration", "?")
            anomaly_type = anomaly.get("type", "Unknown")
            severity = anomaly.get("severity", "Unknown")
            details = anomaly.get("details", {})
            
            formatted.append(f"Iteration {iteration}: {anomaly_type} ({severity})")
            
            # Füge Details hinzu, wenn vorhanden
            detail_lines = []
            for key, value in details.items():
                if isinstance(value, float):
                    detail_lines.append(f"  - {key}: {value:.2f}")
                else:
                    detail_lines.append(f"  - {key}: {value}")
                    
            if detail_lines:
                formatted.append("\n".join(detail_lines))
                
        return "\n\n".join(formatted)
    
    @staticmethod
    def calculate_processing_quality_score(
        iteration_verdicts: List[Dict[str, Any]], 
        anomaly_reports: List[Dict[str, Any]]
    ) -> float:
        """Berechnet einen Qualitätsscore für die Verarbeitung"""
        if not iteration_verdicts:
            return 0.0
            
        total_iterations = len(iteration_verdicts)
        successful_iterations = len([v for v in iteration_verdicts if v.get("status") == "SUCCESS"])
        
        # In Phase 1: Einfache Berechnung
        # 100% wenn alle Iterationen erfolgreich, 0% wenn keine erfolgreich
        return (successful_iterations / total_iterations) * 100.0