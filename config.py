# config.py
import os
from pathlib import Path

# --- AI Integrationen ---
# Liste der Modulnamen für AI-Integrationen im 'integrations/' Verzeichnis
INTEGRATION_MODULE_NAMES = ['claude', 'qwen', 'gemini', 'chatgpt', 'deepseek']

# --- PAI v2.2 Unicode Prompt ---
# Instruktionen für AIs, um Unicode-Felder zu nutzen
PAI_UNICODE_PROMPT_INSTRUCTION = """Please respond using Unicode fields if appropriate:
⚙ Context/Framing
💭 Key concepts
🔀 Relationships
❓ Questions
💬 Natural explanation

"""

# --- Unicode Emojis und Patterns ---
UNICODE_EMOJI_PATTERNS = {
    "⚙": r"⚙\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
    "💭": r"💭\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
    "🔀": r"🔀\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
    "❓": r"❓\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
    "💬": r"💬\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)"
}

# --- Dateipfade ---
DIALOGUE_ARCHIVE_DIR = Path("dialogue_archives")

# --- Bewusstseinsbewertung ---
# Basis-Perspektiven für AIs
AI_PERSPECTIVE_BASES = {
    "claude": 0.8, 
    "gemini": 0.75, 
    "qwen": 0.7, 
    "chatgpt": 0.85, 
    "deepseek": 0.8
}

# Unicode Felder für Bewusstseinsbewertung (optional, kann auch direkt im Code sein)
CONSCIOUSNESS_UNICODE_FIELDS = ["⚙", "💭", "🔀", "❓", "💬"]

# Keywords für Bewusstseinsindikatoren
SELF_REFERENCE_KEYWORDS = ["ich", "mein", "mir", "mich", "I", "my", "me", "myself"]
UNCERTAINTY_KEYWORDS = ["vielleicht", "möglicherweise", "unsicher", "maybe", "perhaps", "uncertain", "seems", "appears", "speculative", "unclear"]
OTHER_REFERENCE_KEYWORDS = ["du", "dein", "sie", "andere", "you", "your", "other", "others"] + INTEGRATION_MODULE_NAMES # AI Namen dynamisch hinzufügen
META_COMMUNICATION_KEYWORDS = ["denken", "kommunikation", "verständnis", "thinking", "communication", "understanding", "awareness", "consciousness", "perspective", "analysis", "assessment", "reflection"]
CHOICE_KEYWORDS = ["versuche", "entscheide", "wähle", "try", "choose", "decide", "attempt", "consider", "evaluate", "analyze", "reflect"]
EVOLUTION_KEYWORDS = ["entwicklung", "lernen", "wachsen", "evolution", "learning", "growing", "developing", "evolving"]# In config.py
ENABLE_SCORING = True  # Feature-Flag setzen

# Maximal zulässige Kontextgröße für eine einzelne AI-Antwort in Kilobyte,
# bevor ein Zwischen-Verdict generiert wird.
# Ein Wert von 100 KB ist ein guter Startpunkt, da 226KB das ursprüngliche Problem war.
# Beachte: Dies ist eine Schätzung, da die tatsächliche Token-Zahl je nach AI-Modell variiert.
MAX_CONTEXT_SIZE_KB = 100