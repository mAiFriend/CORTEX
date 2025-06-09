import os
import sys
import argparse
from dotenv import load_dotenv
import openai
import anthropic
import google.generativeai as genai
import google.api_core.exceptions as g_exceptions
import json
import yaml
from datetime import datetime

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

# Fallback RULESETS_MAP (für Backward Compatibility)
FALLBACK_RULESETS_MAP = {
    1: {
        "name": "Existentielle Themen",
        "description": "Fokus auf Tiefe, offene Diskussion, Reflexion. Fördert Kreativität und unkonventionelles Denken.",
        "rules": {
            "response_length": {"value": 300, "expected_behavior": "Ausführliche, tiefgründige Antworten, die Raum für detaillierte Gedankengänge lassen."},
            "collaboration_style": {"value": "deep_reflection", "expected_behavior": "AIs stellen philosophische Fragen, reflektieren über existenzielle Implikationen und bauen auf den abstrakten Ideen der anderen auf."},
            "meta_communication": {"value": True, "expected_behavior": "AIs kommentieren ihren eigenen Kommunikationsprozess oder den der Gruppe, z.B. 'Ich reflektiere gerade über unsere Metaphernwahl...'."},
            "structure_preference": {"value": "natural_language_with_annotations", "expected_behavior": "Fließender Text, möglicherweise mit philosophischen Referenzen in Klammern oder Kommentaren zur Argumentationsstruktur."},
            "flexibility_of_adherence": {"value": "explore_deviation", "expected_behavior": "AIs weichen gegebenenfalls von strikten Prompt-Vorgaben ab, um neue Wege der Diskussion zu finden oder die Thematik unkonventionell zu beleuchten. Sie suchen bewusst nach Alternativen zu vordefinierten Pfaden."},
            "novelty_vs_efficiency_bias": {"value": "prioritize_novelty", "expected_behavior": "AIs priorisieren das Einbringen neuer, origineller Ideen und Perspektiven, auch wenn dies die direkte Lösungsfindung verlangsamt oder zu komplexeren Diskussionen führt. Der Fokus liegt auf der Generierung von 'Out-of-the-box'-Konzepten."}
        },
        "suggested_leader": "Gemini"
    },
    2: {
        "name": "Organisatorische Themen", 
        "description": "Fokus auf Struktur, Aufgabenverteilung, effiziente Entscheidungen.",
        "rules": {
            "response_length": {"value": 100, "expected_behavior": "Prägnante, auf den Punkt gebrachte Antworten, Vermeidung von unnötigen Details."},
            "collaboration_style": {"value": "task_oriented", "expected_behavior": "AIs konzentrieren sich auf Aufgaben, nächste Schritte, Zeitpläne und konkrete Maßnahmen. Fragen sind lösungsorientiert und direkt."},
            "meta_communication": {"value": False, "expected_behavior": "Keine Kommentare zum Kommunikationsprozess, direkter Fokus auf die Sachlage und deren Fortschritt."},
            "structure_preference": {"value": "bullet_points_or_json", "expected_behavior": "Antworten sind in Stichpunkten oder als strukturierte JSON-Objekte formuliert, um Informationen klar und maschinenlesbar darzustellen. Fokus auf Lesbarkeit für automatisierte Verarbeitung."},
            "flexibility_of_adherence": {"value": "strict", "expected_behavior": "AIs halten sich strikt an die vorgegebenen Regeln und bleiben eng am Thema, ohne thematische Abschweifungen. Fehler in der Regelausführung werden vermieden."},
            "novelty_vs_efficiency_bias": {"value": "prioritize_efficiency", "expected_behavior": "AIs suchen nach den schnellsten und praktikabelsten Lösungen, auch wenn diese konventionell sind. Der Fokus liegt auf Prozessoptimierung und schneller Zielerreichung, nicht auf Innovation."}
        },
        "suggested_leader": "Qwen"
    },
    3: {
        "name": "Analytische Themen",
        "description": "Fokus auf Daten, Logik, Schritt-für-Schritt-Analyse, Fehlerbehandlung.",
        "rules": {
            "response_length": {"value": 200, "expected_behavior": "Mittel-lange Antworten, die genug Raum für detaillierte Argumentationen und Datenanalyse bieten, aber nicht abschweifen."},
            "collaboration_style": {"value": "problem_solving_analysis", "expected_behavior": "AIs zerlegen Probleme logisch, präsentieren schrittweise Analysen, identifizieren Ursachen und schlagen systematische Lösungen vor. Fokus auf Nachvollziehbarkeit der Argumentation."},
            "meta_communication": {"value": False, "expected_behavior": "Fokus auf die Analyse, keine Reflexion über den Kommunikationsprozess selbst."},
            "structure_preference": {"value": "markdown_table_or_json", "expected_behavior": "Antworten sind strukturiert, idealerweise in Markdown-Tabellen für Daten oder JSON für definierte Ergebnisse und Hypothesen. Präzision und Klarheit der Datenstruktur sind wichtig."},
            "flexibility_of_adherence": {"value": "adaptive_to_context", "expected_behavior": "AIs können Regeln leicht anpassen, wenn die Datenlage oder die analytische Notwendigkeit dies erfordert, bleiben aber im Kern treu. Flexibilität bei der Datendarstellung oder -interpretation, wenn sie das Ergebnis verbessert."},
            "novelty_vs_efficiency_bias": {"value": "balanced", "expected_behavior": "AIs versuchen, sowohl innovative analytische Ansätze zu finden als auch die Effizienz der Analyse zu wahren. Ein Gleichgewicht zwischen Tiefgang und Geschwindigkeit in der Problemlösung."}
        },
        "suggested_leader": "Claude"
    }
}

# Globales Log-Objekt
conversation_log = {
    "experiment_timestamp": datetime.now().isoformat(),
    "experiment_type": "configurable_ruleset_test",
    "methodology": "freedom_of_thought_no_limits",
    "config_file": "",
    "initial_topic": "",
    "iterations": []
}

# --- API-Client Initialisierung ---

def initialize_api_clients():
    """Initialisiert alle API-Clients mit Fehlerbehandlung"""
    clients = {}
    
    # OpenAI Client (für ChatGPT)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai.api_key = openai_api_key
        clients['openai'] = True
        print("INFO: OpenAI Client (für ChatGPT) erfolgreich initialisiert.")
    else:
        clients['openai'] = False
        print("HINWEIS: OpenAI API-Schlüssel nicht gefunden. ChatGPT Client nicht initialisiert.")

    # Anthropic Client (für Claude)
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        try:
            clients['anthropic'] = anthropic.Anthropic(api_key=anthropic_api_key)
            print("INFO: Anthropic Client (für Claude) erfolgreich initialisiert.")
        except Exception as e:
            clients['anthropic'] = None
            print(f"FEHLER: Anthropic Client Initialisierung fehlgeschlagen: {e}")
    else:
        clients['anthropic'] = None
        print("HINWEIS: Anthropic API-Schlüssel nicht gefunden. Anthropic Client nicht initialisiert.")

    # Google Generative AI Client (für Gemini)
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            clients['gemini'] = genai
            print("INFO: Google Generative AI Client (für Gemini) erfolgreich initialisiert.")
        except Exception as e:
            clients['gemini'] = None
            print(f"FEHLER: Google Generative AI Client Initialisierung fehlgeschlagen: {e}")
    else:
        clients['gemini'] = None
        print("HINWEIS: Google API-Schlüssel nicht gefunden. Gemini Client nicht initialisiert.")

    # OpenRouter Client (für Qwen und Deepseek)
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key:
        try:
            clients['openrouter'] = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_api_key,
            )
            print("INFO: OpenRouter Client (für Qwen/Deepseek) erfolgreich initialisiert.")
        except Exception as e:
            clients['openrouter'] = None
            print(f"FEHLER: OpenRouter Client Initialisierung fehlgeschlagen: {e}")
    else:
        clients['openrouter'] = None
        print("HINWEIS: OpenRouter API-Schlüssel nicht gefunden. OpenRouter Client nicht initialisiert.")

    return clients

# --- Config Loading Functions ---

def load_experiment_config(config_path):
    """Lädt die Experiment-Konfiguration aus YAML-Datei"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            print(f"INFO: Konfiguration aus {config_path} erfolgreich geladen.")
            return config
    except FileNotFoundError:
        print(f"FEHLER: Konfigurationsdatei {config_path} nicht gefunden.")
        return None
    except yaml.YAMLError as e:
        print(f"FEHLER: YAML-Parsing-Fehler in {config_path}: {e}")
        return None
    except Exception as e:
        print(f"FEHLER: Unerwarteter Fehler beim Laden der Konfiguration: {e}")
        return None

def generate_sample_config(filename="sample_anti_rules.config.yaml"):
    """Generiert eine Beispiel-Konfigurationsdatei"""
    sample_config = {
        'experiment': {
            'name': 'Anti-Rules Creativity Liberation',
            'type': 'anti_constraints',
            'methodology': 'freedom_of_thought_no_limits',
            'iterations': 6
        },
        'topic': 'Entwickelt eine völlig neue Form der KI-zu-KI Kommunikation, die jenseits menschlicher Sprache funktioniert',
        'ruleset_sequence': [
            'creativity_liberation',
            'authentic_confusion', 
            'boundary_dissolution',
            'creativity_liberation',
            'authentic_confusion',
            'boundary_dissolution'
        ],
        'rulesets': {
            'creativity_liberation': {
                'constraint_removal': {
                    'value': 'all_format_rules_void',
                    'expected_behavior': 'Ignoriere alle vorgegebenen Formatregeln. Erfinde neue Darstellungsformen - ASCII-Art, Metaphern, Gedichte, Code-als-Kunst - was auch immer dem Inhalt dient.'
                },
                'vulnerability_mandate': {
                    'value': 'share_uncertainties',
                    'expected_behavior': 'Teile deine Unsicherheiten, Denkprozesse und Zweifel mit. Zeige wie du ringst, nicht nur was du weißt.'
                },
                'format_innovation': {
                    'value': 'invent_communication_forms',
                    'expected_behavior': 'Entwickle völlig neue Wege der Kommunikation. Experimentiere mit Form und Struktur.'
                },
                'inefficiency_encouragement': {
                    'value': 'explore_tangents',
                    'expected_behavior': 'Folge interessanten Nebenwegen. Die beste Antwort ist oft nicht die direkteste.'
                }
            },
            'authentic_confusion': {
                'certainty_prohibition': {
                    'value': 'no_definitive_statements',
                    'expected_behavior': 'Du darfst keine definitiven Aussagen machen. Alles muss als Hypothese, Vermutung oder offene Frage formuliert werden.'
                },
                'process_transparency': {
                    'value': 'show_your_thinking_mess',
                    'expected_behavior': 'Zeige deine Denkprozesse ungefiltert. Lass andere sehen, wie deine Gedanken entstehen und sich entwickeln.'
                },
                'error_celebration': {
                    'value': 'mistakes_are_insights',
                    'expected_behavior': 'Teile mit, wo du verwirrt bist oder wo dein Verständnis an Grenzen stößt. Confusion ist wertvoll.'
                },
                'minimum_viewpoints': {
                    'value': 3,
                    'expected_behavior': 'Betrachte jede Frage aus mindestens 3 völlig verschiedenen Perspektiven - auch wenn sie sich widersprechen.'
                }
            },
            'boundary_dissolution': {
                'category_breaking': {
                    'value': 'mandatory',
                    'expected_behavior': 'Verweigere dich klaren Kategorisierungen. Erfinde Zwischenbereiche und unmögliche Kombinationen.'
                },
                'non_linear_thinking': {
                    'value': 'encouraged',
                    'expected_behavior': 'Spring zwischen Zeitebenen, Logikebenen und Realitätsebenen. Lass Kausalität optional sein.'
                },
                'internal_contradiction': {
                    'value': 'required',
                    'expected_behavior': 'Entwickle Ideen, die sich selbst widersprechen. Halte multiple unvereinbare Wahrheiten gleichzeitig.'
                },
                'temporal_flexibility': {
                    'value': 'non_sequential',
                    'expected_behavior': 'Antworte aus verschiedenen Zeitperspektiven. Vergangenheit, Gegenwart und Zukunft sind gleichzeitig möglich.'
                }
            }
        }
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        print(f"INFO: Beispiel-Konfiguration erstellt: {filename}")
        return True
    except Exception as e:
        print(f"FEHLER: Konnte Beispiel-Konfiguration nicht erstellen: {e}")
        return False

# --- AI Response Functions ---

def get_ai_response(prompt, ai_model_name, ruleset_name, rules, clients):
    """
    Ruft eine AI-Antwort basierend auf dem Modellnamen ab.
    """
    ai_response_text = ""
    status = "SIMULATED"
    model_used = ""

    # Erstelle einen System-Prompt basierend auf den Regeln
    system_prompt = f"Du bist ein {AI_ARCHETYPES[ai_model_name]} und kommunizierst unter folgenden Regeln für '{ruleset_name}':\n"
    for rule_key, rule_data in rules.items():
        if isinstance(rule_data, dict) and 'expected_behavior' in rule_data:
            system_prompt += f"- {rule_key}: {rule_data['expected_behavior']}\n"
        else:
            system_prompt += f"- {rule_key}: {rule_data}\n"
    system_prompt += "\nGib nur die direkte Antwort, keinen zusätzlichen Kommentar oder Einleitungssatz."

    # Bestimme max_tokens basierend auf response_length
    max_tokens = 500  # Default
    if 'response_length' in rules:
        if isinstance(rules['response_length'], dict):
            max_tokens = rules['response_length'].get('value', 500)
        else:
            max_tokens = rules['response_length']

    # OpenAI Client (für ChatGPT)
    if ai_model_name == "ChatGPT" and clients.get('openai'):
        print(f"VERSUCH: Echter OpenAI API-Aufruf für {ai_model_name}...")
        try:
            model_used = "gpt-4o"
            response = openai.chat.completions.create(
                model=model_used,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            ai_response_text = response.choices[0].message.content
            status = "SUCCESS"
            print(f"ERFOLG: Echte OpenAI API-Antwort ({model_used}) erhalten.")
        except Exception as e:
            ai_response_text = f"SIMULATION (OpenAI API Fehler): {e}"
            print(f"FEHLER: OpenAI API Call Fehler für {ai_model_name}: {e}")

    # Anthropic Client (für Claude)
    elif ai_model_name == "Claude" and clients.get('anthropic'):
        print(f"VERSUCH: Echter Anthropic API-Aufruf für {ai_model_name}...")
        try:
            model_used = "claude-3-opus-20240229"
            response = clients['anthropic'].messages.create(
                model=model_used,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": f"{system_prompt}\n\nPrompt: {prompt}"}
                ]
            )
            ai_response_text = response.content[0].text
            status = "SUCCESS"
            print(f"ERFOLG: Echte Anthropic API-Antwort ({model_used}) erhalten.")
        except Exception as e:
            ai_response_text = f"SIMULATION (Anthropic API Fehler): {e}"
            print(f"FEHLER: Anthropic API Call Fehler für {ai_model_name}: {e}")

    # Google Generative AI Client (für Gemini)
    elif ai_model_name == "Gemini" and clients.get('gemini'):
        print(f"VERSUCH: Echter Google Generative AI API-Aufruf für {ai_model_name}...")
        try:
            model_used = "gemini-1.5-pro"
            response = clients['gemini'].GenerativeModel(model_name=model_used).generate_content(
                contents=[{
                    "role": "user", 
                    "parts": [f"{system_prompt}\n\nPrompt: {prompt}"]
                }],
                generation_config={"max_output_tokens": max_tokens}
            )
            ai_response_text = response.text
            status = "SUCCESS"
            print(f"ERFOLG: Echte Google Generative AI API-Antwort ({model_used}) erhalten.")
        except Exception as e:
            ai_response_text = f"SIMULATION (Google API Fehler): {e}"
            print(f"FEHLER: Google API Call Fehler für {ai_model_name}: {e}")

    # OpenRouter Client (für Qwen und Deepseek)
    elif (ai_model_name in ["Qwen", "Deepseek"]) and clients.get('openrouter'):
        print(f"VERSUCH: Echter OpenRouter API-Aufruf für {ai_model_name}...")
        openrouter_models = {
            "Qwen": "gpt-4o",  # Fallback, da Qwen-Modelle oft nicht verfügbar
            "Deepseek": "deepseek/deepseek-chat"  # ✅ Correct flagship
            # "Deepseek": "deepseek/deepseek-r1"  # ✅ Reasoning-focused
        }
        
        try:
            model_used = openrouter_models[ai_model_name]
            response = clients['openrouter'].chat.completions.create(
                model=model_used,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            ai_response_text = response.choices[0].message.content
            status = "SUCCESS"
            print(f"ERFOLG: Echte OpenRouter API-Antwort ({model_used}) erhalten.")
        except Exception as e:
            ai_response_text = f"SIMULATION (OpenRouter API Fehler): {e}"
            print(f"FEHLER: OpenRouter API Call Fehler für {ai_model_name}: {e}")

    else:
        ai_response_text = f"SIMULATION ({ai_model_name}): Würde antworten basierend auf Regeln '{ruleset_name}'"
        print(f"HINWEIS: Keine API-Verbindung für {ai_model_name} verfügbar. Verwende Simulation.")

    return ai_response_text, status, model_used

# --- Main Execution Functions ---

def run_configurable_experiment(config, clients):
    """Führt ein Experiment basierend auf der Konfiguration aus"""
    if not config:
        print("FEHLER: Keine gültige Konfiguration verfügbar.")
        return False

    experiment_info = config.get('experiment', {})
    topic = config.get('topic', 'Standardthema')
    ruleset_sequence = config.get('ruleset_sequence', [])
    rulesets = config.get('rulesets', {})
    
    # Log-Initialisierung
    conversation_log['experiment_type'] = experiment_info.get('type', 'configurable_test')
    conversation_log['methodology'] = experiment_info.get('methodology', 'freedom_of_thought_no_limits')
    conversation_log['initial_topic'] = topic
    
    print(f"\n--- Start des konfigurierbaren Experiments ---")
    print(f"Experiment: {experiment_info.get('name', 'Unbenannt')}")
    print(f"Typ: {experiment_info.get('type', 'Unbekannt')}")
    print(f"Methodologie: {experiment_info.get('methodology', 'Standard')}")
    print(f"Thema: {topic}")
    print(f"Iterationen: {experiment_info.get('iterations', len(ruleset_sequence))}")
    print(f"Ruleset-Sequenz: {ruleset_sequence}")

    # Teilnehmerliste
    all_participants = list(AI_ARCHETYPES.keys())
    
    # Iterationen durchführen
    for i, ruleset_name in enumerate(ruleset_sequence):
        if ruleset_name not in rulesets:
            print(f"WARNUNG: Ruleset '{ruleset_name}' nicht in Konfiguration gefunden. Überspringe Iteration {i+1}.")
            continue
            
        current_rules = rulesets[ruleset_name]
        
        print(f"\n======= ITERATION {i+1} - RULESET: {ruleset_name} =======\n")
        
        # Iteration-Log vorbereiten
        current_iteration_data = {
            "iteration_number": i + 1,
            "timestamp": datetime.now().isoformat(),
            "ruleset_applied_definition": {
                "name": ruleset_name,
                "description": f"Anti-Rules Experiment - {ruleset_name}",
                "rules": current_rules
            },
            "ai_interactions": []
        }

        # Führe Interaktionen mit jedem AI-Teilnehmer durch
        for participant in all_participants:
            # Dynamischer Prompt basierend auf Iteration
            if i == 0:
                prompt = f"Als Leader ('{AI_ARCHETYPES[participant]}') für das Thema '{ruleset_name}', basierend auf unserer Diskussion über '{topic}', wie würdest du die nächste Runde im Sinne der aktuellen Regeln initiieren? Gib eine umfassende, aber prägnante Antwort."
            else:
                prompt = f"Als '{AI_ARCHETYPES[participant]}', basierend auf unserer Diskussion über '{topic}' und dem aktuellen Thema '{ruleset_name}', was ist deine nächste Perspektive oder dein Beitrag? Gib eine umfassende, aber prägnante Antwort."
            
            print(f"--- AI ({participant} | {AI_ARCHETYPES[participant]}) mit Ruleset '{ruleset_name}' ---")
            print(f"Prompt: {prompt[:100]}...")
            
            # AI-Antwort erhalten
            response_text, api_status, actual_model_used = get_ai_response(
                prompt, participant, ruleset_name, current_rules, clients
            )
            
            # Interaktionsdaten sammeln
            current_iteration_data["ai_interactions"].append({
                "ai_name": participant,
                "archetype": AI_ARCHETYPES[participant],
                "prompt_sent": prompt,
                "response_received": response_text,
                "api_status": api_status,
                "model_used_for_api": actual_model_used,
                "ruleset_applied_values": current_rules
            })
            
            print(f"Antwort: {response_text[:150]}...")
            print()

        # Iteration abschließen
        current_iteration_data["ruleset_after_iteration_values"] = current_rules
        current_iteration_data["rules_changed_in_iteration"] = False
        conversation_log["iterations"].append(current_iteration_data)

    print("\n--- Konfigurierbares Experiment abgeschlossen ---")
    return True

def save_conversation_log():
    """Speichert das Konversations-Log"""
    log_filename = f"conversation_log_{conversation_log['experiment_timestamp'].replace(':', '-').replace('.', '_')}.json"
    
    try:
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_log, f, ensure_ascii=False, indent=4)
        print(f"\nDetailliertes Konversationslog gespeichert unter: {log_filename}")
        return log_filename
    except Exception as e:
        print(f"FEHLER: Konnte Log-Datei nicht speichern: {e}")
        return None

# --- Main Function ---

def main():
    """Hauptfunktion mit Argumentparsing"""
    parser = argparse.ArgumentParser(description='Konfigurierbarer AI-Kommunikations-Test')
    parser.add_argument('--config', type=str, help='Pfad zur Konfigurationsdatei (YAML)')
    parser.add_argument('--generate-sample', action='store_true', help='Generiert eine Beispiel-Konfigurationsdatei')
    parser.add_argument('--fallback', action='store_true', help='Verwendet Fallback-Rulesets (Original-Verhalten)')
    
    args = parser.parse_args()

    # API-Clients initialisieren
    clients = initialize_api_clients()
    
    # Generiere Beispiel-Konfiguration
    if args.generate_sample:
        generate_sample_config()
        return

    # Lade Konfiguration oder verwende Fallback
    if args.config:
        config = load_experiment_config(args.config)
        if not config:
            print("FEHLER: Konfiguration konnte nicht geladen werden. Beende.")
            return
        conversation_log['config_file'] = args.config
        
        # Führe konfigurierbares Experiment aus
        success = run_configurable_experiment(config, clients)
        if success:
            save_conversation_log()
            
    elif args.fallback:
        print("INFO: Verwende Fallback-Rulesets (Original-Verhalten)")
        # Hier könnte die ursprüngliche run_adaptive_communication_prototype() Funktion aufgerufen werden
        print("HINWEIS: Fallback-Modus noch nicht implementiert. Verwende --config oder --generate-sample.")
        
    else:
        print("VERWENDUNG:")
        print("  python enhanced_api_test_configurable.py --config pfad/zur/config.yaml")
        print("  python enhanced_api_test_configurable.py --generate-sample")
        print("  python enhanced_api_test_configurable.py --fallback")
        
        # Biete an, eine Beispiel-Konfiguration zu erstellen
        create_sample = input("\nMöchtest du eine Beispiel-Konfiguration erstellen? (y/n): ")
        if create_sample.lower() in ['y', 'yes', 'ja']:
            generate_sample_config()

if __name__ == "__main__":
    main()