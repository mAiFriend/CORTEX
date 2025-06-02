# core/pai_communicator.py

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field # Notwendig, falls Fallback-Definitionen verwendet werden

from models import AIEngine # Importiere deine AIEngine Dataclass
from config import PAI_UNICODE_PROMPT_INSTRUCTION # Importiere die Prompt-Instruktion
from core.unicode_processor import UnicodeProcessor # Importiere den UnicodeProcessor

# Importiere PAIResponse, UnicodeData und PAI_AVAILABLE von pai_protocol_handler
# Der pai_protocol_handler handhabt die bedingte Definition/Import.
from core.pai_protocol_handler import PAIProtocolHandler, PAI_AVAILABLE, PAIResponse, UnicodeData 

class PAICommunicator:
    def __init__(self, debug_mode: bool, unicode_processor: UnicodeProcessor, pai_protocol_handler: PAIProtocolHandler):
        self.debug_mode = debug_mode
        self.unicode_processor = unicode_processor
        self.pai_protocol_handler = pai_protocol_handler

    async def pai_enhanced_call_ai_api(self, ai_engine: AIEngine, prompt: str) -> PAIResponse:
        """
        Ruft die AI-API auf, entweder über PAI oder mit manuellem Fallback für Unicode-Extraktion.
        ai_engine ist ein AIEngine-Objekt (entählt Modul).
        """
        # Prompt wird immer mit der Unicode-Instruktion angereichert
        enhanced_prompt = PAI_UNICODE_PROMPT_INSTRUCTION + prompt

        async def ai_caller_wrapper(message: str) -> str:  # Remove context parameter!
            """Wrapper-Funktion zum Aufruf der AI-Integration."""
            query_method = ai_engine.module.query
            if asyncio.iscoroutinefunction(query_method):
                return await query_method(message)
            else:
                return query_method(message)

        if self.pai_protocol_handler.pai_available:
            # Verwende PAI v2.2 Protokoll via den Handler
            # Wichtig: Der PAI-Handshake im Handler sendet den Prompt wie er ist, 
            # da das PAI-Protokoll die Unicode-Instruktion selbst hinzufügt oder erwartet.
            # Daher hier nur den "reinen" Prompt übergeben.
            response = await self.pai_protocol_handler.communicate_with_pai(
                ai_caller=ai_caller_wrapper,
                ai_name=ai_engine.key,
                message=prompt, # Hier den reinen Prompt, PAI fügt Instruktion hinzu
                context="PowerTalk Unicode Discourse"
            )
            return response
        else:
            # Fallback zu direktem API-Aufruf mit manueller Unicode-Extraktion
            try:
                raw_response_content = await ai_caller_wrapper(enhanced_prompt) # Hier den angereicherten Prompt nutzen

                extracted_unicode, natural_text = self.unicode_processor.extract_unicode_fields(raw_response_content)
                has_unicode = bool(extracted_unicode)

                # PAIResponse manuell erstellen (Nutzt die PAIResponse, die via pai_protocol_handler verfügbar ist)
                response = PAIResponse(
                    success=True,
                    content=natural_text if natural_text else raw_response_content,
                    protocol_used="unicode_fallback" if has_unicode else "natural_fallback",
                    ai_name=ai_engine.key,
                    timestamp=datetime.now().isoformat(),
                    handshake_strategy="manual_unicode_fallback",
                    has_unicode_fields=has_unicode,
                    response_format="unicode_text" if has_unicode else "natural"
                )

                # UnicodeData hinzufügen, falls Felder gefunden wurden (Nutzt die UnicodeData, die via pai_protocol_handler verfügbar ist)
                if has_unicode:
                    unicode_data = UnicodeData()
                    unicode_data.raw_fields = extracted_unicode
                    # Hier könnten spezifische Felder wie 'context', 'concepts' etc. geparst werden.
                    if "⚙" in extracted_unicode:
                        unicode_data.context = {"raw_context": extracted_unicode["⚙"]}
                    if "💭" in extracted_unicode:
                        unicode_data.concepts = [c.strip() for c in extracted_unicode["💭"].split(',') if c.strip()]
                    if "🔀" in extracted_unicode:
                        unicode_data.relationships = [r.strip() for r in extracted_unicode["🔀"].split(',') if r.strip()]
                    if "❓" in extracted_unicode:
                        unicode_data.questions = extracted_unicode["❓"]
                    if "💬" in extracted_unicode:
                        unicode_data.explanations = extracted_unicode["💬"]
                    response.unicode_data = unicode_data
                
                # Analysen manuell aktualisieren, da der PAIProtocolHandler nicht direkt verwendet wurde
                self.pai_protocol_handler.unicode_analytics.total_responses += 1
                self.pai_protocol_handler.unicode_analytics.ai_adoption_rates[ai_engine.key]['total'] += 1
                if has_unicode:
                    self.pai_protocol_handler.unicode_analytics.unicode_responses += 1
                    self.pai_protocol_handler.unicode_analytics.ai_adoption_rates[ai_engine.key]['unicode'] += 1
                    if response.unicode_data and response.unicode_data.raw_fields:
                        for field_key in response.unicode_data.raw_fields:
                            self.pai_protocol_handler.unicode_analytics.field_usage[field_key] += 1
                self.pai_protocol_handler.unicode_analytics.protocol_distribution[response.protocol_used] += 1

                return response
            except Exception as e:
                import traceback
                error_details = f"PAI Protocol Error: {type(e).__name__}: {str(e)}\nTraceback: {traceback.format_exc()}"
                print(f"DEBUG EXCEPTION: {error_details}")  # Add this line!
                return PAIResponse( 
                    success=False, content=error_details, protocol_used="error",
                    ai_name=ai_engine.key, timestamp=datetime.now().isoformat(),
                    handshake_strategy="api_error"
                )