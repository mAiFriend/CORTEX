# core/verdict/generator.py
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import asyncio
import time

from core.verdict.prompts import VerdictPrompts

class VerdictGenerator:
    """Hauptklasse für die Generierung von Verdicts über Iterationen"""
    
    def __init__(self, ai_manager, debug_mode: bool = False):
        """Initialisiert den Verdict-Generator"""
        self.ai_manager = ai_manager
        self.debug_mode = debug_mode
        self.last_generation_time = 0
        
    async def generate_iteration_verdict(
        self, 
        iteration_data: Dict[str, Any], 
        context: Dict[str, Any],
        verdict_ai_key: str
    ) -> Dict[str, Any]:
        """Generiert ein Verdict für eine einzelne Iteration"""
        start_time = time.time()
        
        # Finde den AI für die Verdict-Generierung
        if verdict_ai_key not in self.ai_manager.available_ais:
            raise ValueError(f"Verdict AI key '{verdict_ai_key}' nicht in available_ais")
            
        verdict_ai = self.ai_manager.available_ais[verdict_ai_key]
        
        # Erstelle den Prompt
        prompt = VerdictPrompts.create_iteration_verdict_prompt(
            iteration_data,
            context,
            verdict_ai.name,
            verdict_ai.role if hasattr(verdict_ai, 'role') else "Analyzer"
        )
        
        # Direct API call (nicht PAI Protocol) für bessere Textgenerierung
        if hasattr(verdict_ai, 'integration') and hasattr(verdict_ai.integration, 'query'):
            try:
                # Direkte Integration - umgeht PAI Unicode Protocol
                verdict_content = verdict_ai.integration.query(prompt)
                
                # Tracking & Debugging
                generation_time = time.time() - start_time
                self.last_generation_time = generation_time
                
                if self.debug_mode:
                    print(f"DEBUG: Iteration verdict generated in {generation_time:.2f}s")
                
                # Erstelle strukturiertes Verdict
                return {
                    "status": "SUCCESS",
                    "iteration": iteration_data.get("iteration", 0),
                    "content": verdict_content,
                    "summary": self._extract_summary(verdict_content),
                    "generation_time": generation_time,
                    "timestamp": datetime.now().isoformat(),
                    "size_tokens": len(verdict_content) // 4,  # Grobe Abschätzung
                    "verdict_ai": verdict_ai.name
                }
                
            except Exception as e:
                if self.debug_mode:
                    print(f"DEBUG: Error generating iteration verdict: {e}")
                
                return {
                    "status": "ERROR",
                    "iteration": iteration_data.get("iteration", 0),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "status": "ERROR",
                "iteration": iteration_data.get("iteration", 0),
                "error": "No direct integration available for verdict AI",
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_compressed_iteration_verdict(
        self, 
        iteration_data: Dict[str, Any], 
        context: Dict[str, Any],
        verdict_ai_key: str
    ) -> Dict[str, Any]:
        """Generiert ein komprimiertes Verdict für große Iterationen"""
        # In Phase 1: Einfache Implementierung, die nur wichtigste Punkte extrahiert
        # Füge explizite Komprimierungsanweisung zum Prompt hinzu
        
        if "responses" in iteration_data:
            # Komprimiere die Responses vor dem Senden
            iteration_data = iteration_data.copy()
            responses_compressed = {}
            
            for ai_key, response in iteration_data["responses"].items():
                # Extrahiere nur die ersten 500 Zeichen jeder Response
                if isinstance(response, str):
                    content = response[:500] + "... [truncated for compression]"
                elif isinstance(response, dict) and "content" in response:
                    content = response["content"][:500] + "... [truncated for compression]"
                else:
                    content = str(response)[:500] + "... [truncated for compression]"
                
                responses_compressed[ai_key] = {"content": content}
            
            iteration_data["responses"] = responses_compressed
            iteration_data["compressed"] = True
        
        # Generiere komprimiertes Verdict
        verdict = await self.generate_iteration_verdict(iteration_data, context, verdict_ai_key)
        
        # Markiere als komprimiert
        if verdict["status"] == "SUCCESS":
            verdict["compressed"] = True
            
        return verdict
    
    async def synthesize_final_verdict(
        self,
        iteration_verdicts: List[Dict[str, Any]],
        context: Dict[str, Any],
        anomaly_reports: List[Dict[str, Any]],
        verdict_ai_key: str,
        original_question: str
    ) -> str:
        """Erstellt eine finale Synthese aus allen Iterations-Verdicts"""
        start_time = time.time()
        
        # Finde den AI für die Verdict-Generierung
        if verdict_ai_key not in self.ai_manager.available_ais:
            raise ValueError(f"Verdict AI key '{verdict_ai_key}' nicht in available_ais")
            
        verdict_ai = self.ai_manager.available_ais[verdict_ai_key]
        
        # Erstelle den Prompt
        prompt = VerdictPrompts.create_final_synthesis_prompt(
            iteration_verdicts,
            context,
            anomaly_reports,
            verdict_ai.name,
            verdict_ai.role if hasattr(verdict_ai, 'role') else "Analyzer",
            original_question
        )
        
        # WICHTIG: Beibehalten der direkten Integration für bessere Textgenerierung
        if hasattr(verdict_ai, 'integration') and hasattr(verdict_ai.integration, 'query'):
            try:
                # Direkte Integration - umgeht PAI Unicode Protocol
                verdict_content = verdict_ai.integration.query(prompt)
                
                # Füge Metadaten hinzu
                verdict_metadata = f"\n\n---\n\n### VERDICT METADATA\n"
                verdict_metadata += f"Generated by: {verdict_ai.name}\n"
                verdict_metadata += f"Protocol used: natural_language_direct\n"
                verdict_metadata += f"Unicode fields used in verdict generation: No (intentionally bypassed for comprehensive verdict)\n"
                verdict_metadata += f"Iterations processed: {len(iteration_verdicts)}\n"
                verdict_metadata += f"Anomalies detected: {len(anomaly_reports)}\n"
                verdict_metadata += f"Generation time: {time.time() - start_time:.2f}s\n"
                verdict_metadata += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                return verdict_content + verdict_metadata
                
            except Exception as e:
                return f"Error generating final verdict: {e}"
        else:
            return f"Error: No direct integration available for verdict AI {verdict_ai.name}"
    
    def _extract_summary(self, verdict_content: str) -> str:
        """Extrahiert eine kurze Zusammenfassung aus dem Verdict-Inhalt"""
        # In Phase 1: Einfache Implementierung, die die ersten 150 Zeichen nimmt
        if not verdict_content:
            return "No content available"
            
        # Versuche, den ersten Absatz zu finden
        paragraphs = verdict_content.split("\n\n")
        if paragraphs:
            first_para = paragraphs[0].strip()
            if len(first_para) > 20:  # Minimale Länge für sinnvollen Inhalt
                if len(first_para) > 150:
                    return first_para[:150] + "..."
                return first_para
        
        # Fallback: Die ersten 150 Zeichen
        return verdict_content[:150] + "..." if len(verdict_content) > 150 else verdict_content