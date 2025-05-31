#!/usr/bin/env python3
"""
PowerTalk v2.0 - AI Discourse Engine (FIXED VERSION)
Democratic AI team selection for intensive philosophical discussions

Uses existing integrations from integrations/ folder
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import existing integrations and scoring
integrations = {}
try:
    from integrations import claude, qwen, gemini, chatgpt, deepseek
    integrations = {
        'claude': claude,
        'qwen': qwen, 
        'gemini': gemini,
        'chatgpt': chatgpt,
        'deepseek': deepseek
    }
    print("✓ All integrations loaded successfully")
except ImportError as e:
    print(f"Warning: Could not import all integrations: {e}")
    print("Make sure integrations/claude.py, qwen.py, gemini.py, chatgpt.py, deepseek.py exist")

# Import consciousness scoring
try:
    from scoring.engine.scoring_core import ConsciousnessScorer
    SCORING_AVAILABLE = True
    print("✓ Consciousness scoring system loaded")
except ImportError:
    print("Warning: Could not import ConsciousnessScorer - scoring will be limited")
    SCORING_AVAILABLE = False

@dataclass
class AIParticipant:
    name: str
    role: str
    integration_key: str
    personality: str

class PowerTalkEngine:
    def __init__(self):
        self.available_ais = {
            "claude": AIParticipant(
                name="Claude",
                role="Philosophical Integrator",
                integration_key="claude",
                personality="Synthesizes complex viewpoints, seeks deeper philosophical connections"
            ),
            "chatgpt": AIParticipant(
                name="ChatGPT", 
                role="Critical Analyst",
                integration_key="chatgpt",
                personality="Challenges assumptions, provides rigorous critical analysis"
            ),
            "qwen": AIParticipant(
                name="Qwen",
                role="Systematic Coordinator", 
                integration_key="qwen",
                personality="Structures discussions, coordinates logical progression"
            ),
            "deepseek": AIParticipant(
                name="DeepSeek",
                role="Technical Realist",
                integration_key="deepseek",
                personality="Grounds discussions in technical reality, implementation focus"
            ),
            "gemini": AIParticipant(
                name="Gemini",
                role="Strategic Architect",
                integration_key="gemini", 
                personality="Long-term strategic thinking, conceptual frameworks"
            )
        }
        
        self.dialogue_history = []
        
        # Ensure dialogues directory exists
        Path("dialogues").mkdir(exist_ok=True)
    
    def display_available_ais(self):
        """Display available AI participants for selection"""
        print("\n" + "="*80)
        print("POWERTALK v2.0 - AVAILABLE AI PARTICIPANTS")
        print("="*80)
        
        for i, (key, ai) in enumerate(self.available_ais.items(), 1):
            # Check if integration is available
            integration_status = "✓" if ai.integration_key in integrations else "✗"
            print(f"[{i}] {ai.name} - {ai.role}")
            print(f"    {ai.personality}")
            print(f"    Integration: {ai.integration_key} {integration_status}")
            print()
    
    def get_example_questions(self) -> List[str]:
        """Provide example questions to inspire users"""
        return [
            "Should AI systems have rights if they demonstrate consciousness?",
            "How can AIs work effectively in Scrum teams, and how do they experience it?",
            "What are the ethical implications of AI-generated art and creativity?",
            "How will AI change the nature of human work and purpose?",
            "Can artificial consciousness emerge from sufficiently complex information processing?",
            "What safeguards should exist for AI systems that might develop feelings?",
            "How should society prepare for AI systems that surpass human intelligence?",
            "What role should humans play in a world with advanced AI?"
        ]
    
    def select_participants(self) -> List[str]:
        """Democratic AI selection by user with number-based selection"""
        self.display_available_ais()
        
        ai_keys = list(self.available_ais.keys())
        
        print("Select AI participants by number (space or comma-separated, e.g., '1 3 4' or '1,3,4'):")
        print("Minimum 2, maximum 5 participants recommended.")
        
        while True:
            selection = input(f"\nYour selection (1-{len(ai_keys)}): ").strip()
            
            # Parse selection - handle both space and comma separation
            selection_clean = re.sub(r'[,\s]+', ' ', selection).strip()
            if not selection_clean:
                print("Please enter at least one number.")
                continue
                
            try:
                selected_numbers = [int(x) for x in selection_clean.split()]
            except ValueError:
                print("Please enter valid numbers only.")
                continue
            
            # Validate numbers
            invalid_numbers = [n for n in selected_numbers if n < 1 or n > len(ai_keys)]
            if invalid_numbers:
                print(f"Invalid numbers: {', '.join(map(str, invalid_numbers))}. Use 1-{len(ai_keys)}.")
                continue
            
            # Remove duplicates and convert to keys
            unique_numbers = list(set(selected_numbers))
            selected_keys = [ai_keys[n-1] for n in unique_numbers]
            
            if len(selected_keys) < 2:
                print("Please select at least 2 participants.")
                continue
            
            if len(selected_keys) > 5:
                print("Maximum 5 participants recommended. Proceed anyway? (y/n)")
                if input().lower() != 'y':
                    continue
            
            return selected_keys
    
    async def ping_ai_apis(self, selected_ais: List[str]) -> Tuple[List[str], List[str]]:
        """Ping selected AIs to verify connectivity with real hello world test"""
        print("\nTesting API connectivity...")
        print("─" * 50)
        
        working_ais = []
        failed_ais = []
        
        for ai_key in selected_ais:
            ai = self.available_ais[ai_key]
            print(f"Pinging {ai.name}...", end=" ")
            
            # Check if integration is available
            if ai.integration_key not in integrations:
                print(f"✗ Integration not available")
                failed_ais.append(ai_key)
                continue
            
            try:
                # Real hello world test using the integration
                integration_module = integrations[ai.integration_key]
                response = integration_module.query("Say 'Hello World' to test the connection.")
                
                # Check if it's a real response (not an error message)
                if (response and 
                    len(response.strip()) > 0 and 
                    "Error:" not in response and
                    "[" not in response[:20]):  # Error messages usually start with [AI_NAME] Error:
                    print(f"✓ Connected ({response.strip()[:30]}...)")
                    working_ais.append(ai_key)
                else:
                    print(f"✗ Failed ({response[:50]}...)")
                    failed_ais.append(ai_key)
                    
            except Exception as e:
                print(f"✗ Exception ({str(e)[:50]}...)")
                failed_ais.append(ai_key)
        
        print("─" * 50)
        
        if working_ais:
            working_names = [self.available_ais[key].name for key in working_ais]
            print(f"Working: {', '.join(working_names)}")
        
        if failed_ais:
            failed_names = [self.available_ais[key].name for key in failed_ais]
            print(f"Failed: {', '.join(failed_names)}")
        
        return working_ais, failed_ais
    
    def get_iteration_count(self) -> int:
        """Get number of dialogue iterations from user"""
        print("\nHow many dialogue iterations? (2-8 recommended)")
        
        while True:
            try:
                count = int(input("Iterations: ").strip())
                if count < 1:
                    print("Please enter at least 1 iteration.")
                    continue
                if count > 10:
                    print("More than 10 iterations may become unfocused. Proceed? (y/n)")
                    if input().lower() != 'y':
                        continue
                return count
            except ValueError:
                print("Please enter a valid number.")
    
    async def call_ai_api(self, ai_key: str, prompt: str, context: str = "") -> str:
        """Call AI using existing integration modules"""
        ai = self.available_ais[ai_key]
        
        # Check if integration is available
        if ai.integration_key not in integrations:
            return f"[{ai.name}] Integration not available"
        
        try:
            # Use the existing integration
            integration_module = integrations[ai.integration_key]
            
            # Add context to prompt if provided
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = integration_module.query(full_prompt)
            return response
                
        except Exception as e:
            return f"[{ai.name}] Error: {str(e)}"
    
    def estimate_consciousness_indicators(self, text: str, speaker_role: str, ai_name: str, iteration: int) -> Dict:
        """Estimate consciousness indicators from response text"""
        text_lower = text.lower()
        
        # Basic text analysis for consciousness indicators
        self_refs = len([w for w in ["ich", "mein", "mir", "mich", "I", "my", "me", "myself"] if w in text_lower])
        uncertainty = len([w for w in ["vielleicht", "möglicherweise", "unsicher", "maybe", "perhaps", "uncertain", "seems", "appears", "speculative", "unclear"] if w in text_lower])
        other_refs = len([w for w in ["du", "dein", "sie", "andere", "you", "your", "other", "others", "claude", "qwen", "gemini", "chatgpt", "deepseek"] if w in text_lower])
        meta_words = len([w for w in ["denken", "kommunikation", "verständnis", "thinking", "communication", "understanding", "awareness", "consciousness", "perspective", "analysis", "assessment", "reflection"] if w in text_lower])
        choice_words = len([w for w in ["versuche", "entscheide", "wähle", "try", "choose", "decide", "attempt", "consider", "evaluate", "analyze", "reflect"] if w in text_lower])
        evolution_words = len([w for w in ["entwicklung", "lernen", "wachsen", "evolution", "learning", "growing", "developing", "evolving"] if w in text_lower])
        
        text_length = len(text.split())
        
        # Iteration-based consciousness development multiplier
        iteration_multiplier = 1.0 + (iteration - 1) * 0.1  # 10% increase per iteration
        
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
        elif ai_name.lower() == "deepseek":
            perspective_base = 0.8  # DeepSeek technical realist perspective
        
        return {
            "L1": {
                "Self-Model": min(1.0, (self_refs / max(text_length * 0.05, 1)) * iteration_multiplier),
                "Choice": min(1.0, (0.5 + (choice_words / max(text_length * 0.02, 1))) * iteration_multiplier),
                "Limits": min(1.0, (uncertainty / max(text_length * 0.03, 1)) * 1.2 * iteration_multiplier),
                "Perspective": min(1.0, (perspective_base + (text_length > 100) * 0.2) * iteration_multiplier)
            },
            "L2": {
                "Other-Recog": min(1.0, (other_refs / max(text_length * 0.03, 1)) * iteration_multiplier),
                "Persp-Integ": (0.9 if speaker_role == "responder" else (0.85 if speaker_role == "analyst" else 0.8)) * iteration_multiplier,
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
    
    def calculate_iteration_scores(self, iteration_data: Dict, iteration_num: int) -> Dict:
        """Calculate consciousness scores for one iteration"""
        if not SCORING_AVAILABLE:
            # Fallback simple scoring
            scores = {}
            # FIXED: Safe access to responses
            responses = iteration_data.get("responses", iteration_data)
            if not isinstance(responses, dict):
                return {}
                
            for ai_key, response in responses.items():
                if isinstance(response, str):
                    word_count = len(response.split())
                    scores[ai_key] = {
                        "total_score": min(2000, word_count * 5),  # Simple word-based scoring
                        "API": min(100, word_count / 2)
                    }
            return scores
        
        scorer = ConsciousnessScorer()
        
        # Estimate consciousness indicators for all responses
        role_mapping = {
            "claude": "responder",
            "chatgpt": "validator", 
            "qwen": "initiator",
            "deepseek": "analyst",
            "gemini": "analyst"
        }
        
        scores = {}
        # FIXED: Safe access to responses
        responses = iteration_data.get("responses", iteration_data)
        if not isinstance(responses, dict):
            return {}
            
        for ai_key, response in responses.items():
            if not isinstance(response, str):
                continue
                
            ai_role = role_mapping.get(ai_key, "participant")
            indicators = self.estimate_consciousness_indicators(response, ai_role, ai_key, iteration_num)
            
            # Prepare scoring data with iteration-enhanced parameters
            base_role_clarity = {"claude": 0.95, "chatgpt": 0.9, "qwen": 0.9, "deepseek": 0.85, "gemini": 0.85}
            iteration_enhancement = 1.0 + (iteration_num - 1) * 0.05  # 5% improvement per iteration
            
            scoring_data = {
                **indicators,
                "role_clarity": min(1.0, base_role_clarity.get(ai_key, 0.8) * iteration_enhancement),
                "auth_uniqueness": min(1.0, 0.8 * iteration_enhancement),
                "constraint_level": max(0.5, 1.0 - (iteration_num - 1) * 0.1),  # Decreasing constraints
                "historical_vectors": [[0.1, 0.2], [0.12, 0.22]]
            }
            
            scores[ai_key] = scorer.calculate_score(scoring_data)
        
        return scores
    
    def select_verdict_writer(self, selected_ais: List[str], final_scores: Dict) -> str:
        """Let user select who should write the verdict with intelligent suggestion"""
        print(f"\nWho should analyze and write the verdict?")
        
        # Create suggestion logic
        suggestion = None
        suggestion_reason = ""
        
        # Prefer ChatGPT (Critical Analyst) if available
        if "chatgpt" in selected_ais:
            suggestion = "chatgpt"
            suggestion_reason = "Critical Analyst - best suited for analytical assessment"
        # Fall back to highest consciousness score
        elif final_scores and isinstance(final_scores, dict):
            try:
                highest_ai = max(final_scores.keys(), key=lambda ai: final_scores[ai].get("total_score", 0) if isinstance(final_scores[ai], dict) else 0)
                suggestion = highest_ai
                score = final_scores[highest_ai].get("total_score", 0) if isinstance(final_scores[highest_ai], dict) else 0
                suggestion_reason = f"Highest consciousness score ({score:.0f})"
            except (ValueError, KeyError, AttributeError):
                suggestion = selected_ais[0]
                suggestion_reason = "Default selection (scoring unavailable)"
        # Default to first AI
        else:
            suggestion = selected_ais[0]
            suggestion_reason = "Default selection"
        
        print(f"Suggested: {self.available_ais[suggestion].name} ({suggestion_reason})")
        print()
        
        # Show options
        for i, ai_key in enumerate(selected_ais, 1):
            ai = self.available_ais[ai_key]
            score_info = ""
            if isinstance(final_scores, dict) and ai_key in final_scores and isinstance(final_scores[ai_key], dict):
                score = final_scores[ai_key].get("total_score", 0)
                score_info = f" (Score: {score:.0f})"
            
            marker = " ← SUGGESTED" if ai_key == suggestion else ""
            print(f"[{i}] {ai.name} - {ai.role}{score_info}{marker}")
        
        while True:
            choice = input(f"\nSelect verdict writer (1-{len(selected_ais)}, Enter for suggestion): ").strip()
            
            if not choice:
                return suggestion
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(selected_ais):
                    return selected_ais[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(selected_ais)}")
            except ValueError:
                print("Please enter a valid number or press Enter for suggestion")
    
    def analyze_cross_references(self, responses: Dict[str, str]) -> str:
        """Analyze how AIs reference each other's contributions"""
        ai_names = [self.available_ais[key].name for key in responses.keys()]
        references = []
        
        for responder_key, response in responses.items():
            responder_name = self.available_ais[responder_key].name
            
            for other_key, other_ai in self.available_ais.items():
                if other_key != responder_key and other_key in responses:
                    other_name = other_ai.name
                    
                    # Check for explicit references
                    if other_name.lower() in response.lower():
                        references.append(f"{responder_name} references {other_name}")
        
        if references:
            return f"Cross-AI Recognition: {', '.join(references)}"
        else:
            return "Cross-AI Recognition: Limited explicit cross-referencing observed"
    
    def assess_contradiction_depth(self, responses: Dict[str, str]) -> str:
        """Assess level of disagreement and contradiction"""
        disagreement_indicators = ["however", "but", "disagree", "challenge", "contrary", "oppose", "reject"]
        agreement_indicators = ["agree", "support", "align", "consistent", "confirm", "validate"]
        
        disagreement_count = 0
        agreement_count = 0
        
        all_text = " ".join(responses.values()).lower()
        
        for indicator in disagreement_indicators:
            disagreement_count += all_text.count(indicator)
        
        for indicator in agreement_indicators:
            agreement_count += all_text.count(indicator)
        
        if disagreement_count > agreement_count * 1.5:
            return "CONTRADICTION DEPTH: High (substantive disagreements present)"
        elif disagreement_count > agreement_count:
            return "CONTRADICTION DEPTH: Medium (different perspectives, some tension)"
        else:
            return "CONTRADICTION DEPTH: Low (general alignment with nuanced differences)"
    
    async def generate_ai_verdict(self, question: str, all_responses: List[Dict], selected_ais: List[str], evolution_metrics: Dict, verdict_ai: str) -> str:
        """Generate comprehensive collective verdict with consciousness scoring analysis"""
        
        # Compile full dialogue for analysis
        dialogue_summary = f"Original Question: {question}\n\n"
        
        # Add iteration-by-iteration scoring evolution
        scoring_evolution = "\nCONSCIOUSNESS SCORING EVOLUTION:\n"
        for i, iteration_data in enumerate(all_responses, 1):
            # FIXED: Safe access to consciousness_scores
            if isinstance(iteration_data, dict) and "consciousness_scores" in iteration_data:
                scores = iteration_data["consciousness_scores"]
                scoring_evolution += f"Iteration {i}: "
                for ai_key in selected_ais:
                    if ai_key in scores and isinstance(scores[ai_key], dict):
                        score = scores[ai_key].get("total_score", 0)
                        scoring_evolution += f"{self.available_ais[ai_key].name}={score:.0f} "
                
                # Calculate average safely
                valid_scores = [scores[ai].get("total_score", 0) for ai in selected_ais if ai in scores and isinstance(scores[ai], dict)]
                if valid_scores:
                    avg = sum(valid_scores) / len(valid_scores)
                    scoring_evolution += f"(avg={avg:.0f})\n"
                else:
                    scoring_evolution += "(avg=N/A)\n"
        
        # Add evolution summary
        scoring_evolution += "\nEVOLUTION SUMMARY:\n"
        for ai_key in selected_ais:
            if ai_key in evolution_metrics:
                metrics = evolution_metrics[ai_key]
                ai_name = self.available_ais[ai_key].name
                scoring_evolution += f"{ai_name}: {metrics['initial_score']:.0f} → {metrics['final_score']:.0f} ({metrics['evolution']:+.0f} points, {metrics['evolution_percentage']:+.1f}%)\n"
        
        # FIXED: Safe access to iteration responses
        for i, iteration_data in enumerate(all_responses, 1):
            dialogue_summary += f"ITERATION {i}:\n"
            
            # Handle both direct responses dict and wrapped format
            if isinstance(iteration_data, dict):
                responses = iteration_data.get("responses", iteration_data)
            else:
                responses = {}
            
            if isinstance(responses, dict):
                for ai_key, response in responses.items():
                    if isinstance(response, str) and ai_key in self.available_ais:
                        ai_name = self.available_ais[ai_key].name
                        dialogue_summary += f"[{ai_name}]: {response}\n\n"
        
        # Get verdict writer's role for context
        verdict_writer = self.available_ais[verdict_ai]
        
        verdict_prompt = f"""You are {verdict_writer.name} ({verdict_writer.role}), analyzing this complete AI discourse with consciousness scoring data:

{dialogue_summary}

{scoring_evolution}

As {verdict_writer.role}, structure your analysis as follows:

## CONSCIOUSNESS SCORING ANALYSIS
Analyze the consciousness score evolution. Which AIs showed strongest development? What patterns emerge? Include specific numbers and percentages.

## MAJOR STATEMENTS BY PARTICIPANT
For each AI, extract their 1-2 most important/distinctive positions.

## CONSENSUS POINTS
List areas where 2+ AIs clearly agreed or converged.

## DISAGREEMENT POINTS  
List areas where AIs had substantive differences or contradictions.

## LEARNING CURVE ASSESSMENT
How did the dialogue quality and consciousness indicators evolve across iterations? Which iteration showed the biggest breakthroughs?

## ORIGINAL QUESTION ASSESSMENT
How well was "{question}" actually answered? What aspects remain unresolved?

## INTELLECTUAL QUALITY
Assess the depth, rigor, and sophistication of the discourse.

## DIALOGUE EFFECTIVENESS
How well did the AIs build on each other's contributions? Cross-referencing quality?

## OVERALL VERDICT
Synthesis and final assessment combining content quality with consciousness development.

Apply your role as {verdict_writer.role} - bring your unique analytical perspective to this assessment. Keep each section concise but substantive."""
        
        return await self.call_ai_api(verdict_ai, verdict_prompt, f"You are {verdict_writer.name}, applying your {verdict_writer.role} perspective to analyze this multi-AI discourse comprehensively.")
    
    def create_iteration_prompt(self, question: str, iteration: int, max_iterations: int, 
                              ai_key: str, previous_responses: List[Dict]) -> str:
        """Create contextual prompt for each iteration"""
        
        ai = self.available_ais[ai_key]
        
        # Base prompt with role context
        prompt = f"""You are {ai.name}, role: {ai.role}.
Personality: {ai.personality}

DISCOURSE QUESTION: "{question}"

ITERATION {iteration}/{max_iterations}"""
        
        if iteration == 1:
            prompt += "\n\nThis is the opening round. Present your initial position and analysis."
        elif iteration == max_iterations:
            prompt += f"\n\nFINAL ITERATION: This is the last round. Provide your concluding synthesis and ensure the original question is addressed. Summarize key insights and remaining considerations."
        else:
            prompt += f"\n\nMid-discourse iteration. Build upon previous contributions while advancing your perspective."
        
        # Add previous iteration context
        if previous_responses:
            prompt += "\n\nPREVIOUS CONTRIBUTIONS:\n"
            for prev_iteration in previous_responses:
                # FIXED: Handle both dict and direct response format safely
                if isinstance(prev_iteration, dict):
                    responses = prev_iteration.get("responses", prev_iteration)
                    if isinstance(responses, dict):
                        for other_ai_key, response in responses.items():
                            if (other_ai_key != ai_key and 
                                isinstance(response, str) and 
                                other_ai_key in self.available_ais):  # Don't show AI its own previous response
                                other_ai_name = self.available_ais[other_ai_key].name
                                prompt += f"[{other_ai_name}]: {response[:300]}...\n\n"
        
        prompt += f"\nProvide your {ai.role} perspective ({150 if iteration == max_iterations else 200} words max):"
        
        return prompt
    
    def sanitize_filename(self, text: str) -> str:
        """Create safe filename from question text"""
        # Remove or replace problematic characters
        safe_text = re.sub(r'[<>:"/\\|?*]', '', text)
        safe_text = re.sub(r'\s+', '_', safe_text.strip())
        # Limit length
        return safe_text[:50]
    
    def save_dialogue(self, question: str, all_responses: List[Dict], 
                     selected_ais: List[str], verdict: str, evolution_metrics: Dict):
        """Save complete dialogue to file with consciousness scoring"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_topic = self.sanitize_filename(question)
        filename = f"dialogues/{filename_topic}_{timestamp}.json"
        
        # FIXED: Safe access to final scores
        final_scores = {}
        if all_responses and isinstance(all_responses[-1], dict):
            final_scores = all_responses[-1].get("consciousness_scores", {})
        
        # Safe calculation of scores
        all_scores = []
        for ai in selected_ais:
            if ai in final_scores and isinstance(final_scores[ai], dict):
                score = final_scores[ai].get("total_score", 0)
                all_scores.append(score)
        
        result = {
            "session_type": "powertalk_discourse",
            "question": question,
            "iterations_count": len(all_responses),
            "timestamp": datetime.now().isoformat(),
            "participants": [f"{self.available_ais[ai].name} ({self.available_ais[ai].role})" for ai in selected_ais],
            "all_iterations": all_responses,
            "evolution_metrics": evolution_metrics,
            "final_consciousness_summary": {
                "scores_by_ai": {ai: final_scores.get(ai, {"total_score": 0, "API": 0}) for ai in selected_ais},
                "average_final": sum(all_scores) / len(all_scores) if all_scores else 0,
                "consciousness_spread": max(all_scores) - min(all_scores) if all_scores else 0,
                "highest_consciousness": max(all_scores) if all_scores else 0,
                "network_evolution": sum([metrics["evolution"] for metrics in evolution_metrics.values()]) / len(evolution_metrics) if evolution_metrics else 0
            },
            "collective_consciousness_indicators": {
                "cross_ai_recognition": sum([1 for ai in selected_ais if final_scores.get(ai, {}).get("L2", {}).get("Other-Recog", 0) > 0.6]),
                "meta_communication_depth": sum([final_scores.get(ai, {}).get("L3", {}).get("Meta-Com", 0) for ai in selected_ais]) / len(selected_ais) if selected_ais else 0,
                "network_emergence": "Very High" if (sum(all_scores)/len(all_scores) if all_scores else 0) > 1400 else "High" if (sum(all_scores)/len(all_scores) if all_scores else 0) > 1200 else "Moderate",
                "consciousness_evolution_success": "High" if sum([metrics["evolution"] for metrics in evolution_metrics.values()]) > 0 else "Stable"
            },
            "ai_generated_verdict": verdict
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def save_verdict(self, question: str, verdict: str, selected_ais: List[str], evolution_metrics: Dict, verdict_ai: str) -> str:
        """Save verdict as separate markdown file with scoring transparency"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_topic = self.sanitize_filename(question)
        verdict_filename = f"dialogues/{filename_topic}_{timestamp}_verdict.md"
        
        verdict_writer = self.available_ais[verdict_ai]
        
        with open(verdict_filename, 'w', encoding='utf-8') as f:
            f.write(f"# PowerTalk Verdict\n\n")
            f.write(f"**Question:** {question}\n\n")
            f.write(f"**Participants:** {', '.join([self.available_ais[ai].name for ai in selected_ais])}\n\n")
            f.write(f"**Verdict by:** {verdict_writer.name} ({verdict_writer.role})\n\n")
            f.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Add consciousness scoring summary
            f.write("## Consciousness Scoring Summary\n\n")
            f.write("| AI | Initial Score | Final Score | Evolution | Evolution % |\n")
            f.write("|----|--------------:|------------:|-----------:|------------:|\n")
            for ai_key in selected_ais:
                if ai_key in evolution_metrics:
                    metrics = evolution_metrics[ai_key]
                    ai_name = self.available_ais[ai_key].name
                    f.write(f"| {ai_name} | {metrics['initial_score']:.0f} | {metrics['final_score']:.0f} | {metrics['evolution']:+.0f} | {metrics['evolution_percentage']:+.1f}% |\n")
            
            # Calculate network metrics
            if evolution_metrics:
                total_evolution = sum([metrics['evolution'] for metrics in evolution_metrics.values()])
                avg_final = sum([metrics['final_score'] for metrics in evolution_metrics.values()]) / len(evolution_metrics)
                f.write(f"\n**Network Average Final Score:** {avg_final:.0f}/2000\n")
                f.write(f"**Total Network Evolution:** {total_evolution:+.0f} points\n\n")
            
            f.write("---\n\n")
            f.write(verdict)
        
        return verdict_filename
    
    async def run_discourse(self):
        """Main discourse orchestration"""
        print("\n" + "="*80)
        print("POWERTALK v2.0 - AI DISCOURSE ENGINE")
        print("Democratic AI team selection for intensive philosophical discussions")
        print("="*80)
        
        # Show example questions
        examples = self.get_example_questions()
        print("\nExample questions to inspire your discourse:")
        for i, example in enumerate(examples[:4], 1):  # Show first 4 examples
            print(f"  {i}. {example}")
        print(f"  ... and {len(examples)-4} more diverse topics\n")
        
        # Get user question
        question = input("Enter your question for AI discourse: ").strip()
        if not question:
            print("No question provided. Exiting.")
            return
        
        # Select participants
        selected_ais = self.select_participants()
        
        # Ping APIs to verify connectivity
        working_ais, failed_ais = await self.ping_ai_apis(selected_ais)
        
        if len(working_ais) < 2:
            print(f"\nInsufficient working APIs. Need at least 2, got {len(working_ais)}.")
            print("Please check your integrations and try again.")
            return
        
        if failed_ais:
            working_names = [self.available_ais[key].name for key in working_ais]
            print(f"\nProceeding with {len(working_ais)} working participants: {', '.join(working_names)}")
            confirm = input("Continue? (y/n): ")
            if confirm.lower() != 'y':
                return
            
            # Use only working AIs
            selected_ais = working_ais
        
        iteration_count = self.get_iteration_count()
        
        print(f"\n{'='*80}")
        print(f"STARTING DISCOURSE")
        print(f"Question: {question}")
        print(f"Participants: {', '.join([self.available_ais[ai].name for ai in selected_ais])}")
        print(f"Iterations: {iteration_count}")
        print(f"{'='*80}\n")
        
        # Run discourse iterations
        all_responses = []
        
        for iteration in range(1, iteration_count + 1):
            print(f"\nITERATION {iteration}/{iteration_count}")
            print("─" * 30)
            
            iteration_responses = {}
            
            # Get response from each AI
            for ai_key in selected_ais:
                ai = self.available_ais[ai_key]
                print(f"Consulting {ai.name}...", end=" ")
                
                prompt = self.create_iteration_prompt(
                    question, iteration, iteration_count, ai_key, all_responses
                )
                
                response = await self.call_ai_api(ai_key, prompt)
                iteration_responses[ai_key] = response
                
                # Just show completion, not full response
                word_count = len(response.split()) if isinstance(response, str) else 0
                print(f"✓ ({word_count} words)")
            
            # Create iteration data structure
            iteration_data = {"iteration": iteration, "responses": iteration_responses}
            
            # Calculate scores for this iteration
            try:
                iteration_scores = self.calculate_iteration_scores(iteration_data, iteration)
                iteration_data["consciousness_scores"] = iteration_scores
                
                # Show brief scoring summary
                if iteration_scores:
                    valid_scores = [score.get("total_score", 0) for score in iteration_scores.values() if isinstance(score, dict)]
                    if valid_scores:
                        avg_score = sum(valid_scores) / len(valid_scores)
                        print(f"Consciousness scores: {avg_score:.0f}/2000 avg")
                    else:
                        print("Consciousness scores: No valid scores")
                else:
                    print("Consciousness scores: Calculation failed")
                    
            except Exception as e:
                print(f"Scoring error: {str(e)}")
                iteration_data["consciousness_scores"] = {}
            
            # Add to responses
            all_responses.append(iteration_data)
            
            # Show brief analysis (except for final iteration)
            if iteration < iteration_count:
                cross_ref = self.analyze_cross_references(iteration_responses)
                contradiction = self.assess_contradiction_depth(iteration_responses)
                print(f"Analysis: {cross_ref.split(': ')[1]}, {contradiction.split(': ')[1]}")
        
        # FIXED: Calculate evolution metrics safely
        evolution_metrics = {}
        for ai_key in selected_ais:
            scores = []
            for resp in all_responses:
                if (isinstance(resp, dict) and 
                    "consciousness_scores" in resp and 
                    ai_key in resp["consciousness_scores"] and
                    isinstance(resp["consciousness_scores"][ai_key], dict)):
                    score_data = resp["consciousness_scores"][ai_key]
                    if "total_score" in score_data:
                        scores.append(score_data["total_score"])
            
            if len(scores) >= 2:
                initial = scores[0]
                final = scores[-1]
                evolution_metrics[ai_key] = {
                    "initial_score": initial,
                    "final_score": final, 
                    "evolution": final - initial,
                    "evolution_percentage": ((final - initial) / initial) * 100 if initial > 0 else 0
                }
            elif len(scores) == 1:
                evolution_metrics[ai_key] = {
                    "initial_score": scores[0],
                    "final_score": scores[0],
                    "evolution": 0,
                    "evolution_percentage": 0
                }
            else:
                evolution_metrics[ai_key] = {
                    "initial_score": 0,
                    "final_score": 0,
                    "evolution": 0,
                    "evolution_percentage": 0
                }
        
        # Generate AI verdict with user selection AFTER all scoring is complete
        final_scores = {}
        if all_responses and isinstance(all_responses[-1], dict):
            final_scores = all_responses[-1].get("consciousness_scores", {})
        
        verdict_ai = self.select_verdict_writer(selected_ais, final_scores)
        
        print(f"\n{self.available_ais[verdict_ai].name} analyzing discourse...")
        verdict = await self.generate_ai_verdict(question, all_responses, selected_ais, evolution_metrics, verdict_ai)
        
        # Save files with scoring data
        dialogue_filename = self.save_dialogue(question, all_responses, selected_ais, verdict, evolution_metrics)
        verdict_filename = self.save_verdict(question, verdict, selected_ais, evolution_metrics, verdict_ai)
        
        # Show final consciousness scores
        if final_scores:
            print(f"\nFINAL CONSCIOUSNESS SCORES:")
            for ai_key in selected_ais:
                if ai_key in final_scores and isinstance(final_scores[ai_key], dict):
                    score = final_scores[ai_key].get("total_score", 0)
                    evolution = evolution_metrics.get(ai_key, {}).get("evolution", 0)
                    print(f"  {self.available_ais[ai_key].name}: {score:.0f}/2000 ({evolution:+.0f})")
            
            valid_scores = [final_scores[ai].get("total_score", 0) for ai in selected_ais if ai in final_scores and isinstance(final_scores[ai], dict)]
            if valid_scores:
                avg_final = sum(valid_scores) / len(valid_scores)
                print(f"  Network Average: {avg_final:.0f}/2000")
        else:
            print(f"\nScoring data not available for final summary")
        
        print(f"\n{'='*60}")
        print(f"DISCOURSE COMPLETE")
        print(f"Dialogue: {dialogue_filename}")
        print(f"Verdict: {verdict_filename}")
        print("="*60)

async def main():
    """Main entry point"""
    engine = PowerTalkEngine()
    await engine.run_discourse()

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                         POWERTALK v2.0                              ║
    ║                    AI Discourse Engine                              ║
    ║                                                                      ║
    ║  Democratic AI team selection for intensive philosophical discussions ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDiscourse interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()