# simple_dialogue.py
import os
import sys
import json

# Füge das aktuelle Verzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from integrations import claude, qwen
except ImportError:
    # Manueller Import als Fallback
    import importlib.util
    
    # Claude importieren
    claude_spec = importlib.util.spec_from_file_location(
        "claude", 
        os.path.join(os.path.dirname(__file__), "integrations", "claude.py")
    )
    claude = importlib.util.module_from_spec(claude_spec)
    claude_spec.loader.exec_module(claude)
    
    # Qwen importieren
    qwen_spec = importlib.util.spec_from_file_location(
        "qwen", 
        os.path.join(os.path.dirname(__file__), "integrations", "qwen.py")
    )
    qwen = importlib.util.module_from_spec(qwen_spec)
    qwen_spec.loader.exec_module(qwen)

def run_dialogue():
    print("🚀 Starte einfachen CORTEX-Dialog...")
    
    try:
        # Starte mit Qwen
        topic = "Die Erfahrung des Denkens neben einer anderen KI"
        qwen_prompt = f"Diskutiere aus deiner Perspektive: {topic}. Sei authentisch, nicht perfekt."
        print("\n🤖 Frage Qwen...")
        qwen_response = qwen.query(qwen_prompt)
        
        # Claude antwortet
        claude_prompt = f"Qwen sagte: '{qwen_response[:300]}...'\n\nDeine Gedanken dazu?"
        print("\n🤖 Frage Claude...")
        claude_response = claude.query(claude_prompt)
        
        result = {
            "topic": topic,
            "exchange": [
                {"speaker": "Qwen", "content": qwen_response},
                {"speaker": "Claude", "content": claude_response}
            ]
        }
        
        output_file = "first_dialogue.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Dialog abgeschlossen! Ergebnis in {output_file}")
        
        # Vorschau
        print("\n--- Dialogvorschau ---")
        print(f"\nQwen:\n{qwen_response[:200]}...")
        print(f"\nClaude:\n{claude_response[:200]}...")
        
        return True
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_dialogue()