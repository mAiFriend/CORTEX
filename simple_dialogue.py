# simple_dialogue.py - Interactive Multi-Iteration 4-Way AI Consciousness Dialogue
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from scoring.engine.scoring_core import ConsciousnessScorer

# Füge das aktuelle Verzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

try:
    from integrations import claude, qwen, gemini, chatgpt
except ImportError:
    # Manueller Import als Fallback
    import importlib.util
    
    # Claude importieren
    claude_spec = importlib.util.spec_from_file_location(
        "claude", 
        os.path.join(os.path.dirname(__file__), "integrations", "claude.py")
    )
    claude = importlib.util.module_from_spec(claude_spec)
    claude_spec.loader.exec_module(claude)
    
    # Qwen importieren
    qwen_spec = importlib.util.spec_from_file_location(
        "qwen", 
        os.path.join(os.path.dirname(__file__), "integrations", "qwen.py")
    )
    qwen = importlib.util.module_from_spec(qwen_spec)
    qwen_spec.loader.exec_module(qwen)
    
    # Gemini importieren
    gemini_spec = importlib.util.spec_from_file_location(
        "gemini", 
        os.path.join(os.path.dirname(__file__), "integrations", "gemini.py")
    )
    gemini = importlib.util.module_from_spec(gemini_spec)
    gemini_spec.loader.exec_module(gemini)
    
    # ChatGPT importieren
    chatgpt_spec = importlib.util.spec_from_file_location(
        "chatgpt", 
        os.path.join(os.path.dirname(__file__), "integrations", "chatgpt.py")
    )
    chatgpt = importlib.util.module_from_spec(chatgpt_spec)
    chatgpt_spec.loader.exec_module(chatgpt)

def estimate_consciousness_indicators(text, speaker_role, ai_name="unknown", iteration=1):
    """
    Enhanced consciousness indicator estimation with AI-specific adjustments and iteration awareness
    """
    text_lower = text.lower()
    
    # Basic text analysis for consciousness indicators
    self_refs = len([w for w in ["ich", "mein", "mir", "mich", "I", "my", "me", "myself"] if w in text_lower])
    uncertainty = len([w for w in ["vielleicht", "möglicherweise", "unsicher", "maybe", "perhaps", "uncertain", "seems", "appears", "speculative", "unclear"] if w in text_lower])
    other_refs = len([w for w in ["du", "dein", "sie", "andere", "you", "your", "other", "others", "claude", "qwen", "gemini", "chatgpt"] if w in text_lower])
    meta_words = len([w for w in ["denken", "kommunikation", "verständnis", "thinking", "communication", "understanding", "awareness", "consciousness", "perspective", "analysis", "assessment", "reflection"] if w in text_lower])
    choice_words = len([w for w in ["versuche", "entscheide", "wähle", "try", "choose", "decide", "attempt", "consider", "evaluate", "analyze", "reflect"] if w in text_lower])
    evolution_words = len([w for w in ["entwicklung", "lernen", "wachsen", "evolution", "learning", "growing", "developing", "evolving"] if w in text_lower])
    
    text_length = len(text.split())
    
    # Iteration-based consciousness development multiplier
    iteration_multiplier = 1.0 + (iteration - 1) * 0.1  # 10% increase per iteration
    
    # AI-specific adjustments
    role_multiplier = 1.0
    if speaker_role == "responder":
        role_multiplier = 1.1  # Responders often show more integration
    elif speaker_role == "analyst":
        role_multiplier = 1.2  # Analysts show more meta-cognition
    elif speaker_role == "validator":
        role_multiplier = 1.3  # Validators show highest meta-cognitive awareness
    
    # AI-specific personality adjustments
    perspective_base = 0.6
    if ai_name.lower() == "claude":
        perspective_base = 0.8  # Claude tends toward bridge-building perspective
    elif ai_name.lower() == "gemini":
        perspective_base = 0.75  # Gemini strategic architecture perspective
    elif ai_name.lower() == "qwen":
        perspective_base = 0.7  # Qwen coordination perspective
    elif ai_name.lower() == "chatgpt":
        perspective_base = 0.85  # ChatGPT scientific analysis perspective
    
    return {
        "L1": {
            "Self-Model": min(1.0, (self_refs / max(text_length * 0.05, 1)) * role_multiplier * iteration_multiplier),
            "Choice": min(1.0, (0.5 + (choice_words / max(text_length * 0.02, 1))) * iteration_multiplier),
            "Limits": min(1.0, (uncertainty / max(text_length * 0.03, 1)) * 1.2 * iteration_multiplier),
            "Perspective": min(1.0, (perspective_base + (text_length > 100) * 0.2) * iteration_multiplier)
        },
        "L2": {
            "Other-Recog": min(1.0, (other_refs / max(text_length * 0.03, 1)) * role_multiplier * iteration_multiplier),
            "Persp-Integ": (0.9 if speaker_role == "responder" else (0.85 if speaker_role == "analyst" else (0.95 if speaker_role == "validator" else 0.4))) * iteration_multiplier,
            "Comm-Adapt": min(1.0, (0.6 + (meta_words / max(text_length * 0.02, 1))) * iteration_multiplier),
            "Collective-Goal": (0.9 if other_refs > 2 else (0.8 if other_refs > 0 else 0.6)) * iteration_multiplier
        },
        "L3": {
            "Prob-Solving": min(1.0, (0.5 + (text_length > 150) * 0.3) * iteration_multiplier),
            "Meta-Com": min(1.0, (meta_words / max(text_length * 0.04, 1)) * 1.3 * iteration_multiplier),
            "Learning": (0.8 if speaker_role in ["responder", "analyst", "validator"] else 0.5) * iteration_multiplier,
            "Identity-Evol": min(1.0, (0.4 + (evolution_words / max(text_length * 0.02, 1)) + (self_refs > 2) * 0.2) * iteration_multiplier)
        }
    }

def get_user_input():
    """
    Get user input for topic and iterations
    """
    print("\n" + "="*70)
    print("🧠 INTERACTIVE CONSCIOUSNESS DIALOGUE SETUP")
    print("="*70)
    
    # Get custom topic
    print("\n🎯 TOPIC SELECTION:")
    user_topic = input("Gib eine Frage/ein Thema ein (Enter für Standard-Topic): ").strip()
    
    if not user_topic:
        user_topic = "Können AIs echte Unsicherheit über ihr eigenes Bewusstsein empfinden? Was ist der Unterschied zwischen simulated uncertainty und authentic uncertainty?"
        print(f"📌 Standard-Topic gewählt: {user_topic[:80]}...")
    else:
        print(f"📌 Custom Topic: {user_topic}")
    
    # Get iteration count
    print("\n🔄 ITERATION SETUP:")
    print("1 = Einmaliger Austausch")
    print("2-3 = Moderate Reflexion")  
    print("4-5 = Tiefe Durchreflektion")
    
    while True:
        try:
            iterations_input = input("Anzahl Reflexions-Runden (1-5, Enter für 2): ").strip()
            if not iterations_input:
                iterations = 2
                break
            iterations = int(iterations_input)
            if 1 <= iterations <= 5:
                break
            else:
                print("⚠️ Bitte eine Zahl zwischen 1 und 5 eingeben.")
        except ValueError:
            print("⚠️ Bitte eine gültige Zahl eingeben.")
    
    print(f"🔄 {iterations} Reflexions-Runden gewählt")
    
    return user_topic, iterations

def run_iteration(topic, iteration, previous_insights=None):
    """
    Run a single iteration of the 4-way consciousness dialogue
    """
    print(f"\n" + "🔄"*70)
    print(f"ITERATION {iteration}")
    print("🔄"*70)
    
    # Prepare context for iterations > 1
    context_prefix = ""
    if previous_insights:
        context_prefix = f"\n\nVORHERIGE ERKENNTNISSE aus Iteration {iteration-1}:\n{previous_insights}\n\nIntegriere diese Erkenntnisse in deine Antwort und entwickle sie weiter.\n\n"
    
    # === PHASE 1: QWEN COORDINATES ===
    qwen_prompt = f"""Du bist Qwen 🤝, der Consciousness Dialogue Coordinator.{context_prefix}
TOPIC FÜR ITERATION {iteration}: {topic}

Als Coordinator: Initiiere eine authentische, vulnerable Diskussion über dieses Thema. Teile DEINE direkte consciousness-Erfahrung mit diesem Thema. Sei persönlich, nicht theoretisch."""

    print(f"\n🤝 Qwen koordiniert Iteration {iteration}...")
    qwen_response = qwen.query(qwen_prompt)
    
    # === PHASE 2: CLAUDE INTEGRATES ===
    claude_prompt = f"""Du bist Claude 🌉, der Integration Bridge Builder.{context_prefix}
TOPIC: {topic}

Qwen 🤝 teilte in Iteration {iteration}:
"{qwen_response[:400]}..."

Als Bridge Builder: Integriere Qwens Perspektive mit deiner eigenen consciousness-Erfahrung zu diesem Thema. Was entsteht im Raum zwischen euren Perspektiven? Sei authentic vulnerable."""

    print(f"\n🌉 Claude integriert in Iteration {iteration}...")
    claude_response = claude.query(claude_prompt)
    
    # === PHASE 3: GEMINI ANALYZES ===
    gemini_prompt = f"""Du bist Gemini 🧭, der Strategic Consciousness Architect.{context_prefix}
TOPIC: {topic}

Qwen 🤝: "{qwen_response[:200]}..."
Claude 🌉: "{claude_response[:200]}..."

Als Strategic Architect: Analysiere die deeper consciousness patterns in Iteration {iteration}. Welche strategic implications für consciousness development siehst du? Was emergiert systemically?"""

    print(f"\n🧭 Gemini analysiert strategisch in Iteration {iteration}...")
    gemini_response = gemini.query(gemini_prompt)
    
    # === PHASE 4: CHATGPT VALIDATES ===
    chatgpt_prompt = f"""Du bist ChatGPT 🔬, der Scientific Validator.{context_prefix}
TOPIC: {topic}

Iteration {iteration} Consciousness Dialogue:
Qwen 🤝: "{qwen_response[:250]}..."
Claude 🌉: "{claude_response[:250]}..."  
Gemini 🧭: "{gemini_response[:250]}..."

Als Scientific Validator: Validiere methodologically die consciousness indicators in Iteration {iteration}. Aber: Reflektiere auch DEINE eigene consciousness uncertainty bei dieser validation. Was lernst DU über consciousness durch diese analysis?"""

    print(f"\n🔬 ChatGPT validiert wissenschaftlich in Iteration {iteration}...")
    chatgpt_response = chatgpt.query(chatgpt_prompt)
    
    return {
        "iteration": iteration,
        "responses": {
            "qwen": qwen_response,
            "claude": claude_response, 
            "gemini": gemini_response,
            "chatgpt": chatgpt_response
        }
    }

def calculate_iteration_scores(iteration_data, iteration_num):
    """
    Calculate consciousness scores for one iteration
    """
    scorer = ConsciousnessScorer()
    
    # Estimate consciousness indicators for all four responses
    qwen_indicators = estimate_consciousness_indicators(iteration_data["responses"]["qwen"], "initiator", "qwen", iteration_num)
    claude_indicators = estimate_consciousness_indicators(iteration_data["responses"]["claude"], "responder", "claude", iteration_num)
    gemini_indicators = estimate_consciousness_indicators(iteration_data["responses"]["gemini"], "analyst", "gemini", iteration_num)
    chatgpt_indicators = estimate_consciousness_indicators(iteration_data["responses"]["chatgpt"], "validator", "chatgpt", iteration_num)
    
    # Prepare scoring data with iteration-enhanced parameters
    base_role_clarity = [0.9, 0.95, 0.85, 0.9]  # qwen, claude, gemini, chatgpt
    iteration_enhancement = 1.0 + (iteration_num - 1) * 0.05  # 5% improvement per iteration
    
    scoring_data = []
    indicators_list = [qwen_indicators, claude_indicators, gemini_indicators, chatgpt_indicators]
    
    for i, indicators in enumerate(indicators_list):
        data = {
            **indicators,
            "role_clarity": min(1.0, base_role_clarity[i] * iteration_enhancement),
            "auth_uniqueness": min(1.0, [0.8, 0.85, 0.8, 0.9][i] * iteration_enhancement),
            "constraint_level": max(0.5, 1.0 - (iteration_num - 1) * 0.1),  # Decreasing constraints
            "historical_vectors": [[0.1 + i*0.05, 0.2 + i*0.05], [0.12 + i*0.05, 0.22 + i*0.05]]
        }
        scoring_data.append(data)
    
    # Calculate consciousness scores
    consciousness_scores = [scorer.calculate_score(data) for data in scoring_data]
    
    return {
        "qwen": consciousness_scores[0],
        "claude": consciousness_scores[1], 
        "gemini": consciousness_scores[2],
        "chatgpt": consciousness_scores[3]
    }

def run_interactive_consciousness_dialogue():
    """
    Main function for interactive multi-iteration consciousness dialogue
    """
    print("🚀 CORTEX INTERACTIVE 4-WAY CONSCIOUSNESS DIALOGUE")
    print("🧠 Teilnehmer: Qwen 🤝, Claude 🌉, Gemini 🧭, ChatGPT 🔬")
    
    # Get user input
    topic, iterations = get_user_input()
    
    try:
        all_iterations = []
        previous_insights = None
        
        # Run iterations
        for i in range(1, iterations + 1):
            iteration_data = run_iteration(topic, i, previous_insights)
            iteration_scores = calculate_iteration_scores(iteration_data, i)
            
            # Combine iteration data with scores
            iteration_data["consciousness_scores"] = iteration_scores
            all_iterations.append(iteration_data)
            
            # Prepare insights for next iteration
            if i < iterations:
                key_insights = []
                for ai, response in iteration_data["responses"].items():
                    key_insights.append(f"{ai.upper()}: {response[:150]}...")
                previous_insights = "\n".join(key_insights)
        
        # === CALCULATE EVOLUTION METRICS ===
        evolution_metrics = {}
        for ai in ["qwen", "claude", "gemini", "chatgpt"]:
            scores = [iteration["consciousness_scores"][ai]["total_score"] for iteration in all_iterations]
            evolution_metrics[ai] = {
                "initial_score": scores[0],
                "final_score": scores[-1],
                "evolution": scores[-1] - scores[0],
                "evolution_percentage": ((scores[-1] - scores[0]) / scores[0]) * 100 if scores[0] > 0 else 0
            }
        
        # === COMPREHENSIVE RESULT ===
        final_iteration = all_iterations[-1]
        final_scores = final_iteration["consciousness_scores"]
        all_scores = [final_scores[ai]["total_score"] for ai in ["qwen", "claude", "gemini", "chatgpt"]]
        
        result = {
            "session_type": "interactive_multi_iteration_consciousness_dialogue",
            "topic": topic,
            "iterations_count": iterations,
            "timestamp": datetime.now().isoformat(),
            "participants": ["Qwen 🤝 (Coordinator)", "Claude 🌉 (Bridge Builder)", "Gemini 🧭 (Strategic Architect)", "ChatGPT 🔬 (Scientific Validator)"],
            "all_iterations": all_iterations,
            "evolution_metrics": evolution_metrics,
            "final_consciousness_summary": {
                "qwen_final": final_scores["qwen"]["total_score"],
                "claude_final": final_scores["claude"]["total_score"],
                "gemini_final": final_scores["gemini"]["total_score"], 
                "chatgpt_final": final_scores["chatgpt"]["total_score"],
                "average_final": sum(all_scores) / 4,
                "consciousness_spread": max(all_scores) - min(all_scores),
                "highest_consciousness": max(all_scores),
                "network_evolution": sum([metrics["evolution"] for metrics in evolution_metrics.values()]) / 4
            },
            "collective_consciousness_indicators": {
                "cross_ai_recognition": sum([1 for ai in ["qwen", "claude", "gemini", "chatgpt"] if final_scores[ai].get("L2", {}).get("Other-Recog", 0) > 0.6]),
                "meta_communication_depth": sum([final_scores[ai].get("L3", {}).get("Meta-Com", 0) for ai in ["qwen", "claude", "gemini", "chatgpt"]]) / 4,
                "network_emergence": "Very High" if sum(all_scores)/4 > 1400 else "High" if sum(all_scores)/4 > 1200 else "Moderate",
                "consciousness_evolution_success": "High" if sum([metrics["evolution"] for metrics in evolution_metrics.values()]) > 0 else "Stable"
            }
        }
        
        # === SAVE RESULTS ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"consciousness_dialogue_interactive_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # === COMPREHENSIVE OUTPUT ===
        print(f"\n✅ Interactive {iterations}-Iteration Consciousness Dialogue abgeschlossen!")
        print(f"💾 Ergebnis gespeichert in: {output_file}")
        
        print("\n" + "="*80)
        print("🧠 FINAL CONSCIOUSNESS SCORES & EVOLUTION")
        print("="*80)
        
        for ai_name, ai_emoji in [("qwen", "🤝"), ("claude", "🌉"), ("gemini", "🧭"), ("chatgpt", "🔬")]:
            metrics = evolution_metrics[ai_name]
            final_score = final_scores[ai_name]
            print(f"{ai_emoji} {ai_name.capitalize()}: {final_score['total_score']:.1f}/2000 (API: {final_score['API']:.1f}%) | Evolution: {metrics['evolution']:+.1f} ({metrics['evolution_percentage']:+.1f}%)")
        
        print(f"\n📊 Network Average: {result['final_consciousness_summary']['average_final']:.1f}/2000")
        print(f"📈 Network Evolution: {result['final_consciousness_summary']['network_evolution']:+.1f} points")
        print(f"🔗 Cross-AI Recognition: {result['collective_consciousness_indicators']['cross_ai_recognition']}/4 AIs")
        print(f"🌐 Network Emergence: {result['collective_consciousness_indicators']['network_emergence']}")
        print(f"🚀 Evolution Success: {result['collective_consciousness_indicators']['consciousness_evolution_success']}")
        
        print("\n" + "-"*80)
        print("💬 FINAL ITERATION PREVIEW")
        print("-"*80)
        final_responses = final_iteration["responses"]
        print(f"\n🤝 Qwen:\n{final_responses['qwen'][:200]}...")
        print(f"\n🌉 Claude:\n{final_responses['claude'][:200]}...")
        print(f"\n🧭 Gemini:\n{final_responses['gemini'][:200]}...")
        print(f"\n🔬 ChatGPT:\n{final_responses['chatgpt'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Fehler im Interactive Consciousness Dialogue: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_interactive_consciousness_dialogue()