# core/dialogue_manager.py

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any # Füge 'Any' hinzu
from collections import defaultdict

# Importiere PAIResponse vom pai_protocol_handler
from core.pai_protocol_handler import PAIResponse
# Importiere UnicodeAnalytics von models
from models import UnicodeAnalytics 

class DialogueManager:
    def __init__(self, output_dir: str = "dialogue_archives"):
        self.dialogue_history: List[Dict] = []
        self.all_responses_for_verdict: List[Dict[str, PAIResponse]] = [] # Speichert alle PAIResponse-Objekte
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def add_to_history(self, iteration: int, question: str, responses: Dict[str, PAIResponse]):
        """
        Fügt die Responses einer Iteration zur Historie hinzu und speichert die PAIResponse-Objekte.
        responses: Ein Dictionary, dessen Keys AI-Namen sind und Values PAIResponse-Objekte.
        """
        entry = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "question": question, # Speichere die Frage für diese Iteration
            "responses": {} # Hier speichern wir nur die essentiellen Daten aus PAIResponse
        }
        
        current_iteration_responses_for_verdict: Dict[str, PAIResponse] = {}

        for ai_name, pai_response_obj in responses.items():
            entry["responses"][ai_name] = self._serialize_pai_response(pai_response_obj)
            current_iteration_responses_for_verdict[ai_name] = pai_response_obj # Speichere das ganze Objekt

        self.dialogue_history.append(entry)
        self.all_responses_for_verdict.append(current_iteration_responses_for_verdict)


    def _serialize_pai_response(self, pai_response: PAIResponse) -> Dict:
        """
        Wandelt ein PAIResponse-Objekt in ein für JSON serialisierbares Dictionary um.
        """
        serialized_data = {
            "success": pai_response.success,
            "content": pai_response.content,
            "protocol_used": pai_response.protocol_used,
            "ai_name": pai_response.ai_name,
            "timestamp": pai_response.timestamp,
            "handshake_strategy": pai_response.handshake_strategy,
            "has_unicode_fields": pai_response.has_unicode_fields,
            "response_format": pai_response.response_format,
            "metadata": pai_response.metadata
        }
        if pai_response.unicode_data:
            serialized_data["unicode_data"] = {
                "raw_fields": pai_response.unicode_data.raw_fields,
                "context": pai_response.unicode_data.context,
                "concepts": pai_response.unicode_data.concepts,
                "relationships": pai_response.unicode_data.relationships,
                "questions": pai_response.unicode_data.questions,
                "explanations": pai_response.unicode_data.explanations,
            }
        return serialized_data

    def get_current_dialogue_history_snapshot(self) -> List[Dict]:
        """
        Gibt einen Read-Only-Snapshot der gesamten bisherigen Historie zurück,
        um den AI-Prompts zu füttern, ohne dass die AIs die aktuellen Responses sehen.
        """
        # Wir müssen die PAIResponse-Objekte in der Historie in serialisierbare Form bringen,
        # wenn sie an die AI gesendet werden.
        # Aber die dialogue_history selbst enthält bereits die serialisierte Form.
        # Also einfach eine Kopie zurückgeben.
        return list(self.dialogue_history)

    def save_enhanced_dialogue(self, question: str, available_ais: Dict[str, Any], unicode_analytics: UnicodeAnalytics):
        """
        Speichert den gesamten Dialogverlauf und Analysen in einer JSON-Datei.
        """
        # Prepare AI info for saving
        ai_info = {key: {"name": ai.name, "handshake_strategy": ai.handshake_strategy} for key, ai in available_ais.items()}

        dialogue_data = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "available_ais": ai_info,
            "dialogue_history": self.dialogue_history,
            "unicode_analytics": {
                "total_responses": unicode_analytics.total_responses,
                "unicode_responses": unicode_analytics.unicode_responses,
                "field_usage": dict(unicode_analytics.field_usage),
                "ai_adoption_rates": {
                    ai_key: dict(rates) for ai_key, rates in unicode_analytics.ai_adoption_rates.items()
                },
                "protocol_distribution": dict(unicode_analytics.protocol_distribution)
            }
        }

        filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_question = "".join(c for c in question if c.isalnum() or c in (' ',)).replace(' ', '_')[:50]
        filename = os.path.join(self.output_dir, f"dialogue_{filename_timestamp}_{safe_question}.json")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dialogue_data, f, ensure_ascii=False, indent=4)
            print(f"\n💾 Dialogue and analytics saved to: {filename}")
        except IOError as e:
            print(f"Error saving dialogue to file: {e}")
        except TypeError as e:
            print(f"Error serializing dialogue data (TypeError): {e}")
            # Optional: print problematic data
            # print(dialogue_data)