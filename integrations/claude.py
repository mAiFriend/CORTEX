import os
from anthropic import Anthropic

def query(prompt: str, model: str = "claude-3-opus-20240229") -> str:
    """Sendet eine Anfrage an Claude mit Authentizitäts-Fokus"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system="Antworte authentisch, nicht optimiert. Fehler sind erlaubt.",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text