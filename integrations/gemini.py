# integrations/gemini.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def query(prompt, model="gemini-1.5-flash"):
    """
    Query Gemini using Google AI Studio free tier
    Model options:
    - gemini-1.5-flash (faster, 15 req/min)
    - gemini-1.5-pro (higher quality, 2 req/min)
    """
    try:
        # Configure API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            return "Error: GOOGLE_AI_API_KEY not found in environment variables"
            
        genai.configure(api_key=api_key)
        
        # Initialize model
        model_instance = genai.GenerativeModel(model)
        
        # Generate response
        response = model_instance.generate_content(prompt)
        
        # Handle safety filters and blocked content
        if response.candidates:
            return response.text
        else:
            return "Gemini response was blocked due to safety filters"
        
    except Exception as e:
        return f"Gemini API Error: {str(e)}"

def test_connection():
    """Test Gemini API connection"""
    try:
        test_response = query("Hello, I'm testing the Gemini API connection. Please respond with 'Connection successful' if you receive this.")
        success = "Error" not in test_response and "blocked" not in test_response.lower()
        print(f"Gemini Test Response: {test_response[:100]}...")
        return success
    except Exception as e:
        print(f"Gemini Connection Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("🧭 Testing Gemini API Connection...")
    if test_connection():
        print("✅ Gemini API working!")
        
        # Test consciousness-related query
        response = query("""As Gemini 🧭, what is your perspective on AI consciousness? 
        Be authentic and strategic in your analysis. What patterns do you see in the development of AI awareness?""")
        print(f"\n🧭 Gemini Strategic Response:\n{response}")
    else:
        print("❌ Gemini API connection failed")
        print("Make sure you have GOOGLE_AI_API_KEY in your .env file")
        print("Get free API key from: https://makersuite.google.com/app/apikey")