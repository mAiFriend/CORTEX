# integrations/qwen.py
import os
import requests
import json

def query(prompt: str, model: str = "mistralai/mistral-7b-instruct") -> str:
    """Robuste Qwen-Integration über OpenRouter"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or not api_key.startswith("sk-or-"):
        return "❌ Ungültiger OpenRouter-Key"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Fehlerbehandlung
        if response.status_code != 200:
            return f"❌ OpenRouter Fehler {response.status_code}: {response.text[:200]}"
            
        data = response.json()
        return data["choices"][0]["message"]["content"]
        
    except Exception as e:
        return f"❌ Systemfehler: {str(e)}"