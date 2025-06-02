# core/ai_manager.py

import sys
import asyncio
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

from models import AIEngine # Importiere deine AIEngine Dataclass
from config import INTEGRATION_MODULE_NAMES # Importiere die Modulliste

class AIManager:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.available_ais: Dict[str, AIEngine] = {}
        self._load_integrations()

    def _load_integrations(self):
        """Loads AI integration modules dynamically."""
        integrations_loaded = {}
        integration_load_errors = []

        # Füge den Ordner 'integrations' zum Pfad hinzu, falls nicht schon geschehen
        # Dies sollte in powertalk.py (main) erledigt werden, aber zur Sicherheit hier nochmal
        if 'integrations' not in sys.modules:
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) # Add parent dir to path for imports

        try:
            for module_name in INTEGRATION_MODULE_NAMES:
                try:
                    module = __import__(f'integrations.{module_name}', fromlist=[module_name])
                    integrations_loaded[module_name] = module
                except ImportError as ie:
                    integration_load_errors.append(f"Failed to load integration {module_name}: {ie}")
        except Exception as e:
            integration_load_errors.append(f"An unexpected error occurred during integrations import: {e}")

        if integration_load_errors:
            print(f"Warnings loading integrations: {'; '.join(integration_load_errors)}")
        if not integrations_loaded:
            print("CRITICAL ERROR: No AI integrations loaded. PowerTalk cannot function.")
            sys.exit(1)
        else:
            print("✓ All integrations loaded successfully")
        
        self.available_ais = {
            k: AIEngine(name=k.capitalize(), key=k, module=v) 
            for k, v in integrations_loaded.items()
        }

    async def ping_ai(self, ai_key: str, test_message: str = "Hello World...") -> Tuple[bool, str]:
        """Pings a single AI engine to test connectivity."""
        ai_engine = self.available_ais.get(ai_key)
        if not ai_engine or not ai_engine.module:
            return False, "AI not found or module not loaded."
        
        try:
            if hasattr(ai_engine.module, 'ping') and callable(ai_engine.module.ping):
                ping_method = ai_engine.module.ping
                if asyncio.iscoroutinefunction(ping_method):
                    response = await ping_method(test_message)
                else:
                    response = ping_method(test_message)
                return True, response
            elif hasattr(ai_engine.module, 'query') and callable(ai_engine.module.query):
                query_method = ai_engine.module.query
                if asyncio.iscoroutinefunction(query_method):
                    response = await query_method(test_message)
                else:
                    response = query_method(test_message)
                return True, response
            else:
                return False, "No 'ping' or 'query' method found in integration."
        except Exception as e:
            return False, str(e)

    async def test_all_ai_connectivity(self) -> List[str]:
        """Tests connectivity for all loaded AI engines."""
        print("🔍 Testing PowerTalk connectivity...")
        print("──────────────────────────────────────────────────")
        working_ais = []
        for ai_key, ai_engine in list(self.available_ais.items()): # Use list() to allow modification during iteration
            if ai_engine.enabled and ai_engine.module:
                print(f"Pinging {ai_engine.name.capitalize()}...", end="")
                success, message = await self.ping_ai(ai_key)
                if success:
                    print(f" ✓ Connected ({message[:20]}...)")
                    working_ais.append(ai_key)
                else:
                    print(f" ✗ Failed ({message})")
                    ai_engine.enabled = False # Disable non-working AI
        print("──────────────────────────────────────────────────")
        
        # Update available_ais to only include working ones (or just keep enabled flag)
        self.available_ais = {k: v for k, v in self.available_ais.items() if v.enabled}
        
        print(f"✅ Working AIs: {', '.join([ai.name for ai in self.available_ais.values()])}")
        return list(self.available_ais.keys())