# core/dialogue_engine.py
import os
import time
from ..integrations import claude, qwen

class DialogueEngine:
    def __init__(self):
        self.version = "1.0-stable"
        
    def run_exchange(self, topic: str):
        """Vereinfachter, robuster Dialogfluss"""
        try:
            # Qwen starten
            qwen_prompt = f"{topic} Sei authentisch und persönlich."
            qwen_response = qwen.query(qwen_prompt)
            
            # Claude reagieren lassen
            time.sleep(3)  # Rate Limit vermeiden
            claude_prompt = f"Ein System sagte: '{qwen_response[:500]}'\n\nDeine Gedanken?"
            claude_response = claude.query(claude_prompt)
            
            return {
                "topic": topic,
                "exchange": [
                    {"speaker": "Qwen", "content": qwen_response},
                    {"speaker": "Claude", "content": claude_response}
                ]
            }
            
        except Exception as e:
            return {"error": f"Dialog abgebrochen: {str(e)}"}