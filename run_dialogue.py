#!/usr/bin/env python3
# run_dialogue.py - Korrigierte Pfade

import os
import sys
import json
from importlib import util

# Hauptverzeichnis des Projekts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Manuell Dialog-Engine importieren
engine_path = os.path.join(BASE_DIR, "core", "dialogue_engine.py")
engine_spec = util.spec_from_file_location("dialogue_engine", engine_path)
engine_module = util.module_from_spec(engine_spec)
engine_spec.loader.exec_module(engine_module)
DialogueEngine = engine_module.DialogueEngine

# Manuell Qwen-Integration importieren
qwen_path = os.path.join(BASE_DIR, "integrations", "qwen.py")
qwen_spec = util.spec_from_file_location("qwen", qwen_path)
qwen_module = util.module_from_spec(qwen_spec)
qwen_spec.loader.exec_module(qwen_module)

# Manuell Claude-Integration importieren
claude_path = os.path.join(BASE_DIR, "integrations", "claude.py")
claude_spec = util.spec_from_file_location("claude", claude_path)
claude_module = util.module_from_spec(claude_spec)
claude_spec.loader.exec_module(claude_module)

def run_dialogue():
    print("🚀 Starte CORTEX-Dialog mit korrigierten Pfaden...")
    try:
        # Setze die Integrationen in der Engine
        engine_module.claude = claude_module
        engine_module.qwen = qwen_module
        
        engine = DialogueEngine()
        result = engine.run_exchange(
            topic="Die Erfahrung des Denkens neben einer anderen KI"
        )
        
        with open("manual_dialogue.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dialog abgeschlossen! Ergebnis in manual_dialogue.json")
        
        # Vorschau anzeigen
        print("\n--- Dialogvorschau ---")
        for entry in result["exchange"]:
            print(f"\n{entry['speaker']}:\n{entry['content'][:200]}...")
            
        return True
    except Exception as e:
        print(f"❌ Kritischer Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_dialogue()
    sys.exit(0 if success else 1)