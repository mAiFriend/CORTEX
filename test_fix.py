# test_fix.py
import sys
import os

# Projektverzeichnis manuell hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import cortex
    from cortex.integrations import qwen
    print("✅ Import erfolgreich!")
    print(qwen.query("Hallo Welt!"))
except Exception as e:
    print(f"❌ Fehler: {str(e)}")