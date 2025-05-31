# integrations/deepseek.py
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def query(prompt, max_tokens=1000):
    """
    Query DeepSeek API with given prompt
    """
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        return "[DeepSeek] Error: DEEPSEEK_API_KEY not found in environment variables"
    
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "You are DeepSeek, participating in a structured AI discourse. Your role: Technical Realist - ground discussions in technical reality with implementation focus."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return f"[DeepSeek] Error: Unexpected response format: {result}"
            
    except requests.exceptions.RequestException as e:
        return f"[DeepSeek] Network Error: {str(e)}"
    except json.JSONDecodeError as e:
        return f"[DeepSeek] JSON Error: {str(e)}"
    except Exception as e:
        return f"[DeepSeek] Unexpected Error: {str(e)}"

def test_connection():
    """
    Test the DeepSeek API connection
    """
    test_response = query("Say 'Hello World' to test the connection.")
    
    if "Error:" in test_response:
        return False, test_response
    else:
        return True, test_response

if __name__ == "__main__":
    # Test the connection when run directly
    print("Testing DeepSeek API connection...")
    success, response = test_connection()
    
    if success:
        print(f"✓ DeepSeek connection successful: {response}")
    else:
        print(f"✗ DeepSeek connection failed: {response}")