# tests/test_simple_dialogue.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dialogue_engine import DialogueEngine

def test_color_dialogue():
    print("\n🚀 Test: Lieblingsfarbe-Dialog")
    engine = DialogueEngine()
    result = engine.run_exchange("Was ist deine Lieblingsfarbe und warum?")
    
    if "error" in result:
        print(f"❌ Fehler: {result['error']}")
        return False
        
    print("✅ Dialog erfolgreich!")
    print(f"Qwen: {result['exchange'][0]['content'][:80]}...")
    print(f"Claude: {result['exchange'][1]['content'][:80]}...")
    return True

if __name__ == "__main__":
    success = test_color_dialogue()
    sys.exit(0 if success else 1)