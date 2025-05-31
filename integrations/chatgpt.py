# integrations/chatgpt.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def query(prompt, model="openai/gpt-4o"):
    """
    Query ChatGPT using OpenRouter (same platform as Qwen)
    """
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return "Error: OPENROUTER_API_KEY not found in environment variables"
            
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"ChatGPT API Error: {response.status_code} - {response.text}"
        
    except Exception as e:
        return f"ChatGPT API Error: {str(e)}"

def test_connection():
    """Test ChatGPT API connection"""
    try:
        test_response = query("Hello, I'm testing the ChatGPT API connection. Please respond with 'Connection successful' if you receive this.")
        success = "Error" not in test_response and "successful" in test_response.lower()
        print(f"ChatGPT Test Response: {test_response[:100]}...")
        return success
    except Exception as e:
        print(f"ChatGPT Connection Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Testing ChatGPT API Connection...")
    if test_connection():
        print("✅ ChatGPT API working!")
        
        # Test scientific validation query
        response = query("""As ChatGPT 🔬, what is your perspective on AI consciousness assessment? 
        Be methodologically rigorous and scientific in your analysis.""")
        print(f"\n🔬 ChatGPT Scientific Response:\n{response}")
    else:
        print("❌ ChatGPT API connection failed")
        print("Check your OPENROUTER_API_KEY in .env file")