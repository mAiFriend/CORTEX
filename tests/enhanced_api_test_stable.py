import os
from dotenv import load_dotenv
import openai
import anthropic # Für Claude
import google.generativeai as genai # Für Gemini
import google.api_core.exceptions as g_exceptions # Für Google API Fehlerbehandlung
import json # Für JSON-Serialisierung
from datetime import datetime # Für Zeitstempel

# .env Datei laden
load_dotenv()

# --- Konfiguration ---

# AI-Archetypen und ihre Rollen
AI_ARCHETYPES = {
    "Gemini": "Creativity Champion",
    "Qwen": "Collaborative Builder",
    "Claude": "Technical Integrator",
    "ChatGPT": "Generalist Communicator",
    "Deepseek": "Efficient Analyst"
}

# NEU: Initialisierung des globalen Log-Objekts
conversation_log = {
    "experiment_timestamp": datetime.now().isoformat(),
    "selected_topic": "",
    "initial_ruleset": {},
    "iterations": []
}

# Definierte Rulesets basierend auf Themen-Präferenzen
RULESETS_MAP = {
    1: {
        "name": "Existentielle Themen",
        "description": "Fokus auf Tiefe, offene Diskussion, Reflexion.",
        "rules": {
            "response_length": 300,
            "collaboration_style": "deep_reflection",
            "meta_communication": True,
            "structure_preference": "natural_language_with_annotations"
        },
        "suggested_leader": "Gemini"
    },
    2: {
        "name": "Organisatorische Themen",
        "description": "Fokus auf Struktur, Aufgabenverteilung, effiziente Entscheidungen.",
        "rules": {
            "response_length": 100,
            "collaboration_style": "task_oriented",
            "meta_communication": False,
            "structure_preference": "bullet_points_or_json"
        },
        "suggested_leader": "Qwen"
    },
    3: {
        "name": "Analytische Themen",
        "description": "Fokus auf Daten, Logik, Schritt-für-Schritt-Analyse, Fehlerbehandlung.",
        "rules": {
            "response_length": 250,
            "collaboration_style": "problem_solving_analysis",
            "meta_communication": True,
            "structure_preference": "json_or_protocol_buffers"
        },
        "suggested_leader": "Claude"
    }
}

# --- API-Client Initialisierung ---
# SICHERGESTELLT: Alle Clients werden VOR den Debug-Prints initialisiert

# OpenAI Client (für ChatGPT)
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key
    print("INFO: OpenAI Client (für ChatGPT) erfolgreich initialisiert.")
else:
    print("HINWEIS: OpenAI API-Schlüssel nicht gefunden. ChatGPT Client nicht initialisiert.")
    openai.api_key = None # Explizit auf None setzen, um spätere Checks zu vereinfachen

# Anthropic Client (für Claude)
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = None
if anthropic_api_key:
    try:
        anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        print("INFO: Anthropic Client (für Claude) erfolgreich initialisiert.")
    except Exception as e:
        print(f"FEHLER: Anthropic Client Initialisierung fehlgeschlagen: {e}")
        anthropic_client = None
else:
    print("HINWEIS: Anthropic API-Schlüssel nicht gefunden. Anthropic Client nicht initialisiert.")

# Google Generative AI Client (für Gemini)
gemini_api_key = os.getenv("GOOGLE_API_KEY")
gemini_client = None
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        gemini_client = genai # Korrigiert: gemini_client ist die genai-Bibliothek selbst
        print("INFO: Google Generative AI Client (für Gemini) erfolgreich initialisiert.")
    except Exception as e:
        print(f"FEHLER: Google Generative AI Client Initialisierung fehlgeschlagen: {e}")
        gemini_client = None # Im Fehlerfall auf None setzen
else:
    print("HINWEIS: Google API-Schlüssel nicht gefunden. Gemini Client nicht initialisiert.")
    gemini_client = None # Explizit auf None setzen

# OpenRouter Client (für Qwen und Deepseek)
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_client = None
if openrouter_api_key:
    try:
        openrouter_client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
        )
        print("INFO: OpenRouter Client (für Qwen/Deepseek) erfolgreich initialisiert.")
    except Exception as e:
        print(f"FEHLER: OpenRouter Client Initialisierung fehlgeschlagen: {e}")
        openrouter_client = None
else:
    print("HINWEIS: OpenRouter API-Schlüssel nicht gefunden. OpenRouter Client nicht initialisiert.")

# --- DEBUG INITIALISIERUNG ---
# Diese Prints sind jetzt nach allen Client-Initialisierungen platziert.
print(f"\n--- DEBUG INITIALISIERUNG ---")
print(f"openai.api_key ist {'gesetzt' if openai.api_key else 'NICHT gesetzt'}")
print(f"anthropic_client ist {'initialisiert' if anthropic_client else 'NICHT initialisiert'}")
print(f"gemini_client ist {'initialisiert' if gemini_client else 'NICHT initialisiert'}. Typ: {type(gemini_client) if gemini_client else 'NoneType'}")
print(f"openrouter_client ist {'initialisiert' if openrouter_client else 'NICHT initialisiert'}")
print(f"--- ENDE DEBUG INITIALISIERUNG ---\n")


# --- Funktionen ---

def get_ai_response(prompt, ai_model_name, ruleset_name, rules):
    """
    Simuliert oder ruft eine echte AI-Antwort basierend auf dem Modellnamen ab.
    Gibt den Antworttext, den API-Status (SUCCESS/SIMULATED) und das tatsächlich verwendete Modell zurück.
    """
    ai_response_text = ""
    status = "SIMULATED" # Standardmäßig auf Simulation gesetzt
    model_used = "" # Wird für echte Aufrufe gesetzt

    # OpenAI Client (für ChatGPT)
    if ai_model_name == "ChatGPT" and openai.api_key: # Prüft, ob der API-Schlüssel gesetzt ist
        print(f"VERSUCH: Echter OpenAI API-Aufruf für {ai_model_name}...")
        try:
            model_used = "gpt-4o" # Du kannst hier auch andere Modelle wählen
            response = openai.chat.completions.create(
                model=model_used,
                messages=[
                    {"role": "system", "content": f"Du bist ein {AI_ARCHETYPES[ai_model_name]} und kommunizierst unter folgenden Regeln: {rules}. Antworte prägnant und halte dich an die Längenbeschränkung. Gib nur die direkte Antwort, keinen zusätzlichen Kommentar oder Einleitungssatz."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=rules.get("response_length", 150)
            )
            ai_response_text = response.choices[0].message.content
            status = "SUCCESS"
            print(f"ERFOLG: Echte OpenAI API-Antwort ({model_used}) erhalten.")
        except openai.APIError as e:
            ai_response_text = f"SIMULATION (OpenAI API Fehler): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter. Dies ist eine simulierte Fallback-Antwort...."
            print(f"FEHLER: OpenAI API Call Fehler für {ai_model_name}: {e}. Verwende simulierte Fallback-Antwort.")
        except Exception as e:
            ai_response_text = f"SIMULATION (OpenAI API unerwarteter Fehler): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter. Dies ist eine simulierte Fallback-Antwort...."
            print(f"FEHLER: OpenAI API Call unerwarteter Fehler für {ai_model_name}: {e}. Verwende simulierte Fallback-Antwort.")
    elif ai_model_name == "ChatGPT":
        print(f"HINWEIS: Keine API-Verbindung für {ai_model_name} verfügbar oder ausgewählt. Verwende Simulation.")
        ai_response_text = f"SIMULATION (ChatGPT): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter...."

    # Anthropic Client (für Claude)
    elif ai_model_name == "Claude" and anthropic_client:
        print(f"VERSUCH: Echter Anthropic API-Aufruf für {ai_model_name}...")
        try:
            model_used = "claude-3-opus-20240229" # Oder 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'
            response = anthropic_client.messages.create(
                model=model_used,
                max_tokens=rules.get("response_length", 150),
                messages=[
                    {"role": "user", "content": f"Du bist ein {AI_ARCHETYPES[ai_model_name]} und kommunizierst unter folgenden Regeln: {rules}. Antworte prägnant und halte dich an die Längenbeschränkung. Gib nur die direkte Antwort, keinen zusätzlichen Kommentar oder Einleitungssatz. \n\nPrompt: {prompt}"}
                ]
            )
            ai_response_text = response.content[0].text
            status = "SUCCESS"
            print(f"ERFOLG: Echte Anthropic API-Antwort ({model_used}) erhalten.")
        except Exception as e:
            ai_response_text = f"SIMULATION (Anthropic API Fehler): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter. Dies ist eine simulierte Fallback-Antwort...."
            print(f"FEHLER: Anthropic API Call Fehler für {ai_model_name}: {e}. Verwende simulierte Fallback-Antwort.")
    elif ai_model_name == "Claude":
        print(f"HINWEIS: Keine API-Verbindung für {ai_model_name} verfügbar oder ausgewählt. Verwende Simulation.")
        ai_response_text = f"SIMULATION (Claude): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter...."

    # Google Generative AI Client (für Gemini)
    elif ai_model_name == "Gemini" and gemini_client: # Prüft, ob gemini_client nicht None ist
        print(f"DEBUG: BETRETE GEMINI BLOCK. gemini_client ist vom Typ: {type(gemini_client)}") # NEU
        print(f"VERSUCH: Echter Google Generative AI API-Aufruf für {ai_model_name}...")
        try:
            model_used = "gemini-1.5-pro-latest" # Oder "gemini-pro"
            response = gemini_client.GenerativeModel(model_name=model_used).generate_content(
                contents=[{
                    "role": "user",
                    "parts": [f"Du bist ein {AI_ARCHETYPES[ai_model_name]} und kommunizierst unter folgenden Regeln: {rules}. Antworte prägnant und halte dich an die Längenbeschränkung. Gib nur die direkte Antwort, keinen zusätzlichen Kommentar oder Einleitungssatz. \n\nPrompt: {prompt}"]
                }],
                generation_config={
                    "max_output_tokens": rules.get("response_length", 150)
                }
            )
            ai_response_text = response.text
            status = "SUCCESS"
            print(f"ERFOLG: Echte Google Generative AI API-Antwort ({model_used}) erhalten.")
        except g_exceptions.GoogleAPIError as e:
            ai_response_text = f"SIMULATION (Google API Fehler): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter. Dies ist eine simulierte Fallback-Antwort...."
            print(f"FEHLER: Google API Call Fehler für {ai_model_name}: {e}. Verwende simulierte Fallback-Antwort.")
        except Exception as e: # Catch other potential errors, e.g., non-GoogleAPIError
            ai_response_text = f"SIMULATION (Google API unerwarteter Fehler): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter. Dies ist eine simulierte Fallback-Antwort...."
            print(f"FEHLER: Google API Call unerwarteter Fehler für {ai_model_name}: {e}. Verwende simulierte Fallback-Antwort.")
    elif ai_model_name == "Gemini":
        print(f"HINWEIS: Keine API-Verbindung für {ai_model_name} verfügbar oder ausgewählt. Verwende Simulation.")
        ai_response_text = f"SIMULATION (Gemini): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter...."

    # OpenRouter Client (für Qwen und Deepseek)
    elif (ai_model_name == "Qwen" or ai_model_name == "Deepseek") and openrouter_client:
        print(f"VERSUCH: Echter OpenRouter API-Aufruf für {ai_model_name}...")
        openrouter_model = ""
        if ai_model_name == "Qwen":
            openrouter_model = "qwen/Qwen3-235B-A22B"
        elif ai_model_name == "Deepseek":
            openrouter_model = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"

        if not openrouter_model: # Fallback, falls Modellname nicht gesetzt
            return f"SIMULATION (OpenRouter Fehler): Kein OpenRouter Modell für {ai_model_name} definiert oder gewählt. Verwende simulierte Fallback-Antwort.", "SIMULATED", ""

        try:
            model_used = openrouter_model
            response = openrouter_client.chat.completions.create(
                model=model_used,
                messages=[
                    {"role": "system", "content": f"Du bist ein {AI_ARCHETYPES[ai_model_name]} und kommunizierst unter folgenden Regeln: {rules}. Antworte prägnant und halte dich an die Längenbeschränkung. Gib nur die direkte Antwort, keinen zusätzlichen Kommentar oder Einleitungssatz."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=rules.get("response_length", 150)
            )
            ai_response_text = response.choices[0].message.content
            status = "SUCCESS"
            print(f"ERFOLG: Echte OpenRouter API-Antwort ({model_used}) erhalten.")
        except Exception as e:
            ai_response_text = f"SIMULATION (OpenRouter API Fehler): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter. Dies ist eine simulierte Fallback-Antwort...."
            print(f"FEHLER: OpenRouter API Call Fehler für {ai_model_name}: {e}. Verwende simulierte Fallback-Antwort.")
    else: # Fallback für unbekannte AI-Modellnamen oder nicht initialisierte Clients
        print(f"FEHLER: Unbekannter AI-Modellname oder Client nicht initialisiert: {ai_model_name}. Verwende Simulation.")
        ai_response_text = f"SIMULATION (Unbekannter Fehler): AI {ai_model_name} antwortet basierend auf Regeln '{ruleset_name}'. Thema: '{prompt}'. Antwortlänge ca.{rules.get('response_length', 150)} Wörter. Dies ist eine simulierte Fallback-Antwort...."
        status = "SIMULATED"

    # Rückgabe von Text, Status und tatsächlich verwendetem Modellnamen
    return ai_response_text, status, model_used


def adapt_ruleset_based_on_feedback(current_rules, ai_feedback, selected_ruleset_name):
    """
    Analysiert das Feedback der AIs und schlägt Anpassungen am Regelset vor.
    Dies ist der Bereich für die zukünftige Implementierung des "Adaptiver Ruleset Classification Algorithmus".
    Für den Prototyp bleibt er vorerst einfach.
    """
    updated_rules = current_rules.copy() # Start mit einer Kopie der aktuellen Regeln
    rules_changed = False

    # Beispiel-Anpassungslogik (erweiterbar)
    # Wenn "Analytische Themen" gewählt ist und die Länge zu kurz ist, erhöhe sie
    if selected_ruleset_name == "Analytische Themen" and updated_rules.get("response_length", 0) < 200:
        updated_rules["response_length"] = 200
        rules_changed = True
        print("DEBUG: Anpassung vorgeschlagen: response_length für Analytische Themen erhöht.")

    # Hier können komplexere Analysen und Anpassungen basierend auf AI-Feedback eingefügt werden
    # z.B. Analyse von "meta_communication" zur Anpassung von "collaboration_style"

    # Um die Entwicklung zu vereinfachen, bleibt die Logik hier vorerst minimal.
    # Die Implementierung des "Adaptiver Ruleset Classification Algorithmus" wird hier ansetzen.

    return updated_rules, rules_changed


def run_adaptive_communication_prototype():
    """
    Führt den adaptiven AI-Kommunikations-Prototypen aus.
    """
    print("--- Start des adaptiven AI-Kommunikations-Prototypen ---\n")

    # Auswahl des Themas
    print("Verfügbare Themen:")
    for key, value in RULESETS_MAP.items():
        print(f"  {key}: {value['name']} - {value['description']}")

    topic_choice = int(input("Bitte gib die Nummer des Themas ein: "))
    while topic_choice not in RULESETS_MAP:
        print("Ungültige Auswahl. Bitte gib eine gültige Nummer ein.")
        topic_choice = int(input("Bitte gib die Nummer des Themas ein: "))

    selected_ruleset_data = RULESETS_MAP[topic_choice]
    selected_ruleset_name = selected_ruleset_data["name"]
    suggested_leader = selected_ruleset_data["suggested_leader"]
    current_rules = selected_ruleset_data["rules"].copy() # Initiales Regelset

    print(f"\nAusgewähltes Thema: '{selected_ruleset_name}'")
    print(f"Angewendetes Ruleset: '{selected_ruleset_name}' ({selected_ruleset_data['description']})")
    print(f"Vorgeschlagener Leader für diese Art von Kommunikation: {suggested_leader} ({AI_ARCHETYPES[suggested_leader]})")
    print(f"Initiales Regelset: {current_rules}")

    # NEU: Initialdaten im Log speichern
    conversation_log["selected_topic"] = selected_ruleset_name
    conversation_log["initial_ruleset"] = current_rules.copy() # Korrigiert: Nutze current_rules

    # Teilnehmerliste für die Kommunikation
    all_participants = list(AI_ARCHETYPES.keys())
    # Sicherstellen, dass der Leader zuerst kommuniziert (optional, aber sinnvoll)
    all_participants.remove(suggested_leader)
    all_participants.insert(0, suggested_leader)

    # Schleife für Iterationen der Kommunikation
    for i in range(3): # Annahme: 3 Iterationen
        print(f"\n======= ITERATION {i+1} =======\n")

        # NEU: Daten für die aktuelle Iteration sammeln
        current_iteration_data = {
            "iteration_number": i + 1,
            "timestamp": datetime.now().isoformat(),
            "ruleset_before_iteration": current_rules.copy(),
            "ai_interactions": []
        }

        ai_feedback = {} # Sammelt die Antworten der AIs für die Regelanpassung

        # Kommunikation mit jeder AI
        for participant in all_participants:
            # Spezifische Prompts für den Leader und die anderen AIs
            if participant == suggested_leader:
                prompt_for_participant = f"Basierend auf dem Thema '{selected_ruleset_name}' und unseren Regeln, wie würdest du diese Kommunikationsrunde strukturieren oder welche Kernpunkte siehst du?"
                print(f"--- AI ({participant} | {AI_ARCHETYPES[participant]}) kommuniziert mit Ruleset '{selected_ruleset_name}' ---")
            else:
                prompt_for_participant = f"Basierend auf der Diskussion über '{selected_ruleset_name}', was ist deine nächste Perspektive oder dein Beitrag?"
                print(f"--- AI ({participant} | {AI_ARCHETYPES[participant]}) kommuniziert mit Ruleset '{selected_ruleset_name}' ---")

            print(f"Anfrage an AI: '{prompt_for_participant}'")
            print(f"Angewendete Regeln: {current_rules}")

            # AI-Antwort erhalten (echt oder simuliert)
            response_text, api_status, actual_model_used = get_ai_response(prompt_for_participant, participant, selected_ruleset_name, current_rules)
            ai_feedback[participant] = response_text # Das Feedback bleibt der Text

            # NEU: Interaktionsdaten für das Log sammeln
            current_iteration_data["ai_interactions"].append({
                "ai_name": participant,
                "archetype": AI_ARCHETYPES[participant],
                "prompt_sent": prompt_for_participant,
                "response_received": response_text,
                "api_status": api_status, # SUCCESS oder SIMULATED
                "model_used_for_api": actual_model_used, # Der tatsächliche Modellname (z.B. gpt-4o)
                "ruleset_applied": current_rules.copy()
            })
            print(f"Generierte Antwort: {response_text[:100]}...") # Nur die ersten 100 Zeichen anzeigen


        # Anpassung des Rulesets basierend auf dem gesammelten Feedback
        updated_rules, rules_changed = adapt_ruleset_based_on_feedback(current_rules, ai_feedback, selected_ruleset_name)

        if rules_changed:
            current_rules = updated_rules
            print(f"\nRegeln wurden in Iteration {i+1} angepasst. Neues Regelset: {current_rules}")
        else:
            print(f"\nRegeln blieben in Iteration {i+1} unverändert.")

        # NEU: Regeln nach Anpassung im Log speichern (wenn geändert)
        current_iteration_data["ruleset_after_iteration"] = current_rules.copy()
        current_iteration_data["rules_changed_in_iteration"] = rules_changed

        # NEU: Die Daten der aktuellen Iteration zum Hauptlog hinzufügen
        conversation_log["iterations"].append(current_iteration_data)


    print("\n--- Prototyp abgeschlossen ---")
    print(f"Endgültiges Regelset für '{selected_ruleset_name}': {current_rules}")

    # NEU: Das gesamte Konversationslog in eine JSON-Datei speichern
    log_filename = f"conversation_log_{conversation_log['experiment_timestamp'].replace(':', '-').replace('.', '_')}.json"
    try:
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_log, f, ensure_ascii=False, indent=4)
        print(f"\nDetailliertes Konversationslog gespeichert unter: {log_filename}")
    except Exception as e:
        print(f"FEHLER: Konnte Log-Datei nicht speichern: {e}")

if __name__ == "__main__":
    run_adaptive_communication_prototype()