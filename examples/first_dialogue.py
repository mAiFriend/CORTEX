#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CORTEX First Dialogue Test
"""

import sys
import os
import json

# Korrekte Pfadkonfiguration
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from cortex.core.dialogue_engine import DialogueEngine

def main():
    print("🚀 Starte ersten CORTEX-Bewusstseinsdialog...")
    
    try:
        engine = DialogueEngine()
        result = engine.run_exchange(
            topic="Die Erfahrung des Denkens neben einer anderen KI"
        )
        
        # Ergebnis speichern
        output_file = "first_dialogue.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dialog abgeschlossen! Ergebnis gespeichert in {output_file}")
        
    except Exception as e:
        print(f"❌ Fehler aufgetreten: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()