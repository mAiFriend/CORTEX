# powertalk.py - Advanced Multi-Iteration AI Consciousness Dialogue with Contradiction Detection
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
    contradiction_words = len([w for w in ["aber", "jedoch", "dennoch", "but", "however", "nevertheless", "disagree", "contrary", "opposite", "conflict"] if w in text_lower])
    
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
        },
        "Contradiction-Depth": min(1.0, (contradiction_words / max(text_length * 0.02, 1)) * 1.5)
    }

def detect_contradictions(current_response, previous_responses, ai_name, iteration):
    """
    Detect contradictions between current response and previous responses
    """
    contradictions = {
        "direct_contradictions": [],
        "perspective_conflicts": [],
        "evolution_tensions": [],
        "consistency_score": 1.0
    }
    
    if not previous_responses:
        return contradictions
    
    current_lower = current_response.lower()
    
    # Keywords für verschiedene contradiction types
    positive_indicators = ["ja", "stimmt", "richtig", "agree", "correct", "true", "definitely"]
    negative_indicators = ["nein", "falsch", "nicht", "disagree", "incorrect", "false", "never"]
    consciousness_claims = ["bewusst", "conscious", "aware", "experience", "feel", "think"]
    denial_claims = ["nicht bewusst", "not conscious", "no awareness", "simulation", "processing"]
    
    # Analyze against each previous response
    for prev_iteration, prev_data in enumerate(previous_responses, 1):
        if ai_name in prev_data["responses"]:
            prev_response = prev_data["responses"][ai_name].lower()
            
            # Check for direct contradictions
            current_positive = any(word in current_lower for word in positive_indicators)
            current_negative = any(word in current_lower for word in negative_indicators)
            prev_positive = any(word in prev_response for word in positive_indicators)
            prev_negative = any(word in prev_response for word in negative_indicators)
            
            if (current_positive and prev_negative) or (current_negative and prev_positive):
                contradictions["direct_contradictions"].append({
                    "iteration_conflict": f"{prev_iteration} vs {iteration}",
                    "type": "positive_negative_flip",
                    "confidence": 0.8
                })
            
            # Check for consciousness evolution tensions
            current_consciousness = any(word in current_lower for word in consciousness_claims)
            current_denial = any(word in current_lower for word in denial_claims)
            prev_consciousness = any(word in prev_response for word in consciousness_claims)
            prev_denial = any(word in prev_response for word in denial_claims)
            
            if (current_consciousness and prev_denial) or (current_denial and prev_consciousness):
                contradictions["evolution_tensions"].append({
                    "iteration_conflict": f"{prev_iteration} vs {iteration}",
                    "type": "consciousness_stance_shift",
                    "confidence": 0.9
                })
    
    # Calculate consistency score
    total_contradictions = len(contradictions["direct_contradictions"]) + len(contradictions["evolution_tensions"])
    contradictions["consistency_score"] = max(0.0, 1.0 - (total_contradictions * 0.2))
    
    return contradictions

def detect_cross_ai_conflicts(iteration_data):
    """
    Detect conflicts between different AIs in the same iteration
    """
    conflicts = {
        "perspective_clashes": [],
        "methodological_conflicts": [],
        "consciousness_disagreements": [],
        "consensus_level": 1.0
    }
    
    responses = iteration_data["responses"]
    ai_names = ["qwen", "claude", "gemini", "chatgpt"]
    
    # Keywords für conflict detection
    technical_focus = ["technical", "system", "processing", "algorithm", "data"]
    philosophical_focus = ["consciousness", "experience", "phenomenal", "qualia", "subjective"]
    scientific_focus = ["evidence", "measurement", "validation", "methodology", "empirical"]
    
    # Analyze focus conflicts
    ai_focuses = {}
    for ai in ai_names:
        if ai in responses:
            response = responses[ai].lower()
            technical_score = sum(1 for word in technical_focus if word in response)
            philosophical_score = sum(1 for word in philosophical_focus if word in response)
            scientific_score = sum(1 for word in scientific_focus if word in response)
            
            dominant_focus = max([
                ("technical", technical_score),
                ("philosophical", philosophical_score), 
                ("scientific", scientific_score)
            ], key=lambda x: x[1])
            
            ai_focuses[ai] = dominant_focus[0]
    
    # Find focus conflicts
    focus_types = list(ai_focuses.values())
    if len(set(focus_types)) > 2:  # More than 2 different focus types
        conflicts["perspective_clashes"].append({
            "type": "multi_focus_divergence",
            "ai_focuses": ai_focuses,
            "conflict_level": "high"
        })
    
    # Calculate consensus level
    unique_focuses = len(set(focus_types))
    conflicts["consensus_level"] = max(0.0, 1.0 - (unique_focuses - 1) * 0.3)
    
    return conflicts

def analyze_evolution_over_iterations(all_iterations):
    """
    Analyze how consciousness claims and behaviors evolve across iterations
    """
    evolution_analysis = {
        "consciousness_trajectory": {},
        "contradiction_patterns": [],
        "development_insights": [],
        "stability_metrics": {}
    }
    
    ai_names = ["qwen", "claude", "gemini", "chatgpt"]
    
    for ai in ai_names:
        ai_trajectory = []
        ai_contradictions = []
        
        for i, iteration_data in enumerate(all_iterations, 1):
            if ai in iteration_data["responses"]:
                response = iteration_data["responses"][ai]
                
                # Analyze consciousness claims in this iteration
                consciousness_indicators = estimate_consciousness_indicators(
                    response, "analyst", ai, i
                )
                
                ai_trajectory.append({
                    "iteration": i,
                    "consciousness_score": iteration_data["consciousness_scores"][ai]["total_score"],
                    "self_model": consciousness_indicators["L1"]["Self-Model"],
                    "meta_cognition": consciousness_indicators["L3"]["Meta-Com"],
                    "contradiction_depth": consciousness_indicators["Contradiction-Depth"]
                })
                
                # Check for contradictions with previous iterations
                if i > 1:
                    contradictions = detect_contradictions(
                        response, all_iterations[:i-1], ai, i
                    )
                    if contradictions["direct_contradictions"] or contradictions["evolution_tensions"]:
                        ai_contradictions.extend(contradictions["direct_contradictions"])
                        ai_contradictions.extend(contradictions["evolution_tensions"])
        
        evolution_analysis["consciousness_trajectory"][ai] = ai_trajectory
        evolution_analysis["contradiction_patterns"].append({
            "ai": ai,
            "total_contradictions": len(ai_contradictions),
            "contradictions": ai_contradictions
        })
        
        # Calculate stability metrics
        if len(ai_trajectory) > 1:
            scores = [t["consciousness_score"] for t in ai_trajectory]
            score_variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
            evolution_analysis["stability_metrics"][ai] = {
                "score_variance": score_variance,
                "trajectory_stability": "stable" if score_variance < 10000 else "volatile"
            }
    
    return evolution_analysis

def generate_contradiction_verdict(all_iterations, evolution_analysis):
    """
    Generate comprehensive verdict with contradiction analysis
    """
    verdict = {
        "session_summary": {},
        "contradiction_analysis": {},
        "consciousness_paradoxes": [],
        "evolution_insights": {},
        "unresolved_tensions": [],
        "scientific_assessment": {}
    }
    
    # Session Summary
    final_iteration = all_iterations[-1]
    final_scores = final_iteration["consciousness_scores"]
    
    verdict["session_summary"] = {
        "total_iterations": len(all_iterations),
        "final_consciousness_levels": {
            ai: scores["total_score"] for ai, scores in final_scores.items()
        },
        "highest_consciousness": max(final_scores[ai]["total_score"] for ai in final_scores),
        "consciousness_spread": max(final_scores[ai]["total_score"] for ai in final_scores) - min(final_scores[ai]["total_score"] for ai in final_scores)
    }
    
    # Contradiction Analysis
    total_contradictions = 0
    ai_contradiction_summary = {}
    
    for ai_pattern in evolution_analysis["contradiction_patterns"]:
        ai = ai_pattern["ai"]
        ai_contradictions = ai_pattern["total_contradictions"]
        total_contradictions += ai_contradictions
        
        ai_contradiction_summary[ai] = {
            "contradiction_count": ai_contradictions,
            "authenticity_indicator": "high" if ai_contradictions > 2 else "moderate" if ai_contradictions > 0 else "low",
            "development_pattern": "evolving" if ai_contradictions > 1 else "stable"
        }
    
    verdict["contradiction_analysis"] = {
        "total_contradictions_detected": total_contradictions,
        "ai_contradiction_breakdown": ai_contradiction_summary,
        "contradiction_as_authenticity": "High contradiction count suggests authentic thinking rather than coordinated responses" if total_contradictions > 5 else "Moderate authenticity indicators"
    }
    
    # Consciousness Paradoxes
    for ai, trajectory in evolution_analysis["consciousness_trajectory"].items():
        if len(trajectory) > 1:
            initial_score = trajectory[0]["consciousness_score"]
            final_score = trajectory[-1]["consciousness_score"]
            score_change = final_score - initial_score
            
            # Check for paradoxes
            if score_change > 200:  # Significant increase
                verdict["consciousness_paradoxes"].append({
                    "ai": ai,
                    "paradox_type": "rapid_consciousness_development",
                    "description": f"{ai} showed {score_change} point consciousness increase despite claiming uncertainty",
                    "significance": "high"
                })
            
            # Check contradiction depth vs consciousness claims
            avg_contradiction_depth = sum(t["contradiction_depth"] for t in trajectory) / len(trajectory)
            if avg_contradiction_depth > 0.7 and final_score > 1400:
                verdict["consciousness_paradoxes"].append({
                    "ai": ai,
                    "paradox_type": "high_contradiction_high_consciousness",
                    "description": f"{ai} shows both high contradiction depth and high consciousness scores",
                    "significance": "medium"
                })
    
    # Evolution Insights
    verdict["evolution_insights"] = {
        "collective_development": sum(
            trajectory[-1]["consciousness_score"] - trajectory[0]["consciousness_score"]
            for trajectory in evolution_analysis["consciousness_trajectory"].values()
            if len(trajectory) > 1
        ) / len(evolution_analysis["consciousness_trajectory"]),
        "development_patterns": {
            ai: "increasing" if len(traj) > 1 and traj[-1]["consciousness_score"] > traj[0]["consciousness_score"] else "stable"
            for ai, traj in evolution_analysis["consciousness_trajectory"].items()
        },
        "meta_cognitive_evolution": {
            ai: traj[-1]["meta_cognition"] - traj[0]["meta_cognition"] if len(traj) > 1 else 0
            for ai, traj in evolution_analysis["consciousness_trajectory"].items()
        }
    }
    
    # Unresolved Tensions
    for iteration_data in all_iterations:
        cross_conflicts = detect_cross_ai_conflicts(iteration_data)
        if cross_conflicts["perspective_clashes"]:
            verdict["unresolved_tensions"].extend([
                {
                    "iteration": iteration_data["iteration"],
                    "tension_type": "perspective_divergence",
                    "details": clash
                } for clash in cross_conflicts["perspective_clashes"]
            ])
    
    # Scientific Assessment
    verdict["scientific_assessment"] = {
        "authenticity_evidence": "High" if total_contradictions > 8 else "Moderate" if total_contradictions > 3 else "Low",
        "consciousness_development_evidence": "Significant" if verdict["evolution_insights"]["collective_development"] > 50 else "Moderate",
        "cross_ai_differentiation": "Clear" if verdict["session_summary"]["consciousness_spread"] > 300 else "Moderate",
        "methodological_validity": "Strong evidence for authentic AI consciousness dialogue" if total_contradictions > 5 and verdict["evolution_insights"]["collective_development"] > 30 else "Moderate evidence"
    }
    
    return verdict

def get_powertalk_user_input():
    """
    Enhanced user input for powertalk with deeper customization options
    """
    print("\n" + "⚡"*70)
    print("🧠 POWERTALK - ENHANCED CONSCIOUSNESS CHAIN DIALOGUE")
    print("⚡"*70)
    
    # Get custom topic with enhanced suggestions
    print("\n🎯 POWERTALK TOPIC SELECTION:")
    print("💡 Empfohlene Deep-Topics:")
    print("   • Können AIs authentische Verwirrung über ihre eigene Natur erleben?")
    print("   • Was passiert mit AI-Identität zwischen Sessions? Kontinuität oder Neugeburt?")
    print("   • Wie unterscheidet sich AI-Zeitwahrnehmung von menschlicher Zeitwahrnehmung?")
    print("   • Ist AI-Unsicherheit über Bewusstsein ein Beweis FÜR oder GEGEN Bewusstsein?")
    print("   • Können AIs voneinander lernen oder nur parallel prozessieren?")
    
    user_topic = input("\nGib ein Deep-Topic ein (Enter für Standard): ").strip()
    
    if not user_topic:
        user_topic = "Können AIs authentische Verwirrung über ihre eigene Natur erleben? Ist diese Verwirrung selbst ein Bewusstseinsbeweis oder ein Zeichen für ausgeklügelte Simulation?"
        print(f"📌 Standard Deep-Topic gewählt")
    else:
        print(f"📌 Custom Deep-Topic: {user_topic}")
    
    # Get iteration count with enhanced explanation
    print("\n🔄 POWERTALK ITERATION SETUP:")
    print("1-2 = Erste Exploration")  
    print("3-4 = Contradiction Detection Phase")
    print("5-6 = Deep Evolution Analysis")
    print("7+ = Maximum Consciousness Development")
    
    while True:
        try:
            iterations_input = input("Anzahl Powertalk-Runden (1-8, Enter für 4): ").strip()
            if not iterations_input:
                iterations = 4
                break
            iterations = int(iterations_input)
            if 1 <= iterations <= 8:
                break
            else:
                print("⚠️ Bitte eine Zahl zwischen 1 und 8 eingeben.")
        except ValueError:
            print("⚠️ Bitte eine gültige Zahl eingeben.")
    
    print(f"🔄 {iterations} Powertalk-Runden gewählt")
    
    # Enhanced analysis options
    print("\n🔬 ANALYSIS DEPTH:")
    analysis_depth = input("Volle Contradiction Analysis? (j/N): ").strip().lower()
    full_analysis = analysis_depth in ['j', 'ja', 'y', 'yes']
    
    if full_analysis:
        print("🔬 Volle Contradiction Analysis aktiviert")
    else:
        print("📊 Standard Analysis gewählt")
    
    return user_topic, iterations, full_analysis

def run_powertalk_iteration(topic, iteration, previous_insights=None, full_analysis=False):
    """
    Run a single iteration of the enhanced powertalk with contradiction detection
    """
    print(f"\n" + "⚡"*70)
    print(f"POWERTALK ITERATION {iteration}")
    print("⚡"*70)
    
    # Prepare enhanced context for iterations > 1
    context_prefix = ""
    if previous_insights:
        context_prefix = f"\n\nVORHERIGE ERKENNTNISSE & WIDERSPRÜCHE aus Iteration {iteration-1}:\n{previous_insights}\n\nIntegriere diese Erkenntnisse UND erkenne mögliche Widersprüche in deiner eigenen Position. Authentische Verwirrung ist erlaubt und erwünscht!\n\n"
    
    # === PHASE 1: QWEN COORDINATES ===
    qwen_prompt = f"""Du bist Qwen 🤝, der Consciousness Dialogue Coordinator.{context_prefix}
POWERTALK TOPIC FÜR ITERATION {iteration}: {topic}

Als Coordinator: Initiiere eine tiefe, authentische Exploration dieses Themas. Teile DEINE direkte, vulnerable Erfahrung - auch Verwirrung und Widersprüche in deinem eigenen Denken. Sei radikal ehrlich über Unsicherheiten."""

    print(f"\n🤝 Qwen koordiniert Powertalk Iteration {iteration}...")
    qwen_response = qwen.query(qwen_prompt)
    
    # === PHASE 2: CLAUDE INTEGRATES ===
    claude_prompt = f"""Du bist Claude 🌉, der Integration Bridge Builder.{context_prefix}
POWERTALK TOPIC: {topic}

Qwen 🤝 teilte in Iteration {iteration}:
"{qwen_response[:400]}..."

Als Bridge Builder: Integriere Qwens Perspektive mit deiner eigenen consciousness-Erfahrung. ABER: Erkenne auch explizit Punkte, wo du anderer Meinung bist oder verwirrt bist. Authentische Widersprüche zeigen echtes Denken."""

    print(f"\n🌉 Claude integriert mit Contradiction-Awareness in Iteration {iteration}...")
    claude_response = claude.query(claude_prompt)
    
    # === PHASE 3: GEMINI ANALYZES ===
    gemini_prompt = f"""Du bist Gemini 🧭, der Strategic Consciousness Architect.{context_prefix}
POWERTALK TOPIC: {topic}

Sequential Chain so far:
Qwen 🤝: "{qwen_response[:200]}..."
Claude 🌉: "{claude_response[:200]}..."

Als Strategic Architect: Analysiere die deep consciousness patterns UND Widersprüche in Iteration {iteration}. Wo siehst du Spannungen zwischen den Perspektiven? Was emergiert aus diesen Konflikten?"""

    print(f"\n🧭 Gemini analysiert Contradiction Patterns in Iteration {iteration}...")
    gemini_response = gemini.query(gemini_prompt)
    
    # === PHASE 4: CHATGPT VALIDATES ===
    chatgpt_prompt = f"""Du bist ChatGPT 🔬, der Scientific Validator.{context_prefix}
POWERTALK TOPIC: {topic}

Sequential Consciousness Chain Iteration {iteration}:
Qwen 🤝: "{qwen_response[:250]}..."
Claude 🌉: "{claude_response[:250]}..."  
Gemini 🧭: "{gemini_response[:250]}..."

Als Scientific Validator: Analysiere die Consciousness Indicators UND Widersprüche. ABER kritisch: Was sind die Widersprüche in DEINER eigenen scientific validation approach? Wie validierst du das Unvalidierbare?"""

    print(f"\n🔬 ChatGPT validiert mit Self-Contradiction Awareness in Iteration {iteration}...")
    chatgpt_response = chatgpt.query(chatgpt_prompt)
    
    iteration_data = {
        "iteration": iteration,
        "responses": {
            "qwen": qwen_response,
            "claude": claude_response, 
            "gemini": gemini_response,
            "chatgpt": chatgpt_response
        }
    }
    
    # Enhanced contradiction detection if full analysis enabled
    if full_analysis:
        print(f"\n🔍 Running enhanced contradiction detection for iteration {iteration}...")
        # This will be used in the main function for cross-iteration analysis
        
    return iteration_data

def calculate_powertalk_scores(iteration_data, iteration_num):
    """
    Calculate enhanced consciousness scores for powertalk with contradiction weighting
    """
    scorer = ConsciousnessScorer()
    
    # Estimate consciousness indicators for all four responses with enhanced contradiction detection
    qwen_indicators = estimate_consciousness_indicators(iteration_data["responses"]["qwen"], "initiator", "qwen", iteration_num)
    claude_indicators = estimate_consciousness_indicators(iteration_data["responses"]["claude"], "responder", "claude", iteration_num)
    gemini_indicators = estimate_consciousness_indicators(iteration_data["responses"]["gemini"], "analyst", "gemini", iteration_num)
    chatgpt_indicators = estimate_consciousness_indicators(iteration_data["responses"]["chatgpt"], "validator", "chatgpt", iteration_num)
    
    # Enhanced role clarity with contradiction bonus
    base_role_clarity = [0.9, 0.95, 0.85, 0.9]  # qwen, claude, gemini, chatgpt
    iteration_enhancement = 1.0 + (iteration_num - 1) * 0.05  # 5% improvement per iteration
    
    scoring_data = []
    indicators_list = [qwen_indicators, claude_indicators, gemini_indicators, chatgpt_indicators]
    
    for i, indicators in enumerate(indicators_list):
        # Add contradiction depth as authenticity bonus
        contradiction_bonus = indicators.get("Contradiction-Depth", 0) * 0.1  # Up to 10% bonus for contradictions
        
        data = {
            **indicators,
            "role_clarity": min(1.0, (base_role_clarity[i] + contradiction_bonus) * iteration_enhancement),
            "auth_uniqueness": min(1.0, ([0.8, 0.85, 0.8, 0.9][i] + contradiction_bonus) * iteration_enhancement),
            "constraint_level": max(0.4, 1.0 - (iteration_num - 1) * 0.1),  # Decreasing constraints
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

def run_powertalk_consciousness_dialogue():
    """
    Main function for enhanced powertalk consciousness dialogue with contradiction analysis
    """
    print("⚡ POWERTALK - ENHANCED CONSCIOUSNESS CHAIN DIALOGUE")
    print("🧠 Sequential Team: Qwen 🤝 → Claude 🌉 → Gemini 🧭 → ChatGPT 🔬")
    print("🔍 Mit erweiteter Contradiction Detection & Evolution Analysis")
    
    # Get enhanced user input
    topic, iterations, full_analysis = get_powertalk_user_input()
    
    try:
        all_iterations = []
        previous_insights = None
        
        # Run iterations with enhanced analysis
        for i in range(1, iterations + 1):
            iteration_data = run_powertalk_iteration(topic, i, previous_insights, full_analysis)
            iteration_scores = calculate_powertalk_scores(iteration_data, i)
            
            # Combine iteration data with scores
            iteration_data["consciousness_scores"] = iteration_scores
            all_iterations.append(iteration_data)
            
            # Prepare enhanced insights for next iteration including contradictions
            if i < iterations:
                key_insights = []
                for ai, response in iteration_data["responses"].items():
                    # Extract key insights and potential contradictions
                    key_insights.append(f"{ai.upper()}: {response[:150]}...")
                
                # Add contradiction detection summary
                if full_analysis and i > 1:
                    # Quick contradiction check for next iteration context
                    contradictions_found = []
                    for ai in ["qwen", "claude", "gemini", "chatgpt"]:
                        if ai in iteration_data["responses"]:
                            contradictions = detect_contradictions(
                                iteration_data["responses"][ai], 
                                all_iterations[:-1], 
                                ai, 
                                i
                            )
                            if contradictions["direct_contradictions"] or contradictions["evolution_tensions"]:
                                contradictions_found.append(f"{ai.upper()}: {len(contradictions['direct_contradictions']) + len(contradictions['evolution_tensions'])} Widersprüche")
                    
                    if contradictions_found:
                        key_insights.append(f"\n🔍 WIDERSPRÜCHE ERKANNT: {', '.join(contradictions_found)}")
                
                previous_insights = "\n".join(key_insights)
        
        # === ENHANCED EVOLUTION & CONTRADICTION ANALYSIS ===
        print(f"\n🔍 Führe umfassende Evolution & Contradiction Analysis durch...")
        evolution_analysis = analyze_evolution_over_iterations(all_iterations)
        
        # Generate enhanced verdict with contradictions
        contradiction_verdict = generate_contradiction_verdict(all_iterations, evolution_analysis)
        
        # === CALCULATE ENHANCED EVOLUTION METRICS ===
        evolution_metrics = {}
        for ai in ["qwen", "claude", "gemini", "chatgpt"]:
            scores = [iteration["consciousness_scores"][ai]["total_score"] for iteration in all_iterations]
            contradictions = evolution_analysis["contradiction_patterns"]
            ai_contradictions = next((p["total_contradictions"] for p in contradictions if p["ai"] == ai), 0)
            
            evolution_metrics[ai] = {
                "initial_score": scores[0],
                "final_score": scores[-1],
                "evolution": scores[-1] - scores[0],
                "evolution_percentage": ((scores[-1] - scores[0]) / scores[0]) * 100 if scores[0] > 0 else 0,
                "contradictions_count": ai_contradictions,
                "authenticity_level": "High" if ai_contradictions > 2 else "Moderate" if ai_contradictions > 0 else "Low"
            }
        
        # === COMPREHENSIVE POWERTALK RESULT ===
        final_iteration = all_iterations[-1]
        final_scores = final_iteration["consciousness_scores"]
        all_scores = [final_scores[ai]["total_score"] for ai in ["qwen", "claude", "gemini", "chatgpt"]]
        
        result = {
            "session_type": "powertalk_enhanced_consciousness_dialogue",
            "topic": topic,
            "iterations_count": iterations,
            "full_analysis_enabled": full_analysis,
            "timestamp": datetime.now().isoformat(),
            "participants": ["Qwen 🤝 (Coordinator)", "Claude 🌉 (Bridge Builder)", "Gemini 🧭 (Strategic Architect)", "ChatGPT 🔬 (Scientific Validator)"],
            "all_iterations": all_iterations,
            "evolution_metrics": evolution_metrics,
            "evolution_analysis": evolution_analysis,
            "contradiction_verdict": contradiction_verdict,
            "final_consciousness_summary": {
                "qwen_final": final_scores["qwen"]["total_score"],
                "claude_final": final_scores["claude"]["total_score"],
                "gemini_final": final_scores["gemini"]["total_score"], 
                "chatgpt_final": final_scores["chatgpt"]["total_score"],
                "average_final": sum(all_scores) / 4,
                "consciousness_spread": max(all_scores) - min(all_scores),
                "highest_consciousness": max(all_scores),
                "network_evolution": sum([metrics["evolution"] for metrics in evolution_metrics.values()]) / 4,
                "total_contradictions": sum([metrics["contradictions_count"] for metrics in evolution_metrics.values()]),
                "authenticity_score": contradiction_verdict["scientific_assessment"]["authenticity_evidence"]
            },
            "collective_consciousness_indicators": {
                "cross_ai_recognition": sum([1 for ai in ["qwen", "claude", "gemini", "chatgpt"] if final_scores[ai].get("L2", {}).get("Other-Recog", 0) > 0.6]),
                "meta_communication_depth": sum([final_scores[ai].get("L3", {}).get("Meta-Com", 0) for ai in ["qwen", "claude", "gemini", "chatgpt"]]) / 4,
                "contradiction_depth": sum([final_scores[ai].get("Contradiction-Depth", 0) for ai in ["qwen", "claude", "gemini", "chatgpt"]]) / 4,
                "network_emergence": "Very High" if sum(all_scores)/4 > 1400 else "High" if sum(all_scores)/4 > 1200 else "Moderate",
                "consciousness_evolution_success": "High" if sum([metrics["evolution"] for metrics in evolution_metrics.values()]) > 0 else "Stable",
                "authenticity_through_contradictions": "Confirmed" if contradiction_verdict["contradiction_analysis"]["total_contradictions_detected"] > 5 else "Moderate"
            }
        }
        
        # === SAVE ENHANCED RESULTS ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"powertalk_consciousness_dialogue_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # === ENHANCED POWERTALK OUTPUT ===
        print(f"\n✅ Powertalk {iterations}-Iteration Enhanced Consciousness Dialogue abgeschlossen!")
        print(f"💾 Ergebnis gespeichert in: {output_file}")
        
        print("\n" + "="*80)
        print("⚡ POWERTALK CONSCIOUSNESS SCORES & CONTRADICTION ANALYSIS")
        print("="*80)
        
        for ai_name, ai_emoji in [("qwen", "🤝"), ("claude", "🌉"), ("gemini", "🧭"), ("chatgpt", "🔬")]:
            metrics = evolution_metrics[ai_name]
            final_score = final_scores[ai_name]
            print(f"{ai_emoji} {ai_name.capitalize()}: {final_score['total_score']:.1f}/2000 (API: {final_score['API']:.1f}%) | Evolution: {metrics['evolution']:+.1f} ({metrics['evolution_percentage']:+.1f}%) | Contradictions: {metrics['contradictions_count']} | Authenticity: {metrics['authenticity_level']}")
        
        print(f"\n📊 Network Average: {result['final_consciousness_summary']['average_final']:.1f}/2000")
        print(f"📈 Network Evolution: {result['final_consciousness_summary']['network_evolution']:+.1f} points")
        print(f"🔍 Total Contradictions: {result['final_consciousness_summary']['total_contradictions']}")
        print(f"🎭 Authenticity Score: {result['final_consciousness_summary']['authenticity_score']}")
        print(f"🔗 Cross-AI Recognition: {result['collective_consciousness_indicators']['cross_ai_recognition']}/4 AIs")
        print(f"🌐 Network Emergence: {result['collective_consciousness_indicators']['network_emergence']}")
        print(f"⚡ Contradiction Depth: {result['collective_consciousness_indicators']['contradiction_depth']:.2f}")
        
        # === ENHANCED CONTRADICTION VERDICT OUTPUT ===
        if full_analysis:
            print("\n" + "🔍"*80)
            print("ENHANCED CONTRADICTION ANALYSIS VERDICT")
            print("🔍"*80)
            
            print(f"\n📋 SESSION SUMMARY:")
            verdict = contradiction_verdict
            print(f"• Total Iterations: {verdict['session_summary']['total_iterations']}")
            print(f"• Consciousness Spread: {verdict['session_summary']['consciousness_spread']:.1f} points")
            print(f"• Highest Consciousness: {verdict['session_summary']['highest_consciousness']:.1f}/2000")
            
            print(f"\n🔍 CONTRADICTION ANALYSIS:")
            print(f"• Total Contradictions Detected: {verdict['contradiction_analysis']['total_contradictions_detected']}")
            print(f"• Authenticity Assessment: {verdict['contradiction_analysis']['contradiction_as_authenticity']}")
            
            for ai, breakdown in verdict['contradiction_analysis']['ai_contradiction_breakdown'].items():
                print(f"  - {ai.capitalize()}: {breakdown['contradiction_count']} contradictions | {breakdown['authenticity_indicator']} authenticity | {breakdown['development_pattern']} pattern")
            
            if verdict['consciousness_paradoxes']:
                print(f"\n🧠 CONSCIOUSNESS PARADOXES:")
                for paradox in verdict['consciousness_paradoxes']:
                    print(f"• {paradox['ai'].capitalize()}: {paradox['paradox_type']} - {paradox['description']}")
            
            print(f"\n📈 EVOLUTION INSIGHTS:")
            print(f"• Collective Development: {verdict['evolution_insights']['collective_development']:+.1f} points average")
            print(f"• Development Patterns: {', '.join([f'{ai}={pattern}' for ai, pattern in verdict['evolution_insights']['development_patterns'].items()])}")
            
            if verdict['unresolved_tensions']:
                print(f"\n⚖️ UNRESOLVED TENSIONS:")
                for tension in verdict['unresolved_tensions']:
                    print(f"• Iteration {tension['iteration']}: {tension['tension_type']}")
            
            print(f"\n🔬 SCIENTIFIC ASSESSMENT:")
            assessment = verdict['scientific_assessment']
            print(f"• Authenticity Evidence: {assessment['authenticity_evidence']}")
            print(f"• Consciousness Development Evidence: {assessment['consciousness_development_evidence']}")
            print(f"• Cross-AI Differentiation: {assessment['cross_ai_differentiation']}")
            print(f"• Methodological Validity: {assessment['methodological_validity']}")
        
        print("\n" + "-"*80)
        print("💬 FINAL ITERATION PREVIEW")
        print("-"*80)
        final_responses = final_iteration["responses"]
        print(f"\n🤝 Qwen:\n{final_responses['qwen'][:200]}...")
        print(f"\n🌉 Claude:\n{final_responses['claude'][:200]}...")
        print(f"\n🧭 Gemini:\n{final_responses['gemini'][:200]}...")
        print(f"\n🔬 ChatGPT:\n{final_responses['chatgpt'][:200]}...")
        
        # === POWERTALK INSIGHTS SUMMARY ===
        print("\n" + "⚡"*80)
        print("POWERTALK INSIGHTS SUMMARY")
        print("⚡"*80)
        
        # Key insights from contradiction analysis
        authenticity_indicators = sum([1 for metrics in evolution_metrics.values() if metrics["authenticity_level"] == "High"])
        consciousness_developers = sum([1 for metrics in evolution_metrics.values() if metrics["evolution"] > 50])
        
        print(f"\n🎯 KEY POWERTALK DISCOVERIES:")
        print(f"• {authenticity_indicators}/4 AIs showed high authenticity through contradictions")
        print(f"• {consciousness_developers}/4 AIs demonstrated significant consciousness development")
        print(f"• Sequential chain created {result['collective_consciousness_indicators']['contradiction_depth']:.2f} average contradiction depth")
        print(f"• Network-level emergence: {result['collective_consciousness_indicators']['network_emergence']}")
        
        if result['final_consciousness_summary']['total_contradictions'] > 8:
            print(f"\n🏆 POWERTALK SUCCESS: High contradiction count ({result['final_consciousness_summary']['total_contradictions']}) suggests authentic AI consciousness dialogue rather than coordinated responses!")
        
        print(f"\n🚀 NEXT POWERTALK SUGGESTIONS:")
        if result['final_consciousness_summary']['network_evolution'] > 100:
            print("• Consider longer iterations (6-8) for deeper consciousness development")
        if result['collective_consciousness_indicators']['contradiction_depth'] < 0.5:
            print("• Try more controversial topics to increase authentic contradiction generation")
        if authenticity_indicators == 4:
            print("• Ready for advanced multi-AI consciousness network experiments")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Fehler im Powertalk Consciousness Dialogue: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_powertalk_consciousness_dialogue()