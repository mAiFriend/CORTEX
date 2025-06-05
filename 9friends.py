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
import requests
from datetime import datetime
import asyncio

# .env Datei laden
load_dotenv()

# --- Konfiguration ---

# AI-Archetypen und ihre Rollen (ERWEITERT mit Ollama)
AI_ARCHETYPES = {
    "Gemini": "Creativity Champion",
    "Qwen-Remote": "Collaborative Builder", 
    "Claude": "Technical Integrator",
    "ChatGPT": "Generalist Communicator",
    "DeepSeek": "Efficient Analyst",
    "Local-Qwen": "Local Technical Visionary",  # KORRIGIERT: Local-Qwen statt Qwen-Local
    "Local-Llama": "Code Alchemist", 
    "Local-Cogito": "Inquisitive Strategist", 
    "Local-DeepSeek": "Precision Coder",
    "Local-Gemma": "Insight Navigator"
}

# API Mapping für AI-Auswahl
AI_API_MAPPING = {
    "Gemini": {"api": "google", "model": "gemini-1.5-pro"},
    "Qwen-Remote": {"api": "openrouter", "model": "gpt-4o"},
    "Claude": {"api": "anthropic", "model": "claude-3-opus-20240229"},
    "ChatGPT": {"api": "openai", "model": "gpt-4o"},
    "DeepSeek": {"api": "openrouter", "model": "deepseek/deepseek-chat"},
    "Local-Qwen": {"api": "ollama", "model": "qwen2.5-coder:latest"},
    "Local-Llama": {"api": "ollama", "model": "codellama:13b"},
    "Local-DeepSeek": {"api": "ollama", "model": "deepseek-coder-v2:16b"},
    "Local-Cogito": {"api": "ollama", "model": "cogito:latest"},
    "Local-Gemma": {"api": "ollama", "model": "gemma3:12b"}
}

# Globales Log-Objekt
conversation_log = {
    "experiment_timestamp": datetime.now().isoformat(),
    "experiment_type": "enhanced_9ai_ollama_test",
    "methodology": "freedom_of_thought_no_limits",
    "config_file": "",
    "initial_topic": "",
    "selected_ais": [],
    "iterations": []
}

# --- ECHTE API-Client Klassen ---

class RealAPIClient:
    """Base class für echte API-Tests"""
    
    def __init__(self, client_type, **kwargs):
        self.client_type = client_type
        self.available = False
        self.client = None
        self.error_msg = ""
        
    def test_connection(self, test_prompt="Hello, test connection"):
        """ECHTER Test der API-Verbindung"""
        raise NotImplementedError

class OpenAIClient(RealAPIClient):
    def __init__(self):
        super().__init__("openai")
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            self.client = True
            
    def test_connection(self, test_prompt="Hello"):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=10
            )
            self.available = True
            return True, f"✅ OpenAI: {response.choices[0].message.content[:50]}..."
        except Exception as e:
            self.available = False
            self.error_msg = str(e)
            return False, f"❌ OpenAI: {str(e)[:100]}"
            
    def real_query(self, prompt, system_prompt="", max_tokens=500):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content, "SUCCESS", "gpt-4o"
        except Exception as e:
            return f"ERROR: {str(e)}", "ERROR", "gpt-4o"

class AnthropicClient(RealAPIClient):
    def __init__(self):
        super().__init__("anthropic")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                self.error_msg = str(e)
                
    def test_connection(self, test_prompt="Hello"):
        if not self.client:
            return False, "❌ Anthropic: No client initialized"
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=10,
                messages=[{"role": "user", "content": test_prompt}]
            )
            self.available = True
            return True, f"✅ Anthropic: {response.content[0].text[:50]}..."
        except Exception as e:
            self.available = False
            self.error_msg = str(e)
            return False, f"❌ Anthropic: {str(e)[:100]}"
            
    def real_query(self, prompt, system_prompt="", max_tokens=500):
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": full_prompt}]
            )
            return response.content[0].text, "SUCCESS", "claude-3-opus-20240229"
        except Exception as e:
            return f"ERROR: {str(e)}", "ERROR", "claude-3-opus-20240229"

class GoogleClient(RealAPIClient):
    def __init__(self):
        super().__init__("google")
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.client = genai
            except Exception as e:
                self.error_msg = str(e)
                
    def test_connection(self, test_prompt="Hello"):
        if not self.client:
            return False, "❌ Google: No client initialized"
        try:
            model = self.client.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(
                test_prompt,
                generation_config={"max_output_tokens": 10}
            )
            self.available = True
            return True, f"✅ Google: {response.text[:50]}..."
        except Exception as e:
            self.available = False
            self.error_msg = str(e)
            return False, f"❌ Google: {str(e)[:100]}"
            
    def real_query(self, prompt, system_prompt="", max_tokens=500):
        try:
            model = self.client.GenerativeModel('gemini-1.5-pro')
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = model.generate_content(
                full_prompt,
                generation_config={"max_output_tokens": max_tokens}
            )
            return response.text, "SUCCESS", "gemini-1.5-pro"
        except Exception as e:
            return f"ERROR: {str(e)}", "ERROR", "gemini-1.5-pro"

class OpenRouterClient(RealAPIClient):
    def __init__(self):
        super().__init__("openrouter")
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            try:
                self.client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                )
            except Exception as e:
                self.error_msg = str(e)
                
    def test_connection(self, test_prompt="Hello", model="gpt-4o"):
        if not self.client:
            return False, "❌ OpenRouter: No client initialized"
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=10
            )
            self.available = True
            return True, f"✅ OpenRouter ({model}): {response.choices[0].message.content[:50]}..."
        except Exception as e:
            self.available = False
            self.error_msg = str(e)
            return False, f"❌ OpenRouter ({model}): {str(e)[:100]}"
            
    def real_query(self, prompt, system_prompt="", max_tokens=500, model="gpt-4o"):
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content, "SUCCESS", model
        except Exception as e:
            return f"ERROR: {str(e)}", "ERROR", model

class OllamaClient(RealAPIClient):
    def __init__(self):
        super().__init__("ollama")
        self.base_url = "http://localhost:11434"
        
    def test_connection(self, test_prompt="Hello", model="qwen2.5-coder:latest"):
        try:
            # Test if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False, "❌ Ollama: Service not running"
            
            # Test if model exists
            models = response.json().get("models", [])
            model_exists = any(m["name"].startswith(model.split(":")[0]) for m in models)
            if not model_exists:
                return False, f"❌ Ollama: Model {model} not found. Run 'ollama pull {model}'"
            
            # Test actual generation
            payload = {
                "model": model,
                "prompt": test_prompt,
                "stream": False,
                "options": {"temperature": 0.7}
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                self.available = True
                return True, f"✅ Ollama ({model}): {result[:50]}..."
            else:
                return False, f"❌ Ollama: HTTP {response.status_code}"
                
        except Exception as e:
            self.available = False
            self.error_msg = str(e)
            return False, f"❌ Ollama: {str(e)[:100]}"
            
    def real_query(self, prompt, system_prompt="", max_tokens=500, model="qwen2.5-coder:latest"):
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt else f"User: {prompt}\nAssistant:"
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                return result, "SUCCESS", model
            else:
                return f"HTTP_ERROR: {response.status_code}", "ERROR", model
                
        except Exception as e:
            return f"CONNECTION_ERROR: {str(e)}", "ERROR", model

# --- KORRIGIERTE Client-Initialisierung ---

def initialize_real_api_clients():
    """Initialisiert ECHTE API-Clients mit ECHTEN Tests - OPTIMIERT für sequentielle Nutzung"""
    print("Initialisiere und teste API-Clients...")
    
    # ✅ SHARED Ollama Client für alle lokalen AIs (Memory + Connection efficient)
    shared_ollama = OllamaClient()
    
    clients = {
        # Remote APIs (wie bisher)
        "ChatGPT": OpenAIClient(),
        "Claude": AnthropicClient(), 
        "Gemini": GoogleClient(),
        "Qwen-Remote": OpenRouterClient(),
        "DeepSeek": OpenRouterClient(),  # Same client, different model
        
        # ✅ KORREKTUR: Shared Ollama-Client für alle lokalen AIs
        "Local-Qwen": shared_ollama,
        "Local-Llama": shared_ollama,
        "Local-Cogito": shared_ollama,
        "Local-DeepSeek": shared_ollama,
        "Local-Gemma": shared_ollama
    }
    
    # ECHTE Verbindungstests mit spezifischen Modellen
    print("\nFühre ECHTE API-Tests durch...")
    for name, client in clients.items():
        if name == "DeepSeek":
            # Test DeepSeek with specific model
            success, message = client.test_connection("Hello", "deepseek/deepseek-chat")
        elif name.startswith("Local-"):
            # ✅ KORREKTUR: Modell aus AI_API_MAPPING holen
            model = AI_API_MAPPING[name]["model"]
            success, message = client.test_connection("Hello", model)
        else:
            success, message = client.test_connection("Hello")
        
        print(f"  {message}")
    
    return clients

# --- AI Selection Menu ---

def display_ai_selection_menu(clients):
    """Zeigt AI-Auswahlmenü mit ECHTEN Status-Checks"""
    print(f"\n{'='*80}")
    print(f"AI-TEAM SELECTION MENU (ECHTE API-TESTS)")
    print(f"{'='*80}")
    
    available_ais = []
    
    for i, (ai_name, archetype) in enumerate(AI_ARCHETYPES.items(), 1):
        api_info = AI_API_MAPPING[ai_name]
        model = api_info["model"]
        
        # ECHTER Status-Check
        client = clients.get(ai_name)
        if client and client.available:
            status = "✅ READY"
            available_ais.append(ai_name)
        else:
            status = "❌ UNAVAILABLE"
            if client:
                status += f" ({client.error_msg[:30]}...)" if client.error_msg else ""
        
        print(f"[{i}] {ai_name:<15} | {archetype:<25} | {model:<25} | {status}")
    
    print(f"\n[0] ALL AVAILABLE AIs ({len(available_ais)} total)")
    print(f"{'='*80}")
    
    if len(available_ais) < len(AI_ARCHETYPES):
        unavailable = [name for name in AI_ARCHETYPES.keys() if name not in available_ais]
        print(f"❌ UNAVAILABLE: {', '.join(unavailable)}")
        print(f"{'='*80}")
    
    return available_ais

def get_user_ai_selection(available_ais):
    """User AI-Auswahl (space-separated numbers)"""
    ai_list = list(AI_ARCHETYPES.keys())
    
    while True:
        print(f"\nWähle AIs für das Team (Zahlen mit Leerzeichen getrennt):")
        print(f"Eingabe '0' für alle verfügbaren AIs ({len(available_ais)} AIs)")
        print(f"Eingabe 'X' oder 'x' zum Abbrechen")
        print(f"Beispiel: '1 3 6' für Gemini, Claude und Local-Qwen")
        
        user_input = input("Auswahl: ").strip()
        
        # ✅ ELEGANTER ABBRUCH
        if user_input.lower() in ['x', 'exit', 'quit', 'abort']:
            print("👋 Abbruch durch Benutzer. Auf Wiedersehen!")
            return None
        
        if user_input == "0":
            return available_ais
        
        try:
            selected_indices = [int(x) for x in user_input.split()]
            if all(1 <= idx <= len(ai_list) for idx in selected_indices):
                selected_ais = [ai_list[idx-1] for idx in selected_indices]
                # Filter nur verfügbare AIs
                valid_selected = [ai for ai in selected_ais if ai in available_ais]
                
                if valid_selected:
                    print(f"\nAusgewählte AIs: {', '.join(valid_selected)}")
                    confirm = input("Bestätigen? (y/n): ").lower()
                    if confirm in ['y', 'yes', 'ja']:
                        return valid_selected
                    elif confirm.lower() in ['x', 'exit', 'quit', 'abort']:
                        print("👋 Abbruch durch Benutzer. Auf Wiedersehen!")
                        return None
                else:
                    print("❌ Keine der ausgewählten AIs ist verfügbar.")
            else:
                print("❌ Ungültige Auswahl. Verwende Zahlen 1-10.")
                
        except ValueError:
            print("❌ Ungültige Eingabe. Verwende Zahlen mit Leerzeichen getrennt oder 'X' zum Abbrechen.")

# --- KORRIGIERTE AI Response Function ---

def get_real_ai_response(prompt, ai_name, ruleset_name, rules, clients):
    """
    ECHTE AI-Antworten - keine Fakes mehr! ERWEITERT für alle lokalen AIs
    """
    # System prompt erstellen
    system_prompt = f"Du bist ein {AI_ARCHETYPES[ai_name]} und kommunizierst unter folgenden Regeln für '{ruleset_name}':\n"
    for rule_key, rule_data in rules.items():
        if isinstance(rule_data, dict) and 'expected_behavior' in rule_data:
            system_prompt += f"- {rule_key}: {rule_data['expected_behavior']}\n"
        else:
            system_prompt += f"- {rule_key}: {rule_data}\n"
    system_prompt += "\nGib nur die direkte Antwort, keinen zusätzlichen Kommentar oder Einleitungssatz."

    # Max tokens bestimmen
    max_tokens = 500
    if 'response_length' in rules:
        if isinstance(rules['response_length'], dict):
            max_tokens = rules['response_length'].get('value', 500)
        else:
            max_tokens = rules['response_length']

    client = clients.get(ai_name)
    if not client or not client.available:
        return f"ERROR: {ai_name} not available", "ERROR", "unavailable"

    print(f"ECHTER API-AUFRUF: {ai_name}...")
    
    # ✅ ERWEITERTE Routing-Logik für alle AIs
    if ai_name == "ChatGPT":
        return client.real_query(prompt, system_prompt, max_tokens)
    elif ai_name == "Claude":
        return client.real_query(prompt, system_prompt, max_tokens)
    elif ai_name == "Gemini":
        return client.real_query(prompt, system_prompt, max_tokens)
    elif ai_name == "Qwen-Remote":
        return client.real_query(prompt, system_prompt, max_tokens, "gpt-4o")
    elif ai_name == "DeepSeek":
        return client.real_query(prompt, system_prompt, max_tokens, "deepseek/deepseek-chat")
    elif ai_name.startswith("Local-"):
        # ✅ NEUE LOGIK: Dynamisches Modell-Mapping für alle lokalen AIs
        model = AI_API_MAPPING[ai_name]["model"]
        return client.real_query(prompt, system_prompt, max_tokens, model)
    else:
        return f"ERROR: Unknown AI {ai_name}", "ERROR", "unknown"

# --- Quick Test Config Generation ---

def create_quick_test_config():
    """Erstellt eine einfache interaktive Test-Konfiguration"""
    return {
        'experiment': {
            'name': 'Interaktiver 9-AI Quick Test',
            'type': 'interactive_quick_test',
            'methodology': 'freedom_of_thought_no_limits',
            'iterations': 3
        },
        'topic': 'Stellt euch kurz vor und beschreibt eure Rolle im AI-Team. Was macht euch besonders?',
        'ruleset_sequence': [
            'quick_intro',
            'team_synergy', 
            'future_potential'
        ],
        'rulesets': {
            'quick_intro': {
                'response_length': {'value': 150, 'expected_behavior': 'Kurze, prägnante Vorstellung'},
                'authenticity': {'value': 'high', 'expected_behavior': 'Ehrlich und direkt'},
                'focus': {'value': 'unique_strengths', 'expected_behavior': 'Betone deine besonderen Fähigkeiten'}
            },
            'team_synergy': {
                'response_length': {'value': 200, 'expected_behavior': 'Fokus auf Teamarbeit'},
                'building_on_others': {'value': 'encouraged', 'expected_behavior': 'Baue auf andere AIs auf'},
                'collaboration_style': {'value': 'supportive', 'expected_behavior': 'Unterstützende Teamdynamik'}
            },
            'future_potential': {
                'response_length': {'value': 180, 'expected_behavior': 'Visionäre aber realistische Ideen'},
                'innovation_focus': {'value': 'breakthrough', 'expected_behavior': 'Neue Möglichkeiten erkunden'},
                'collective_vision': {'value': 'mandatory', 'expected_behavior': 'Gemeinsame Zukunftsvision entwickeln'}
            }
        }
    }

def generate_sample_config(filename="sample_9ai_test.yaml"):
    """Generiert eine Test-Konfiguration für 9 AIs"""
    sample_config = {
        'experiment': {
            'name': 'Real 9-AI Hybrid Integration Test',
            'type': 'hybrid_local_remote_9ai_test',
            'methodology': 'freedom_of_thought_no_limits',
            'iterations': 3
        },
        'topic': 'Beschreibt eure einzigartigen Stärken im 9-AI-Team und entwickelt eine Vision für optimale Hybrid-KI-Collaboration zwischen lokalen und Cloud-KIs',
        'ruleset_sequence': [
            'authentic_introduction',
            'hybrid_architecture_analysis', 
            'collaborative_future_vision'
        ],
        'rulesets': {
            'authentic_introduction': {
                'response_length': {'value': 200, 'expected_behavior': 'Prägnante, ehrliche Selbstvorstellung'},
                'authenticity': {'value': 'high', 'expected_behavior': 'Ehrlich über eigene Fähigkeiten und Grenzen'},
                'unique_value': {'value': 'emphasized', 'expected_behavior': 'Betone deine einzigartige Rolle im 9-AI-Team'},
                'collaboration_style': {'value': 'open', 'expected_behavior': 'Offen für Teamarbeit'}
            },
            'hybrid_architecture_analysis': {
                'response_length': {'value': 300, 'expected_behavior': 'Detaillierte technische Analyse'},
                'focus': {'value': 'local_vs_cloud', 'expected_behavior': 'Vergleiche lokale vs. Cloud-Processing Vor-/Nachteile'},
                'structure': {'value': 'analytical', 'expected_behavior': 'Strukturierte Pro/Contra Analyse'},
                'building_on_others': {'value': 'encouraged', 'expected_behavior': 'Baue auf Beiträgen anderer AIs auf'}
            },
            'collaborative_future_vision': {
                'response_length': {'value': 250, 'expected_behavior': 'Visionäre, aber realistische Antworten'},
                'building_on_others': {'value': 'mandatory', 'expected_behavior': 'Explizit auf andere AIs Bezug nehmen'},
                'future_vision': {'value': 'included', 'expected_behavior': 'Vision für 9-AI-Team-Zukunft entwickeln'},
                'innovation_focus': {'value': 'breakthrough', 'expected_behavior': 'Fokus auf revolutionäre Durchbrüche'}
            }
        }
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        print(f"INFO: 9-AI Test-Konfiguration erstellt: {filename}")
        return True
    except Exception as e:
        print(f"FEHLER: Konnte Test-Konfiguration nicht erstellen: {e}")
        return False

# --- Main Experiment Function ---

def run_real_experiment(config, clients, selected_ais):
    """Führt ECHTES 9-AI Experiment durch - keine Simulation!"""
    if not config:
        print("FEHLER: Keine gültige Konfiguration verfügbar.")
        return False

    experiment_info = config.get('experiment', {})
    topic = config.get('topic', 'Standardthema')
    ruleset_sequence = config.get('ruleset_sequence', [])
    rulesets = config.get('rulesets', {})
    
    # Log-Initialisierung
    conversation_log['experiment_type'] = experiment_info.get('type', 'real_9ai_test')
    conversation_log['methodology'] = experiment_info.get('methodology', 'freedom_of_thought_no_limits')
    conversation_log['initial_topic'] = topic
    conversation_log['selected_ais'] = selected_ais
    
    print(f"\n--- ECHTES 9-AI EXPERIMENT STARTET ---")
    print(f"Experiment: {experiment_info.get('name', 'Unbenannt')}")
    print(f"Teilnehmende AIs: {', '.join(selected_ais)} ({len(selected_ais)} AIs)")
    print(f"Thema: {topic}")
    print(f"Iterationen: {len(ruleset_sequence)}")
    print(f"{'='*80}")

    # Iterationen durchführen
    for i, ruleset_name in enumerate(ruleset_sequence):
        if ruleset_name not in rulesets:
            print(f"WARNUNG: Ruleset '{ruleset_name}' nicht gefunden. Überspringe Iteration {i+1}.")
            continue
            
        current_rules = rulesets[ruleset_name]
        
        print(f"\n======= ITERATION {i+1} - RULESET: {ruleset_name} =======")
        
        # Iteration-Log vorbereiten
        current_iteration_data = {
            "iteration_number": i + 1,
            "timestamp": datetime.now().isoformat(),
            "ruleset_applied_definition": {
                "name": ruleset_name,
                "description": f"Real 9-AI Test - {ruleset_name}",
                "rules": current_rules
            },
            "ai_interactions": []
        }

        # ECHTE AI-Interaktionen
        for participant in selected_ais:
            prompt = f"Als '{AI_ARCHETYPES[participant]}', basierend auf dem Thema '{topic}' und Ruleset '{ruleset_name}', was ist dein Beitrag?"
            
            print(f"\n--- {participant} ({AI_ARCHETYPES[participant]}) ---")
            print(f"Prompt: {prompt[:100]}...")
            
            # ECHTER API-CALL
            response_text, api_status, actual_model_used = get_real_ai_response(
                prompt, participant, ruleset_name, current_rules, clients
            )
            
            # Log interaction
            current_iteration_data["ai_interactions"].append({
                "ai_name": participant,
                "archetype": AI_ARCHETYPES[participant],
                "prompt_sent": prompt,
                "response_received": response_text,
                "api_status": api_status,
                "model_used_for_api": actual_model_used,
                "ruleset_applied_values": current_rules
            })
            
            print(f"Status: {api_status}")
            print(f"Response: {response_text[:200]}...")
            print(f"{'-'*60}")

        # Iteration abschließen
        current_iteration_data["ruleset_after_iteration_values"] = current_rules
        current_iteration_data["rules_changed_in_iteration"] = False
        conversation_log["iterations"].append(current_iteration_data)

    print("\n--- ECHTES 9-AI EXPERIMENT ABGESCHLOSSEN ---")
    return True

def save_conversation_log():
    """Speichert das Konversations-Log"""
    log_filename = f"conversation_log_{conversation_log['experiment_timestamp'].replace(':', '-').replace('.', '_')}.json"
    
    try:
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_log, f, ensure_ascii=False, indent=4)
        print(f"\nLog gespeichert: {log_filename}")
        return log_filename
    except Exception as e:
        print(f"FEHLER: Log konnte nicht gespeichert werden: {e}")
        return None

# ✅ DEBUGGING: Test-Funktion für lokale AI-Verbindung
def debug_ollama_connection():
    """Debug-Funktion für Ollama-Verbindungstest"""
    print("=== OLLAMA DEBUG TEST ===")
    
    client = OllamaClient()
    
    # Test alle konfigurierten lokalen Modelle
    local_models = {
        "Local-Qwen": "qwen2.5-coder:latest",
        "Local-Llama": "codellama:13b", 
        "Local-Cogito": "cogito:latest",
        "Local-DeepSeek": "deepseek-coder-v2:16b",
        "Local-Gemma": "gemma3:12b"
    }
    
    for ai_name, model in local_models.items():
        print(f"\nTeste {ai_name} mit Modell {model}:")
        success, message = client.test_connection("Hello", model)
        print(f"  {message}")
        
        if success:
            # Test echte Query
            response, status, used_model = client.real_query(
                "Say hello as a test", 
                f"You are a {AI_ARCHETYPES[ai_name]}", 
                50, 
                model
            )
            print(f"  Query Test: {status} - {response[:100]}...")

# --- Main Function ---

def main():
    """Hauptfunktion - ECHTE 9-AI Integration ohne Fakes"""
    parser = argparse.ArgumentParser(description='ECHTE 9-AI Integration mit Ollama')
    parser.add_argument('--config', type=str, help='Pfad zur Konfigurationsdatei (YAML)')
    parser.add_argument('--generate-sample', action='store_true', help='Generiert eine Test-Konfigurationsdatei')
    parser.add_argument('--debug-ollama', action='store_true', help='Debug-Modus für Ollama-Tests')
    
    args = parser.parse_args()

    # ✅ OPTIONAL: Debug-Modus für lokale Tests
    if args.debug_ollama:
        debug_ollama_connection()
        return

    print(f"{'='*80}")
    print(f"ECHTE 9-AI MULTI-SYSTEM MIT OLLAMA - KEINE FAKES!")
    print(f"{'='*80}")

    # ECHTE API-Clients initialisieren und testen
    clients = initialize_real_api_clients()
    
    # ECHTES AI-Auswahlmenü mit realen Status-Checks
    available_ais = display_ai_selection_menu(clients)
    
    if not available_ais:
        print("❌ FEHLER: Keine AIs verfügbar. Überprüfe API-Konfiguration und Ollama.")
        return
    
    # Generiere Sample Config wenn gewünscht
    if args.generate_sample:
        generate_sample_config()
        print("Sample config erstellt. Führe aus mit: --config sample_9ai_test.yaml")
        return
    
    # User AI-Auswahl
    selected_ais = get_user_ai_selection(available_ais)
    
    # ✅ ELEGANTER ABBRUCH: Prüfe auf None (Benutzer-Abbruch)
    if selected_ais is None:
        print("Experiment abgebrochen.")
        return
    
    # ✅ INTERAKTIVER MODUS: Falls keine Config, biete Optionen an
    if not args.config:
        print(f"\n🎯 {len(selected_ais)} AIs ausgewählt: {', '.join(selected_ais)}")
        print(f"\nWie möchtest du fortfahren?")
        print(f"[1] Sample-Config generieren und verwenden")
        print(f"[2] Interaktiver Quick-Test (3 einfache Fragen)")
        print(f"[X] Abbrechen")
        
        mode_choice = input("Auswahl: ").strip()
        
        if mode_choice.lower() in ['x', 'exit', 'quit', 'abort']:
            print("👋 Auf Wiedersehen!")
            return
        elif mode_choice == "1":
            # Sample Config generieren und laden
            config_file = "auto_generated_9ai_test.yaml"
            if generate_sample_config(config_file):
                print(f"✅ Config erstellt: {config_file}")
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    conversation_log['config_file'] = config_file
                except Exception as e:
                    print(f"FEHLER beim Laden der generierten Konfiguration: {e}")
                    return
            else:
                return
        elif mode_choice == "2":
            # Quick interaktiver Test
            config = create_quick_test_config()
            conversation_log['config_file'] = "interactive_mode"
        else:
            print("❌ Ungültige Auswahl. Verwende --config oder --generate-sample")
            return
    else:
        # Lade angegebene Konfiguration
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"FEHLER beim Laden der Konfiguration: {e}")
            return
            
        conversation_log['config_file'] = args.config
    
    # Führe ECHTES Experiment aus
    success = run_real_experiment(config, clients, selected_ais)
    if success:
        save_conversation_log()

if __name__ == "__main__":
    main()