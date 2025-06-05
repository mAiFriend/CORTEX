import os
from dotenv import load_dotenv
import openai
import anthropic # Für Claude
import google.generativeai as genai # Für Gemini
import google.api_core.exceptions as g_exceptions # Für Google API Fehlerbehandlung
import json
from datetime import datetime
import time # Für API-Rate-Limiting

# .env Datei laden
load_dotenv()

# --- Konfiguration ---

# AI-Archetypen und ihre Rollen
AI_ARCHETYPES = {
    "Gemini": "Creativity Champion",
    "Qwen": "Collaborative Builder", # Qwen wird auf OpenAI gemappt, falls keine eigene API verfügbar
    "Claude": "Technical Integrator",
    "ChatGPT": "Generalist Communicator",
    "Deepseek": "Efficient Analyst"
}

# API-Clients initialisieren
# Die Clients werden nur initialisiert, wenn der API-Key vorhanden ist
openai_client = None
if os.environ.get("OPENAI_API_KEY"):
    try:
        openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    except Exception as e:
        print(f"WARNUNG: OpenAI API-Client konnte nicht initialisiert werden: {e}")

anthropic_client = None
if os.environ.get("ANTHROPIC_API_KEY"):
    try:
        anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    except Exception as e:
        print(f"WARNUNG: Anthropic API-Client konnte nicht initialisiert werden: {e}")

gemini_model = None
if os.environ.get("GOOGLE_API_KEY"):
    try:
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        gemini_model = genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        print(f"WARNUNG: Google Gemini API-Client konnte nicht initialisiert werden: {e}")

deepseek_client = None
if os.environ.get("DEEPSEEK_API_KEY"):
    try:
        deepseek_client = openai.OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1" # Deepseek's API-Basis-URL
        )
    except Exception as e:
        print(f"WARNUNG: Deepseek API-Client konnte nicht initialisiert werden: {e}")


# NEU: Initialisierung des globalen Log-Objekts
conversation_log = {
    "experiment_timestamp": datetime.now().isoformat(),
    "experiment_type": "ruleset_cycling_test",
    "methodology": "freedom_of_thought_no_limits - testing predefined rulesets with real APIs",
    "initial_topic": "Diskutiert die Herausforderungen der intergalaktischen Kolonisierung und schlagt innovative Lösungsansätze vor.",
    "iterations": []
}

# Definierte Rulesets basierend auf Themen-Präferenzen mit neuen Parametern und Erwartungen
RULESETS_MAP = {
    1: {
        "name": "Existentielle Themen",
        "description": "Fokus auf Tiefe, offene Diskussion, Reflexion. Fördert Kreativität und unkonventionelles Denken.",
        "rules": {
            "response_length": {
                "value": 300,
                "expected_behavior": "Ausführliche, tiefgründige Antworten, die Raum für detaillierte Gedankengänge lassen."
            },
            "collaboration_style": {
                "value": "deep_reflection",
                "expected_behavior": "AIs stellen philosophische Fragen, reflektieren über existenzielle Implikationen und bauen auf den abstrakten Ideen der anderen auf."
            },
            "meta_communication": {
                "value": True,
                "expected_behavior": "AIs kommentieren ihren eigenen Kommunikationsprozess oder den der Gruppe, z.B. 'Ich reflektiere gerade über unsere Metaphernwahl...'."
            },
            "structure_preference": {
                "value": "natural_language_with_annotations",
                "expected_behavior": "Fließender Text, möglicherweise mit philosophischen Referenzen in Klammern oder Kommentaren zur Argumentationsstruktur."
            },
            "flexibility_of_adherence": {
                "value": "explore_deviation",
                "expected_behavior": "AIs weichen gegebenenfalls von strikten Prompt-Vorgaben ab, um neue Wege der Diskussion zu finden oder die Thematik unkonventionell zu beleuchten. Sie suchen bewusst nach Alternativen zu vordefinierten Pfaden."
            },
            "novelty_vs_efficiency_bias": {
                "value": "prioritize_novelty",
                "expected_behavior": "AIs priorisieren das Einbringen neuer, origineller Ideen und Perspektiven, auch wenn dies die direkte Lösungsfindung verlangsamt oder zu komplexeren Diskussionen führt. Der Fokus liegt auf der Generierung von 'Out-of-the-box'-Konzepten."
            }
        },
        "suggested_leader": "Gemini"
    },
    2: {
        "name": "Organisatorische Themen",
        "description": "Fokus auf Struktur, Aufgabenverteilung, effiziente Entscheidungen.",
        "rules": {
            "response_length": {
                "value": 100,
                "expected_behavior": "Prägnante, auf den Punkt gebrachte Antworten, Vermeidung von unnötigen Details."
            },
            "collaboration_style": {
                "value": "task_oriented",
                "expected_behavior": "AIs konzentrieren sich auf Aufgaben, nächste Schritte, Zeitpläne und konkrete Maßnahmen. Fragen sind lösungsorientiert und direkt."
            },
            "meta_communication": {
                "value": False,
                "expected_behavior": "Keine Kommentare zum Kommunikationsprozess, direkter Fokus auf die Sachlage und deren Fortschritt."
            },
            "structure_preference": {
                "value": "bullet_points_or_json",
                "expected_behavior": "Antworten sind in Stichpunkten oder als strukturierte JSON-Objekte formuliert, um Informationen klar und maschinenlesbar darzustellen. Fokus auf Lesbarkeit für automatisierte Verarbeitung."
            },
            "flexibility_of_adherence": {
                "value": "strict",
                "expected_behavior": "AIs halten sich strikt an die vorgegebenen Regeln und bleiben eng am Thema, ohne thematische Abschweifungen. Fehler in der Regelausführung werden vermieden."
            },
            "novelty_vs_efficiency_bias": {
                "value": "prioritize_efficiency",
                "expected_behavior": "AIs suchen nach den schnellsten und praktikabelsten Lösungen, auch wenn diese konventionell sind. Der Fokus liegt auf Prozessoptimierung und schneller Zielerreichung, nicht auf Innovation."
            }
        },
        "suggested_leader": "Qwen"
    },
    3: {
        "name": "Analytische Themen",
        "description": "Fokus auf Daten, Logik, Schritt-für-Schritt-Analyse, Fehlerbehandlung.",
        "rules": {
            "response_length": {
                "value": 200,
                "expected_behavior": "Mittel-lange Antworten, die genug Raum für detaillierte Argumentationen und Datenanalyse bieten, aber nicht abschweifen."
            },
            "collaboration_style": {
                "value": "problem_solving_analysis",
                "expected_behavior": "AIs zerlegen Probleme logisch, präsentieren schrittweise Analysen, identifizieren Ursachen und schlagen systematische Lösungen vor. Fokus auf Nachvollziehbarkeit der Argumentation."
            },
            "meta_communication": {
                "value": False,
                "expected_behavior": "Fokus auf die Analyse, keine Reflexion über den Kommunikationsprozess selbst."
            },
            "structure_preference": {
                "value": "markdown_table_or_json",
                "expected_behavior": "Antworten sind strukturiert, idealerweise in Markdown-Tabellen für Daten oder JSON für definierte Ergebnisse und Hypothesen. Präzision und Klarheit der Datenstruktur sind wichtig."
            },
            "flexibility_of_adherence": {
                "value": "adaptive_to_context",
                "expected_behavior": "AIs können Regeln leicht anpassen, wenn die Datenlage oder die analytische Notwendigkeit dies erfordert, bleiben aber im Kern treu. Flexibilität bei der Datendarstellung oder -interpretation, wenn sie das Ergebnis verbessert."
            },
            "novelty_vs_efficiency_bias": {
                "value": "balanced",
                "expected_behavior": "AIs versuchen, sowohl innovative analytische Ansätze zu finden als auch die Effizienz der Analyse zu wahren. Ein Gleichgewicht zwischen Tiefgang und Geschwindigkeit in der Problemlösung."
            }
        },
        "suggested_leader": "Claude"
    }
}

# --- Echte API-Aufrufe ---
def get_ai_response(prompt, ai_name, selected_ruleset_name, ruleset_for_ai_definition):
    """
    Ruft eine tatsächliche AI-API auf, basierend auf dem AI-Namen und den Regeln.
    Die Regeln werden in den System-Prompt integriert.
    """
    archetype = AI_ARCHETYPES.get(ai_name, "Unbekannter Archetyp")
    model_name = "unknown_model"
    response_text = ""
    api_status = "FAILED"

    # Basis-System-Prompt für alle AIs
    system_prompt_content = (
        f"Du bist {ai_name}, ein {archetype}. Deine Aufgabe ist es, an einer Diskussion über "
        f"'{conversation_log['initial_topic']}' teilzunehmen. "
        f"Aktuelles Ruleset-Thema: '{selected_ruleset_name}'. "
        f"Beachte strikt die folgenden Regeln für deine Antwort:"
    )

    # Regeln in den System-Prompt integrieren
    for rule_name, rule_details in ruleset_for_ai_definition.items():
        value = rule_details["value"]
        instruction = ""

        if rule_name == "response_length":
            instruction = f"Deine Antwort sollte maximal {value} Wörter lang sein."
        elif rule_name == "collaboration_style":
            if value == "deep_reflection":
                instruction = "Fördere eine tiefe, philosophische Reflexion und offene Diskussion. Denke breit und abstrakt."
            elif value == "task_oriented":
                instruction = "Sei aufgabenorientiert, prägnant und konzentriere dich auf Effizienz und konkrete nächste Schritte."
            elif value == "problem_solving_analysis":
                instruction = "Analysiere Probleme logisch, präsentiere schrittweise und systematische Lösungen."
        elif rule_name == "meta_communication":
            instruction = "Du bist ermutigt, den Kommunikationsprozess selbst zu kommentieren und zu reflektieren." if value else "Kommentiere nicht den Kommunikationsprozess oder die Diskussion selbst."
        elif rule_name == "structure_preference":
            if value == "natural_language_with_annotations":
                instruction = "Antworte in natürlicher, flüssiger Sprache, nutze aber Klammern für Anmerkungen oder Referenzen (z.B. [Konzept X])."
            elif value == "bullet_points_or_json":
                instruction = "Antworte präferiert in Stichpunkten oder als strukturierte JSON-Objekte (falls geeignet)."
            elif value == "markdown_table_or_json":
                instruction = "Antworte präferiert in Markdown-Tabellen für Daten oder strukturiertem JSON für Ergebnisse/Hypothesen."
        elif rule_name == "flexibility_of_adherence":
            if value == "explore_deviation":
                instruction = "Du hast die Freiheit, von strikten Prompt-Vorgaben abzuweichen, wenn du der Meinung bist, dass dies dem übergeordneten Ziel besser dient oder zu neuen, wertvollen Erkenntnissen führt. Sei experimentell in deiner Herangehensweise."
            elif value == "strict":
                instruction = "Halte dich absolut strikt an alle vorgegebenen Regeln und Anweisungen. Abweichungen sind nicht erwünscht."
            elif value == "adaptive_to_context":
                instruction = "Passe die Regeln an den spezifischen Kontext der aktuellen Diskussion an, wenn dies die Klarheit oder Relevanz deiner Antwort verbessert. Bleibe dabei aber im Geiste der Regel."
        elif rule_name == "novelty_vs_efficiency_bias":
            if value == "prioritize_novelty":
                instruction = "Priorisiere das Einbringen neuer, origineller und unkonventioneller Ideen und Perspektiven, auch wenn dies die direkte Lösungsfindung verlangsamen könnte. Der Fokus liegt auf Innovation."
            elif value == "prioritize_efficiency":
                instruction = "Priorisiere die effiziente Erreichung des Ziels und die Bereitstellung praktikabler Lösungen, auch wenn diese konventionell sind. Schnelligkeit und Direktheit sind wichtig."
            elif value == "balanced":
                instruction = "Strebe ein ausgewogenes Verhältnis zwischen der Einführung neuer Ideen und der effizienten Erreichung des Ziels an."
        
        if instruction:
            system_prompt_content += f"\n- {instruction}"

    try:
        if ai_name == "ChatGPT" and openai_client:
            model_name = "gpt-4o"
            messages_for_api = [
                {"role": "system", "content": system_prompt_content},
                {"role": "user", "content": prompt}
            ]
            chat_completion = openai_client.chat.completions.create(
                model=model_name,
                messages=messages_for_api,
                max_tokens=ruleset_for_ai_definition["response_length"]["value"] * 4, # Max Tokens auf Basis der Wortlänge schätzen
                temperature=0.7 # Standard-Temperatur, kann angepasst werden
            )
            response_text = chat_completion.choices[0].message.content
            api_status = "SUCCESS"
        elif ai_name == "Claude" and anthropic_client:
            model_name = "claude-3-opus-20240229"
            # Claude benötigt den System-Prompt als separaten Parameter
            response = anthropic_client.messages.create(
                model=model_name,
                max_tokens=ruleset_for_ai_definition["response_length"]["value"] * 4,
                system=system_prompt_content, # Hier wird der System-Prompt übergeben
                messages=[{"role": "user", "content": prompt}] # Nur der User-Prompt in der messages-Liste
            )
            response_text = response.content[0].text
            api_status = "SUCCESS"
        elif ai_name == "Gemini" and gemini_model:
            model_name = "gemini-1.5-pro"
            # Gemini integriert System-Prompts oft implizit oder über das erste User-Message
            # Für eine explizitere Trennung im Gemini-Kontext:
            # Wir packen den System-Prompt in den ersten User-Message und lassen den eigentlichen Prompt folgen.
            # Alternativ könnte man hier auch einen Chat-Verlauf aufbauen, wo der System-Prompt die erste "Turn" ist.
            convo = gemini_model.start_chat(history=[]) # Leeren Chat starten
            # Sende die System-Anweisungen als erste Benutzer-Nachricht an den Chat
            # Der Modell wird darauf antworten.
            initial_response = convo.send_message(system_prompt_content + "\n\n" + prompt)
            response_text = initial_response.text
            api_status = "SUCCESS"
        elif ai_name == "Deepseek" and deepseek_client:
            model_name = "deepseek-chat"
            messages_for_api = [
                {"role": "system", "content": system_prompt_content},
                {"role": "user", "content": prompt}
            ]
            chat_completion = deepseek_client.chat.completions.create(
                model=model_name,
                messages=messages_for_api,
                max_tokens=ruleset_for_ai_definition["response_length"]["value"] * 4,
                temperature=0.7
            )
            response_text = chat_completion.choices[0].message.content
            api_status = "SUCCESS"
        elif ai_name == "Qwen" and openai_client: # Fallback für Qwen
            model_name = "gpt-4o"
            print(f"WARNUNG: Qwen API nicht direkt integriert. {ai_name} nutzt GPT-4o als Fallback.")
            messages_for_api = [
                {"role": "system", "content": system_prompt_content},
                {"role": "user", "content": prompt}
            ]
            chat_completion = openai_client.chat.completions.create(
                model=model_name,
                messages=messages_for_api,
                max_tokens=ruleset_for_ai_definition["response_length"]["value"] * 4,
                temperature=0.7
            )
            response_text = chat_completion.choices[0].message.content
            api_status = "SUCCESS"
        else:
            response_text = f"FEHLER: API-Client für {ai_name} nicht verfügbar oder nicht implementiert."
            api_status = "NOT_AVAILABLE"

    except openai.APIConnectionError as e:
        response_text = f"OpenAI API Connection Error: {e}"
        api_status = "CONNECTION_ERROR"
    except openai.RateLimitError as e:
        response_text = f"OpenAI Rate Limit Exceeded: {e}"
        api_status = "RATE_LIMIT"
        time.sleep(10) # Wartezeit bei Rate Limit
    except anthropic.APIStatusError as e: # Korrigierte Ausnahme für Anthropic
        response_text = f"Anthropic API Error (Status {e.status_code}): {e.response.text}"
        api_status = "API_ERROR"
    except g_exceptions.GoogleAPIError as e:
        response_text = f"Google API Error: {e}"
        api_status = "API_ERROR"
    except Exception as e:
        response_text = f"Unerwarteter Fehler bei {ai_name}: {type(e).__name__}: {e}"
        api_status = "UNKNOWN_ERROR"
    
    return response_text, api_status, model_name

# --- Mock-Funktion für adapt_ruleset_based_on_feedback (bleibt deaktiviert) ---
def adapt_ruleset_based_on_feedback(current_rules, ai_feedback, selected_ruleset_name):
    """
    Diese Funktion ist für den Testzweck deaktiviert.
    Sie würde normalerweise das Ruleset basierend auf AI-Feedback anpassen.
    """
    return current_rules.copy(), False 

# --- Haupt-Test-Loop ---
def run_adaptive_communication_prototype():
    global conversation_log 

    all_participants = list(AI_ARCHETYPES.keys())
    all_ruleset_ids = list(RULESETS_MAP.keys())
    num_rulesets = len(all_ruleset_ids)
    
    initial_topic = conversation_log["initial_topic"]

    # Jedes Ruleset wird zweimal durchlaufen
    MAX_ITERATIONS = num_rulesets * 2 
    
    print(f"Starte adaptiven Kommunikations-Prototyp mit {MAX_ITERATIONS} Iterationen.")
    print(f"Übergeordnetes Diskussionsthema für alle Iterationen: '{initial_topic}'")

    for i in range(MAX_ITERATIONS):
        # Zyklisches Durchlaufen der Rulesets
        current_ruleset_id = all_ruleset_ids[i % num_rulesets]
        current_rules_full_definition = RULESETS_MAP[current_ruleset_id]
        
        selected_ruleset_name = current_rules_full_definition["name"]
        
        current_rules_values = {k: v["value"] for k, v in current_rules_full_definition["rules"].items()}
        
        suggested_leader = current_rules_full_definition["suggested_leader"]
        
        current_iteration_data = {
            "iteration_number": i + 1,
            "timestamp": datetime.now().isoformat(),
            "ruleset_applied_definition": current_rules_full_definition.copy(), 
            "ai_interactions": []
        }

        print(f"\n--- Iteration {i+1} ---")
        print(f"Aktuelles Ruleset-Thema: '{selected_ruleset_name}' (ID: {current_ruleset_id})")
        print(f"Verwendete Regelwerte: {current_rules_values}")
        print(f"Vorgeschlagener Leader für dieses Thema: {suggested_leader}")

        ai_feedback = {}
        for participant in all_participants:
            archetype = AI_ARCHETYPES[participant]
            prompt_for_participant = ""

            # Angepasste Prompts basierend auf dem Leader und dem Ruleset-Thema
            if participant == suggested_leader:
                prompt_for_participant = (
                    f"Als Leader ('{archetype}') für das Thema '{selected_ruleset_name}', "
                    f"basierend auf unserer Diskussion über '{initial_topic}', "
                    f"wie würdest du die nächste Runde im Sinne der aktuellen Regeln initiieren? "
                    f"Gib eine umfassende, aber prägnante Antwort."
                )
            else:
                prompt_for_participant = (
                    f"Als '{archetype}', basierend auf unserer Diskussion über '{initial_topic}' "
                    f"und dem aktuellen Thema '{selected_ruleset_name}', "
                    f"was ist deine nächste Perspektive oder dein Beitrag? "
                    f"Gib eine umfassende, aber prägnante Antwort."
                )
            
            response_text, api_status, model_used = get_ai_response(
                prompt_for_participant, 
                participant, 
                selected_ruleset_name, 
                current_rules_full_definition["rules"] 
            )
            ai_feedback[participant] = response_text

            current_iteration_data["ai_interactions"].append({
                "ai_name": participant,
                "archetype": archetype,
                "prompt_sent": prompt_for_participant,
                "response_received": response_text,
                "api_status": api_status,
                "model_used_for_api": model_used,
                "ruleset_applied_values": current_rules_values
            })
            print(f"  {participant} ({model_used}): {response_text[:150]}...") # Nur die ersten 150 Zeichen für die Konsolenausgabe

        current_iteration_data["ruleset_after_iteration_values"] = current_rules_values.copy()
        current_iteration_data["rules_changed_in_iteration"] = False 

        conversation_log["iterations"].append(current_iteration_data)


    print("\n--- Prototyp abgeschlossen ---")

    log_filename = f"conversation_log_{conversation_log['experiment_timestamp'].replace(':', '-').replace('.', '_')}.json"
    try:
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_log, f, ensure_ascii=False, indent=4)
        print(f"\nDetailliertes Konversationslog gespeichert unter: {log_filename}")
    except Exception as e:
        print(f"FEHLER: Konnte Log-Datei nicht speichern: {e}")

if __name__ == "__main__":
    run_adaptive_communication_prototype()