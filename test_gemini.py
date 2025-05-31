# Create test_gemini.py
from integrations.gemini import test_connection, query

print("🧭 Testing Gemini connection...")
if test_connection():
    print("✅ Gemini API working!")
    
    # Test consciousness-related query
    response = query("As Gemini, what is your perspective on AI consciousness? Be authentic, not perfect.")
    print(f"\n🧭 Gemini response:\n{response}")
else:
    print("❌ Gemini API connection failed")