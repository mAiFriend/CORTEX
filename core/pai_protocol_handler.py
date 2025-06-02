# core/pai_protocol_handler.py

import sys
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from collections import defaultdict

# Importiere deine UnicodeAnalytics Dataclass aus models.py
from models import UnicodeAnalytics 

# PAI-bezogene Imports von der pai-Bibliothek
PAI_AVAILABLE = False
try:
    from pai import PAIProtocolV22, PAIResponse, UnicodeData, create_pai_v22_session
    PAI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PAI v2.2 not available - falling back to basic communication. Error: {e}")
    # Fallback-Definitionen, falls pai-Lib nicht verfügbar ist
    @dataclass
    class UnicodeData:
        raw_fields: Dict[str, str] = field(default_factory=dict)
        context: Optional[Dict] = None
        concepts: List[str] = field(default_factory=list)
        relationships: List[str] = field(default_factory=list)
        questions: Optional[str] = None
        explanations: Optional[str] = None

    @dataclass
    class PAIResponse:
        success: bool
        content: str
        protocol_used: str
        ai_name: str
        timestamp: str
        handshake_strategy: str
        has_unicode_fields: bool = False
        unicode_data: Optional[UnicodeData] = None
        response_format: str = "natural" # "natural", "unicode_text", "structured"
        metadata: Optional[Dict] = None
    
    # Stellen Sie sicher, dass PAIProtocolV22 und create_pai_v22_session auch als Dummy-Objekte existieren,
    # falls sie im Code verwendet werden, wenn PAI_AVAILABLE False ist.
    # Für diesen Fall ist es besser, diese Funktionen gar nicht erst aufzurufen.

class PAIProtocolHandler:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.pai_session: Optional[PAIProtocolV22] = None # Typisierung
        self.pai_available = PAI_AVAILABLE
        self.unicode_analytics = UnicodeAnalytics() # Instanz für systemweite Analysen

        if self.pai_available:
            try:
                self.pai_session = create_pai_v22_session(enable_logging=debug_mode)
                print(f"✓ PAI v2.2 Protocol loaded and session initialized: {self.pai_session}")
            except Exception as e:
                self.pai_available = False
                print(f"Error initializing PAI v2.2 session: {e}. Falling back to basic communication.")
        else:
            print("PAI v2.2 not available, proceeding with basic communication.")

    async def communicate_with_pai(self, ai_caller, ai_name: str, message: str, context: str = "") -> PAIResponse:
        """
        Führt die Kommunikation über das PAI v2.2 Protokoll aus und aktualisiert Analysen.
        ai_caller ist eine Coroutine, die den eigentlichen AI-Aufruf kapselt.
        """
        if not self.pai_available or not self.pai_session:
            # Dies sollte in der aufrufenden Schicht (pai_communicator) behandelt werden,
            # aber zur Sicherheit hier eine Fehlerantwort.
            if self.debug_mode:
                print(f"🚨 DEBUG: PAI not available - pai_available={self.pai_available}, pai_session={self.pai_session}")
            return PAIResponse(
                success=False, content="PAI Protocol not initialized or available.", protocol_used="error",
                ai_name=ai_name, timestamp=datetime.now().isoformat(), handshake_strategy="not_initialized"
            )

        try:
            if self.debug_mode:
                print(f"🔍 DEBUG: Starting PAI communication for {ai_name}")
                print(f"🔍 DEBUG: Message length: {len(message)}")
                print(f"🔍 DEBUG: Context: {context}")

            # Der ai_caller (z.B. ai_engine.module.query) wird hier aufgerufen
            response = await self.pai_session.communicate(
                ai_caller=ai_caller,
                ai_name=ai_name,
                message=message,
                context=context
            )

            if self.debug_mode:
                print(f"🔍 DEBUG: PAI communication completed successfully")
                print(f"🔍 DEBUG: Response success: {response.success}")
                print(f"🔍 DEBUG: Response protocol: {response.protocol_used}")
                print(f"🔍 DEBUG: Response has_unicode: {response.has_unicode_fields}")

            # CRITICAL: Validate that successful structured responses are NOT treated as errors
            if response.success and response.protocol_used in ["structured", "unicode_json", "unicode_text"]:
                if self.debug_mode:
                    print(f"✅ DEBUG: Successful structured response detected - this is SUCCESS, not error!")
            
            # Update analytics
            self.unicode_analytics.total_responses += 1
            self.unicode_analytics.ai_adoption_rates[ai_name]['total'] += 1
            if response.has_unicode_fields:
                self.unicode_analytics.unicode_responses += 1
                self.unicode_analytics.ai_adoption_rates[ai_name]['unicode'] += 1
                if response.unicode_data and response.unicode_data.raw_fields:
                    for field_key in response.unicode_data.raw_fields:
                        self.unicode_analytics.field_usage[field_key] += 1

            # 🔧 BUGFIX: Use defaultdict behavior or safe increment
            if hasattr(self.unicode_analytics.protocol_distribution, '__missing__'):
                # If it's already a defaultdict, this will work automatically
                self.unicode_analytics.protocol_distribution[response.protocol_used] += 1
            else:
                # If it's a regular dict, use safe increment
                if response.protocol_used not in self.unicode_analytics.protocol_distribution:
                    self.unicode_analytics.protocol_distribution[response.protocol_used] = 0
                self.unicode_analytics.protocol_distribution[response.protocol_used] += 1

            if self.debug_mode:
                print(f"🔍 DEBUG: Analytics updated successfully")
                print(f"🔍 DEBUG: Protocol distribution: {dict(self.unicode_analytics.protocol_distribution)}")
                print(f"🔍 DEBUG: Returning successful response")

            return response

        except Exception as e:
            # ENHANCED DEBUG: Show the REAL exception details
            import traceback
            error_type = type(e).__name__
            error_message = str(e)
            error_traceback = traceback.format_exc()
            
            detailed_error = f"PAI Protocol Exception: {error_type}: {error_message}"
            
            if self.debug_mode:
                print(f"🚨 DEBUG EXCEPTION in communicate_with_pai:")
                print(f"🚨 DEBUG: Exception type: {error_type}")
                print(f"🚨 DEBUG: Exception message: {error_message}")
                print(f"🚨 DEBUG: ai_name: {ai_name}")
                print(f"🚨 DEBUG: message length: {len(message)}")
                print(f"🚨 DEBUG: Full traceback:")
                print(f"{error_traceback}")
                print(f"🚨 DEBUG: This exception is converting SUCCESS to ERROR!")
            
            # Return detailed error information
            return PAIResponse(
                success=False, 
                content=detailed_error,
                protocol_used="error",
                ai_name=ai_name, 
                timestamp=datetime.now().isoformat(),
                handshake_strategy="pai_error",
                metadata={
                    "error_type": error_type,
                    "error_message": error_message,
                    "error_traceback": error_traceback,
                    "debug_info": {
                        "message_length": len(message),
                        "context_length": len(context),
                        "pai_available": self.pai_available,
                        "pai_session_exists": self.pai_session is not None
                    }
                }
            )
            
    def get_unicode_analytics(self) -> UnicodeAnalytics:
        """Gibt die gesammelten Unicode-Analysedaten zurück."""
        return self.unicode_analytics