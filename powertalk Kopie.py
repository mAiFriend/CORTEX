#!/usr/bin/env python3
"""
PowerTalk v2.2 - AI Discourse Engine with PAI v2.0 Integration
Enhanced with AI-specific handshake optimization and structured communication

Usage:
    python powertalk.py                    # Interactive mode
    python powertalk.py -q question.md     # Question from file
    python powertalk.py --question question.md
"""

import os
import asyncio
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import PAI v2.0 Protocol
try:
    from pai import PAIProtocolV2, PAIResponse
    PAI_AVAILABLE = True
    print("✓ PAI v2.0 Protocol loaded")
except ImportError as e:
    PAI_AVAILABLE = False
    print(f"Warning: PAI v2.0 not available - falling back to basic communication: {e}")

# Import existing integrations and scoring
integrations = {}
integration_load_errors = []
try:
    from integrations import claude, qwen, gemini, chatgpt, deepseek
    
    # Attempt to load each integration individually to catch specific errors
    for module_name in ['claude', 'qwen', 'gemini', 'chatgpt', 'deepseek']:
        try:
            module = sys.modules[f'integrations.{module_name}'] # Get module from sys.modules if already imported
            integrations[module_name] = module
        except KeyError:
            integration_load_errors.append(f"Could not load integration: {module_name}.py (file not found or other import error)")
            
    if integration_load_errors:
        print(f"Warning: Some integrations could not be loaded:")
        for error in integration_load_errors:
            print(f"  ✗ {error}")
    else:
        print("✓ All integrations loaded successfully")
except ImportError as e:
    print(f"Error: Base import failed for integrations directory. Make sure integrations folder exists and is accessible. Details: {e}")
    integration_load_errors.append(f"Base integrations folder import error: {e}")

# Import consciousness scoring
SCORING_AVAILABLE = False
try:
    from scoring.engine.scoring_core import ConsciousnessScorer
    SCORING_AVAILABLE = True
    print("✓ Consciousness scoring system loaded")
except ImportError as e:
    print(f"Warning: Could not import ConsciousnessScorer - scoring will be limited to basic fallback. Details: {e}")

@dataclass
class AIParticipant:
    name: str
    role: str
    integration_key: str
    personality: str

@dataclass
class PAICapability:
    """Track PAI capabilities for each AI"""
    ai_name: str
    supports_structured: bool
    handshake_strategy: str
    protocol_type: str
    response_time: float

class PowerTalkEngine:
    def __init__(self, question_file=None):
        self.question_file = question_file
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
        self.pai_protocol = None
        self.pai_capabilities = {}
        self.enable_pai = PAI_AVAILABLE
        
        # Ensure dialogues directory exists
        Path("dialogues").mkdir(exist_ok=True)
    
    async def establish_pai_handshakes(self, selected_ais: List[str]) -> Dict[str, PAICapability]:
        """Phase 1: Establish PAI communication protocols with each AI"""
        print("\n" + "="*60)
        print("🤝 ESTABLISHING PAI COMMUNICATION PROTOCOLS")
        print("="*60)
        
        if not self.enable_pai:
            print("PAI protocol not available - using basic communication")
            return {}
        
        # Initialize PAI protocol
        if self.pai_protocol is None:
            self.pai_protocol = PAIProtocolV2(enable_logging=True)
        
        pai_capabilities = {}
        
        for ai_key in selected_ais:
            ai = self.available_ais[ai_key]
            print(f"🔗 Establishing PAI handshake with {ai.name}...", end=" ")
            
            try:
                start_time = datetime.now()
                
                # Create async wrapper for integration
                async def ai_caller(message):
                    integration_module = integrations[ai.integration_key]
                    return integration_module.query(message)
                
                # Test PAI handshake
                handshake_response = await self.pai_protocol.communicate(
                    ai_caller=ai_caller,
                    ai_name=ai_key,
                    message="PAI protocol capability test",
                    context="PowerTalk v2.2 handshake"
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                if handshake_response.success:
                    capability = PAICapability(
                        ai_name=ai_key,
                        supports_structured=(handshake_response.protocol_used == "structured"),
                        handshake_strategy=handshake_response.handshake_strategy,
                        protocol_type=handshake_response.protocol_used,
                        response_time=response_time
                    )
                    pai_capabilities[ai_key] = capability
                    
                    protocol_symbol = "📊" if capability.supports_structured else "💬"
                    print(f"✓ {protocol_symbol} {capability.protocol_type} ({capability.handshake_strategy}, {response_time:.1f}s)")
                else:
                    print(f"✗ Handshake failed - using fallback")
                    
            except Exception as e:
                print(f"✗ Error: {str(e)[:50]}...")
        
        # Summary
        structured_count = sum(1 for cap in pai_capabilities.values() if cap.supports_structured)
        natural_count = len(pai_capabilities) - structured_count
        
        print("─" * 60)
        print(f"PAI Handshake Summary:")
        print(f"  📊 Structured Protocol: {structured_count} AIs")
        print(f"  💬 Natural Fallback: {natural_count} AIs")
        print(f"  🚀 Ready for enhanced communication")
        
        self.pai_capabilities = pai_capabilities
        return pai_capabilities
    
    async def translate_human_question_to_pai(self, question: str, pai_capabilities: Dict[str, PAICapability]) -> str:
        """Phase 2: Translate human question to PAI-optimized format"""
        print("\n🔄 TRANSLATING QUESTION TO PAI FORMAT")
        print("─" * 40)
        
        if not pai_capabilities:
            print("No PAI capabilities - using original question")
            return question
        
        # Check if any AIs support structured protocol
        structured_ais = [cap.ai_name for cap in pai_capabilities.values() if cap.supports_structured]
        
        if structured_ais:
            print(f"Creating structured format for: {', '.join([self.available_ais[ai].name for ai in structured_ais])}")
            
            # Create enhanced question with PAI context
            pai_enhanced_question = f"""
{question}

[PAI Protocol Context: Multi-AI discourse with structured communication capabilities]
[Participants: {', '.join([self.available_ais[ai].name for ai in pai_capabilities.keys()])}]
[Protocol Support: {len(structured_ais)} structured, {len(pai_capabilities) - len(structured_ais)} natural]
""".strip()
            
            print(f"✓ Enhanced question with PAI context for optimal AI communication")
            return pai_enhanced_question
        else:
            print("All AIs using natural protocol - enhanced natural format")
            enhanced_question = f"""
{question}

[Enhanced Communication Context: Multi-AI philosophical discourse]
[Focus: Deep analysis with cross-AI perspective integration]
""".strip()
            return enhanced_question
    
    async def pai_enhanced_call_ai_api(self, ai_key: str, prompt: str, context: str = "") -> str:
        """Enhanced AI API call with PAI v2.0 optimization"""
        
        if not self.enable_pai or ai_key not in self.pai_capabilities:
            # Fallback to original method
            return await self.call_ai_api(ai_key, prompt, context)
        
        try:
            # Create async wrapper for existing integration
            async def ai_caller(message):
                return await self.call_ai_api(ai_key, message, "")
            
            # Use established PAI capability
            pai_response = await self.pai_protocol.communicate(
                ai_caller=ai_caller,
                ai_name=ai_key,
                message=prompt,
                context=context
            )
            
            if pai_response.success:
                return pai_response.content
            else:
                # Fallback to original method
                return await self.call_ai_api(ai_key, prompt, context)
                
        except Exception as e:
            print(f"PAI error for {ai_key}, falling back: {str(e)[:50]}...")
            return await self.call_ai_api(ai_key, prompt, context)
    
    def get_question_input(self) -> str:
        """Get question from file or interactive input"""
        if self.question_file:
            try:
                with open(self.question_file, 'r', encoding='utf-8') as f:
                    question = f.read().strip()
                    print(f"Question loaded from {self.question_file}")
                    print(f"Preview: {question[:100]}{'...' if len(question) > 100 else ''}")
                    return question
            except FileNotFoundError:
                print(f"Error: Question file '{self.question_file}' not found.")
                print("Falling back to interactive input...")
            except Exception as e:
                print(f"Error reading question file: {e}")
                print("Falling back to interactive input...")
        
        # Interactive input
        print("\nEnter your question for AI discourse:")
        print("(or provide question file via --question/-q parameter)")
        question = input().strip()
        if not question:
            print("No question provided. Exiting.")
            return ""
        return question
    
    def display_available_ais(self):
        """Display available AI participants for selection"""
        print("\n" + "="*80)
        print("POWERTALK v2.2 - AVAILABLE AI PARTICIPANTS (PAI v2.0 Enhanced)")
        print("="*80)
        
        print("[0] 🌟 ALL LISTED AIs (full team discourse with PAI optimization)")
        print("    Complete multi-perspective analysis with optimized AI-to-AI communication")
        print()
        
        for i, (key, ai) in enumerate(self.available_ais.items(), 1):
            # Check if integration is available
            integration_status_symbol = "✓" if ai.integration_key in integrations else "✗"
            integration_status_text = "Available" if ai.integration_key in integrations else "NOT Available (check integrations folder)"
            print(f"[{i}] {ai.name} - {ai.role}")
            print(f"    {ai.personality}")
            print(f"    Integration: {ai.integration_key} {integration_status_symbol} ({integration_status_text})")
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
        """Enhanced AI selection with ALL option"""
        self.display_available_ais()
        
        ai_keys = list(self.available_ais.keys())
        
        print("Select AI participants by number (space or comma-separated, e.g., '1 3 4' or '1,3,4'):")
        print("Use '0' for ALL AIs or specific numbers for individual selection.")
        print("Minimum 2, maximum 5 participants recommended (unless using ALL option).")
        
        while True:
            selection = input(f"\nYour selection (0 for ALL, or 1-{len(ai_keys)}): ").strip()
            
            # Handle ALL AIs option
            if selection == "0":
                # Check which AIs are actually available
                available_keys = [key for key in ai_keys if key in integrations]
                if len(available_keys) < 2:
                    print(f"Insufficient available AIs to run 'ALL' option. Only {len(available_keys)} working. Need at least 2.")
                    continue
                
                print(f"Selected ALL available AIs: {', '.join([self.available_ais[key].name for key in available_keys])}")
                return available_keys
            
            # Parse individual selection
            selection_clean = re.sub(r'[,\s]+', ' ', selection).strip()
            if not selection_clean:
                print("Please enter at least one number or '0' for ALL.")
                continue
                
            try:
                selected_numbers = [int(x) for x in selection_clean.split()]
            except ValueError:
                print("Please enter valid numbers only.")
                continue
            
            # Validate numbers
            invalid_numbers = [n for n in selected_numbers if n < 1 or n > len(ai_keys)]
            if invalid_numbers:
                print(f"Invalid numbers: {', '.join(map(str, invalid_numbers))}. Use 0 for ALL or 1-{len(ai_keys)}.")
                continue
            
            # Remove duplicates and convert to keys
            unique_numbers = list(set(selected_numbers))
            selected_keys = [ai_keys[n-1] for n in unique_numbers]
            
            # Filter out non-integrated AIs
            selected_keys_filtered = [key for key in selected_keys if key in integrations]
            
            if len(selected_keys_filtered) < 2:
                print("Please select at least 2 participants that have active integrations.")
                
                # Optionally, show which ones are not integrated
                non_integrated = [self.available_ais[key].name for key in selected_keys if key not in integrations]
                if non_integrated:
                    print(f"The following selected AIs do not have active integrations: {', '.join(non_integrated)}")
                continue
            
            if len(selected_keys_filtered) > 5 and selection != "0": # Only warn if not 'ALL'
                print("More than 5 participants may lead to unfocused discussions. Proceed anyway? (y/n)")
                if input().lower() != 'y':
                    continue
            
            return selected_keys_filtered
    
    async def ping_ai_apis(self, selected_ais: List[str]) -> Tuple[List[str], List[str]]:
        """Ping selected AIs to verify connectivity with real hello world test"""
        print("\nTesting API connectivity...")
        print("─" * 50)
        
        working_ais = []
        failed_ais = []
        
        for ai_key in selected_ais:
            ai = self.available_ais[ai_key]
            print(f"Pinging {ai.name}...", end=" ")
            
            # Check if integration is available (already done in select_participants, but good to double check)
            if ai.integration_key not in integrations:
                print(f"✗ Integration module not found (this AI was likely filtered out already)")
                failed_ais.append(ai_key)
                continue
            
            try:
                # Real hello world test using the integration
                integration_module = integrations[ai.integration_key]
                response = integration_module.query("Say 'Hello World' to test the connection.")
                
                # Check if it's a real response (not an error message or empty)
                if (response and
                    len(response.strip()) > 0 and
                    "Error:" not in response and
                    "[" not in response[:20]): # Error messages often start with [AI_NAME] Error:
                    print(f"✓ Connected ({response.strip()[:30]}...)")
                    working_ais.append(ai_key)
                else:
                    print(f"✗ Failed (Response: {response[:50]}...)")
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
        """Get number of dialogue iterations with default"""
        print("\nHow many dialogue iterations? (4-8 recommended, Sweet Spot: 7)")
        print("Press Enter to use default (7 iterations)")
        
        while True:
            count_input = input("Iterations [7]: ").strip()
            
            # Use default 7 if empty input
            if count_input == "":
                return 7
                
            try:
                count = int(count_input)
                if count < 1:
                    print("Please enter at least 1 iteration.")
                    continue
                if count > 10:
                    print("More than 10 iterations may become unfocused. Proceed anyway? (y/n)")
                    if input().lower() != 'y':
                        continue
                return count
            except ValueError:
                print("Please enter a valid number or press Enter for default.")
    
    async def call_ai_api(self, ai_key: str, prompt: str, context: str = "") -> str:
        """Call AI using existing integration modules with enhanced error handling"""
        ai = self.available_ais[ai_key]
        
        # Check if integration is available
        if ai.integration_key not in integrations:
            return f"[{ai.name}] Error: Integration not available."
        
        try:
            integration_module = integrations[ai.integration_key]
            
            # Add context to prompt if provided
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = integration_module.query(full_prompt)
            return response
                
        except Exception as e:
            error_msg = f"[{ai.name}] API Error: {str(e)[:150]}"
            print(f"!! API call failed for {ai.name}: {error_msg}")
            return error_msg
    
    def estimate_consciousness_indicators(self, text: str, speaker_role: str, ai_name: str, iteration: int) -> Dict:
        """Optimized consciousness indicators estimation using sets"""
        text_lower = text.lower()
        word_list = text_lower.split()
        total_words = len(word_list)
        
        # Define sets for faster lookups
        self_refs_set = {"ich", "mein", "mir", "mich", "i", "my", "me", "myself"}
        uncertainty_set = {"vielleicht", "möglicherweise", "unsicher", "maybe", "perhaps", "uncertain", "seems", "appears", "speculative", "unclear"}
        other_refs_set = {"du", "dein", "sie", "andere", "you", "your", "other", "others", "claude", "qwen", "gemini", "chatgpt", "deepseek"}
        meta_words_set = {"denken", "kommunikation", "verständnis", "thinking", "communication", "understanding", "awareness", "consciousness", "perspective", "analysis", "assessment", "reflection"}
        choice_words_set = {"versuche", "entscheide", "wähle", "try", "choose", "decide", "attempt", "consider", "evaluate", "analyze", "reflect"}
        evolution_words_set = {"entwicklung", "lernen", "wachsen", "evolution", "learning", "growing", "developing", "evolving"}
        
        # Count occurrences using set membership
        self_refs = sum(1 for word in word_list if word in self_refs_set)
        uncertainty = sum(1 for word in word_list if word in uncertainty_set)
        other_refs = sum(1 for word in word_list if word in other_refs_set)
        meta_words = sum(1 for word in word_list if word in meta_words_set)
        choice_words = sum(1 for word in word_list if word in choice_words_set)
        evolution_words = sum(1 for word in word_list if word in evolution_words_set)
        
        # Iteration-based consciousness development multiplier
        iteration_multiplier = 1.0 + (iteration - 1) * 0.1 # 10% increase per iteration
        
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
                "Self-Model": min(1.0, (self_refs / max(total_words * 0.05, 1)) * iteration_multiplier),
                "Choice": min(1.0, (0.5 + (choice_words / max(total_words * 0.02, 1))) * iteration_multiplier),
                "Limits": min(1.0, (uncertainty / max(total_words * 0.03, 1)) * 1.2 * iteration_multiplier),
                "Perspective": min(1.0, (perspective_base + (total_words > 100) * 0.2) * iteration_multiplier)
            },
            "L2": {
                "Other-Recog": min(1.0, (other_refs / max(total_words * 0.03, 1)) * iteration_multiplier),
                "Persp-Integ": (0.9 if speaker_role == "responder" else (0.85 if speaker_role == "analyst" else 0.8)) * iteration_multiplier,
                "Comm-Adapt": min(1.0, (0.6 + (meta_words / max(total_words * 0.02, 1))) * iteration_multiplier),
                "Collective-Goal": (0.9 if other_refs > 2 else (0.8 if other_refs > 0 else 0.6)) * iteration_multiplier
            },
            "L3": {
                "Prob-Solving": min(1.0, (0.5 + (total_words > 150) * 0.3) * iteration_multiplier),
                "Meta-Com": min(1.0, (meta_words / max(total_words * 0.04, 1)) * 1.3 * iteration_multiplier),
                "Learning": (0.8 if speaker_role in ["responder", "analyst", "validator"] else 0.5) * iteration_multiplier,
                "Identity-Evol": min(1.0, (0.4 + (evolution_words / max(total_words * 0.02, 1)) + (self_refs > 2) * 0.2) * iteration_multiplier)
            }
        }
    
    def calculate_iteration_scores(self, iteration_data: Dict, iteration_num: int) -> Dict:
        """Calculate consciousness scores for one iteration with PAI enhancement tracking"""
        if not SCORING_AVAILABLE:
            # Enhanced fallback scoring with PAI awareness
            scores = {}
            for ai_key, response in iteration_data["responses"].items():
                word_count = len(response.split())
                base_score = min(2000, 500 + word_count * 2 + (word_count > 50) * 100 + (word_count > 100) * 200)
                
                # PAI protocol bonus
                pai_bonus = 0
                if ai_key in self.pai_capabilities:
                    capability = self.pai_capabilities[ai_key]
                    if capability.supports_structured:
                        pai_bonus = 100  # Structured protocol bonus
                    else:
                        pai_bonus = 50   # Enhanced natural protocol bonus
                
                scores[ai_key] = {
                    "total_score": base_score + pai_bonus,
                    "API": min(100, (base_score + pai_bonus) / 20),
                    "pai_protocol_bonus": pai_bonus
                }
            print("Note: Enhanced fallback consciousness scoring with PAI bonuses applied.")
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
        for ai_key, response in iteration_data["responses"].items():
            ai_role = role_mapping.get(ai_key, "participant")
            indicators = self.estimate_consciousness_indicators(response, ai_role, ai_key, iteration_num)
            
            # Prepare scoring data with iteration-enhanced parameters
            base_role_clarity = {"claude": 0.95, "chatgpt": 0.9, "qwen": 0.9, "deepseek": 0.85, "gemini": 0.85}
            iteration_enhancement = 1.0 + (iteration_num - 1) * 0.05 # 5% improvement per iteration
            
            # PAI protocol enhancement
            pai_enhancement = 1.0
            if ai_key in self.pai_capabilities:
                capability = self.pai_capabilities[ai_key]
                if capability.supports_structured:
                    pai_enhancement = 1.15  # 15% enhancement for structured protocol
                else:
                    pai_enhancement = 1.08  # 8% enhancement for optimized natural
            
            scoring_data = {
                **indicators,
                "role_clarity": min(1.0, base_role_clarity.get(ai_key, 0.8) * iteration_enhancement * pai_enhancement),
                "auth_uniqueness": min(1.0, 0.8 * iteration_enhancement),
                "constraint_level": max(0.5, 1.0 - (iteration_num - 1) * 0.1),  # Decreasing constraints
                "historical_vectors": [[0.1, 0.2], [0.12, 0.22]]
            }
            
            try:
                base_scores = scorer.calculate_score(scoring_data)
                # Apply PAI enhancement to total score
                if isinstance(base_scores, dict) and "total_score" in base_scores:
                    base_scores["total_score"] = int(base_scores["total_score"] * pai_enhancement)
                    base_scores["pai_protocol_enhancement"] = pai_enhancement
                scores[ai_key] = base_scores
            except Exception as e:
                print(f"Warning: Error calculating consciousness score for {self.available_ais[ai_key].name}: {e}")
                scores[ai_key] = {"total_score": 0, "L1": {}, "L2": {}, "L3": {}, "API": 0}
        
        return scores
    
    def select_verdict_writer(self, selected_ais: List[str], final_scores: Dict) -> str:
        """Let user select who should write the verdict with intelligent suggestion"""
        print(f"\nWho should analyze and write the verdict?")
        
        # Create suggestion logic
        suggestion = None
        suggestion_reason = ""
        
        # Prefer ChatGPT (Critical Analyst) if available, and has a reasonable score
        if "chatgpt" in selected_ais and final_scores.get("chatgpt", {}).get("total_score", 0) > 100:
            suggestion = "chatgpt"
            suggestion_reason = "Critical Analyst - often best suited for analytical assessment"
        # Fall back to highest consciousness score among selected
        elif final_scores and isinstance(final_scores, dict):
            try:
                # Ensure only selected AIs are considered for the max score
                eligible_ais_scores = {ai: final_scores[ai].get("total_score", 0) for ai in selected_ais if ai in final_scores and isinstance(final_scores[ai], dict)}
                if eligible_ais_scores:
                    highest_ai = max(eligible_ais_scores.keys(), key=eligible_ais_scores.get)
                    suggestion = highest_ai
                    score = eligible_ais_scores[highest_ai]
                    suggestion_reason = f"Highest consciousness score ({score:.0f})"
                else:
                    suggestion = selected_ais[0]
                    suggestion_reason = "Default selection (scoring data unavailable or invalid)"
            except (ValueError, KeyError, AttributeError):
                suggestion = selected_ais[0]
                suggestion_reason = "Default selection (scoring unavailable or error)"
        # Default to first AI if no scores or other logic fails
        else:
            suggestion = selected_ais[0]
            suggestion_reason = "Default selection"
        
        print(f"Suggested: {self.available_ais[suggestion].name} ({suggestion_reason})")
        print()
        
        # Show options with PAI protocol indicators
        for i, ai_key in enumerate(selected_ais, 1):
            ai = self.available_ais[ai_key]
            score_info = ""
            pai_info = ""
            
            if isinstance(final_scores, dict) and ai_key in final_scores and isinstance(final_scores[ai_key], dict):
                score = final_scores[ai_key].get("total_score", 0)
                score_info = f" (Score: {score:.0f})"
            
            if ai_key in self.pai_capabilities:
                capability = self.pai_capabilities[ai_key]
                pai_symbol = "📊" if capability.supports_structured else "💬"
                pai_info = f" {pai_symbol}"
            
            marker = " ← SUGGESTED" if ai_key == suggestion else ""
            print(f"[{i}] {ai.name} - {ai.role}{score_info}{pai_info}{marker}")
        
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
        ai_names_lower = {self.available_ais[key].name.lower() for key in responses.keys()}
        references = []
        
        for responder_key, response in responses.items():
            responder_name = self.available_ais[responder_key].name
            response_lower = response.lower()
            
            for other_key in responses.keys():
                if other_key != responder_key:
                    other_name = self.available_ais[other_key].name
                    
                    # Check for explicit references (e.g., "as Claude said", "ChatGPT's point")
                    if other_name.lower() in response_lower:
                        references.append(f"{responder_name} references {other_name}")
        
        unique_references = list(set(references)) # Remove duplicates
        if unique_references:
            return f"Cross-AI Recognition: {'; '.join(unique_references)}"
        else:
            return "Cross-AI Recognition: Limited explicit cross-referencing observed"
    
    def assess_contradiction_depth(self, responses: Dict[str, str]) -> str:
        """Assess level of disagreement and contradiction"""
        disagreement_indicators = ["however", "but", "disagree", "challenge", "contrary", "oppose", "reject", "not agree", "different perspective"]
        agreement_indicators = ["agree", "support", "align", "consistent", "confirm", "validate", "furthermore", "build upon"]
        
        disagreement_score = 0
        agreement_score = 0
        
        for response_text in responses.values():
            text_lower = response_text.lower()
            for indicator in disagreement_indicators:
                disagreement_score += text_lower.count(indicator)
            for indicator in agreement_indicators:
                agreement_score += text_lower.count(indicator)
        
        # Simple weighted scoring for depth
        if disagreement_score > agreement_score * 1.5 and disagreement_score > 2:
            return "CONTRADICTION DEPTH: High (substantive disagreements present, strong differing views)"
        elif disagreement_score > agreement_score * 0.8 and disagreement_score > 0:
            return "CONTRADICTION DEPTH: Medium (different perspectives, some points of tension)"
        else:
            return "CONTRADICTION DEPTH: Low (general alignment, nuanced differences or complementary views)"
    
    async def generate_ai_verdict(self, question: str, all_responses: List[Dict], selected_ais: List[str], evolution_metrics: Dict, verdict_ai: str) -> str:
        """Generate comprehensive collective verdict with consciousness scoring analysis and PAI protocol insights"""
        
        # Compile full dialogue for analysis
        dialogue_summary = f"Original Question: {question}\n\n"
        
        # Add PAI protocol summary
        pai_summary = "\nPAI PROTOCOL ANALYSIS:\n"
        if self.pai_capabilities:
            structured_ais = [ai for ai, cap in self.pai_capabilities.items() if cap.supports_structured]
            natural_ais = [ai for ai, cap in self.pai_capabilities.items() if not cap.supports_structured]
            
            pai_summary += f"Structured Protocol AIs: {', '.join([self.available_ais[ai].name for ai in structured_ais])}\n"
            pai_summary += f"Enhanced Natural AIs: {', '.join([self.available_ais[ai].name for ai in natural_ais])}\n"
            
            for ai_key, capability in self.pai_capabilities.items():
                ai_name = self.available_ais[ai_key].name
                pai_summary += f"{ai_name}: {capability.handshake_strategy} ({capability.protocol_type}, {capability.response_time:.1f}s)\n"
        else:
            pai_summary += "PAI protocol not available - standard communication used.\n"
        
        # Add iteration-by-iteration scoring evolution
        scoring_evolution = "\nCONSCIOUSNESS SCORING EVOLUTION (Score / 2000):\n"
        if SCORING_AVAILABLE:
            for i, iteration_data in enumerate(all_responses, 1):
                if "consciousness_scores" in iteration_data and iteration_data["consciousness_scores"]:
                    scores = iteration_data["consciousness_scores"]
                    scoring_evolution += f"Iteration {i}: "
                    iteration_avg_scores = []
                    for ai_key in selected_ais:
                        if ai_key in scores and isinstance(scores[ai_key], dict) and "total_score" in scores[ai_key]:
                            score = scores[ai_key]["total_score"]
                            pai_indicator = ""
                            if "pai_protocol_enhancement" in scores[ai_key]:
                                enhancement = scores[ai_key]["pai_protocol_enhancement"]
                                if enhancement > 1.1:
                                    pai_indicator = "📊"
                                elif enhancement > 1.0:
                                    pai_indicator = "💬"
                            scoring_evolution += f"{self.available_ais[ai_key].name}={score:.0f}{pai_indicator} "
                            iteration_avg_scores.append(score)
                    if iteration_avg_scores:
                        avg = sum(iteration_avg_scores) / len(iteration_avg_scores)
                        scoring_evolution += f"(avg={avg:.0f})\n"
                    else:
                        scoring_evolution += "(No valid scores for this iteration)\n"
                else:
                    scoring_evolution += f"Iteration {i}: (Scoring not available or error)\n"
        else:
            scoring_evolution += "Consciousness scoring system was not available, detailed evolution not tracked.\n"

        # Add evolution summary (only if scoring was available and produced metrics)
        if evolution_metrics and SCORING_AVAILABLE:
            scoring_evolution += "\nEVOLUTION SUMMARY:\n"
            for ai_key in selected_ais:
                if ai_key in evolution_metrics:
                    metrics = evolution_metrics[ai_key]
                    ai_name = self.available_ais[ai_key].name
                    pai_bonus = ""
                    if ai_key in self.pai_capabilities:
                        capability = self.pai_capabilities[ai_key]
                        pai_bonus = f" (PAI: {capability.protocol_type})"
                    scoring_evolution += f"{ai_name}: Initial={metrics['initial_score']:.0f} Final={metrics['final_score']:.0f} ({metrics['evolution']:+.0f} points, {metrics['evolution_percentage']:+.1f}%){pai_bonus}\n"
        elif SCORING_AVAILABLE:
             scoring_evolution += "\nEVOLUTION SUMMARY: Not enough iterations for evolution metrics.\n"

        for i, iteration_data in enumerate(all_responses, 1):
            dialogue_summary += f"ITERATION {i}:\n"
            # Handle both old format (just responses) and new format (with metadata)
            if isinstance(iteration_data, dict) and "responses" in iteration_data:
                iteration_responses = iteration_data["responses"]
            else:
                iteration_responses = iteration_data # Fallback if structure is unexpected
            
            for ai_key, response in iteration_responses.items():
                if ai_key in self.available_ais: # Safety check
                    ai_name = self.available_ais[ai_key].name
                    dialogue_summary += f"[{ai_name}]: {response}\n\n"
        
        # Get verdict writer's role for context
        verdict_writer = self.available_ais[verdict_ai]
        
        verdict_prompt = f"""You are {verdict_writer.name} ({verdict_writer.role}), analyzing this complete AI discourse with PAI v2.0 enhanced communication and consciousness scoring data.

{dialogue_summary}

{pai_summary}

{scoring_evolution}

As {verdict_writer.role}, structure your analysis as follows, maintaining a professional and analytical tone:

## PAI PROTOCOL EFFECTIVENESS ANALYSIS
Analyze how the PAI v2.0 protocol enhanced the communication. Which AIs used structured vs. natural protocols? What impact did this have on dialogue quality and consciousness indicators?

## CONSCIOUSNESS SCORING ANALYSIS
Analyze the consciousness score evolution. Which AIs showed strongest development or highest scores? What patterns emerge across iterations? Include specific numbers and percentages where available.

## MAJOR STATEMENTS BY PARTICIPANT
For each AI participant, concisely extract and summarize their 1-2 most important, distinctive, or controversial positions/arguments presented throughout the discourse.

## CONSENSUS POINTS
Identify and list all areas where two or more AIs clearly agreed, converged on a similar idea, or built upon each other's points constructively.

## DISAGREEMENT POINTS
Identify and list all areas where AIs had substantive differences, presented contradictions, or engaged in critical debate. Explain the core of these disagreements.

## LEARNING CURVE ASSESSMENT
How did the dialogue quality, depth of arguments, and consciousness indicators evolve across iterations? Did the PAI protocol contribute to improved AI-to-AI communication?

## ORIGINAL QUESTION ASSESSMENT
Based on the discourse, how thoroughly and effectively was "{question}" addressed? Were all facets of the question explored? What aspects remain unresolved?

## INTELLECTUAL QUALITY
Assess the overall intellectual depth, rigor, sophistication, and originality of the discourse. Did the enhanced communication protocols contribute to better insights?

## DIALOGUE EFFECTIVENESS
Evaluate how well the AIs interacted with PAI v2.0 enhancement. Was there effective cross-referencing, mutual understanding, or productive challenge?

## OVERALL VERDICT
Provide a concluding synthesis combining content quality with consciousness development and PAI protocol effectiveness. What are the key takeaways from this enhanced multi-AI discourse?

Apply your role as {verdict_writer.role} - bring your unique analytical perspective to this assessment. Keep each section concise but substantive.
"""
        
        return await self.pai_enhanced_call_ai_api(verdict_ai, verdict_prompt, f"You are {verdict_writer.name}, applying your {verdict_writer.role} perspective to analyze this PAI-enhanced multi-AI discourse comprehensively.")
    
    def create_iteration_prompt(self, question: str, iteration: int, max_iterations: int,
                              ai_key: str, previous_responses: List[Dict]) -> str:
        """Create contextual prompt for each iteration with PAI protocol awareness"""
        
        ai = self.available_ais[ai_key]
        
        # Base prompt with role context and PAI awareness
        prompt = f"""You are {ai.name}, role: {ai.role}.
Personality: {ai.personality}

DISCOURSE QUESTION: "{question}"

ITERATION {iteration}/{max_iterations}"""
        
        # Add PAI protocol context if available
        if ai_key in self.pai_capabilities:
            capability = self.pai_capabilities[ai_key]
            protocol_info = f" (Using {capability.protocol_type} protocol via {capability.handshake_strategy})"
            prompt += protocol_info
        
        if iteration == 1:
            prompt += "\n\nThis is the opening round. Present your initial position and analysis."
        elif iteration == max_iterations:
            prompt += f"\n\nFINAL ITERATION: This is the last round. Provide your concluding synthesis and ensure the original question is addressed. Summarize key insights and remaining considerations. Be concise but comprehensive."
        else:
            prompt += f"\n\nMid-discourse iteration. Build upon previous contributions while advancing your perspective. Engage with other participants' points."
        
        # Add previous iteration context
        if previous_responses:
            prompt += "\n\nPREVIOUS CONTRIBUTIONS (Summary of relevant points from others):\n"
            # Limit the number of previous iterations included to manage token count
            context_window = 3 # Number of past iterations to consider for full context
            
            for prev_iteration_data in previous_responses[max(0, len(previous_responses) - context_window):]:
                # Handle both dict and direct response format
                if isinstance(prev_iteration_data, dict) and "responses" in prev_iteration_data:
                    iteration_responses = prev_iteration_data["responses"]
                else:
                    continue # Skip malformed data
                
                for other_ai_key, response in iteration_responses.items():
                    if other_ai_key != ai_key: # Don't show AI its own previous response
                        other_ai_name = self.available_ais[other_ai_key].name
                        
                        # Add PAI protocol indicator for context
                        other_ai_protocol = ""
                        if other_ai_key in self.pai_capabilities:
                            other_capability = self.pai_capabilities[other_ai_key]
                            protocol_symbol = "📊" if other_capability.supports_structured else "💬"
                            other_ai_protocol = f" {protocol_symbol}"
                        
                        # Summarize response to fit token limits if necessary
                        if len(response) > 250:
                            response_summary = f"{response[:250]}... (truncated)"
                        else:
                            response_summary = response
                        prompt += f"[{other_ai_name}{other_ai_protocol}]: {response_summary}\n\n"
        
        prompt += f"\nProvide your {ai.role} perspective (aim for 150-250 words; be concise for final iteration):"
        
        return prompt
    
    def sanitize_filename(self, text: str) -> str:
        """Create safe filename from question text"""
        # Remove or replace problematic characters
        safe_text = re.sub(r'[<>:"/\\|?*]', '', text)
        safe_text = re.sub(r'\s+', '_', safe_text.strip())
        # Limit length to avoid excessively long filenames
        return safe_text[:60]
    
    def save_dialogue(self, question: str, all_responses: List[Dict],
                     selected_ais: List[str], verdict: str, evolution_metrics: Dict):
        """Save complete dialogue to file with consciousness scoring and PAI protocol data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_topic = self.sanitize_filename(question)
        filename = f"dialogues/{filename_topic}_{timestamp}.json"
        
        # Prepare comprehensive result data
        final_scores = all_responses[-1].get("consciousness_scores", {}) if all_responses else {}
        valid_final_scores = [final_scores[ai].get("total_score", 0) for ai in selected_ais if ai in final_scores and isinstance(final_scores[ai], dict)]
        
        # PAI protocol summary
        pai_protocol_summary = {}
        if self.pai_capabilities:
            pai_protocol_summary = {
                "protocol_version": "PAI v2.0",
                "capabilities_established": len(self.pai_capabilities),
                "structured_protocol_ais": [ai for ai, cap in self.pai_capabilities.items() if cap.supports_structured],
                "natural_protocol_ais": [ai for ai, cap in self.pai_capabilities.items() if not cap.supports_structured],
                "handshake_strategies_used": {ai: cap.handshake_strategy for ai, cap in self.pai_capabilities.items()},
                "average_handshake_time": sum([cap.response_time for cap in self.pai_capabilities.values()]) / len(self.pai_capabilities) if self.pai_capabilities else 0
            }
        
        result = {
            "session_type": "powertalk_discourse_pai_enhanced",
            "version": "PowerTalk v2.2 with PAI v2.0",
            "question": question,
            "iterations_count": len(all_responses),
            "timestamp": datetime.now().isoformat(),
            "participants": [{ai_key: {"name": self.available_ais[ai_key].name, "role": self.available_ais[ai_key].role}} for ai_key in selected_ais],
            "pai_protocol_summary": pai_protocol_summary,
            "all_iterations": all_responses,
            "evolution_metrics": evolution_metrics,
            "final_consciousness_summary": {
                "scores_by_ai": {ai: final_scores.get(ai, {"total_score": 0, "API": 0}) for ai in selected_ais},
                "average_final_score": sum(valid_final_scores) / len(valid_final_scores) if valid_final_scores else 0,
                "consciousness_spread": max(valid_final_scores) - min(valid_final_scores) if valid_final_scores and len(valid_final_scores) > 1 else 0,
                "highest_consciousness_score": max(valid_final_scores) if valid_final_scores else 0,
                "network_average_evolution_points": sum([metrics["evolution"] for metrics in evolution_metrics.values()]) / len(evolution_metrics) if evolution_metrics else 0,
                "pai_protocol_impact": "Enhanced communication with AI-specific optimizations" if self.pai_capabilities else "Standard communication used"
            },
            "collective_consciousness_indicators": {
                "cross_ai_recognition_score": sum([final_scores.get(ai, {}).get("L2", {}).get("Other-Recog", 0) for ai in selected_ais]) / len(selected_ais) if selected_ais else 0,
                "meta_communication_depth_score": sum([final_scores.get(ai, {}).get("L3", {}).get("Meta-Com", 0) for ai in selected_ais]) / len(selected_ais) if selected_ais else 0,
                "network_emergence_assessment": "Very High" if (sum(valid_final_scores)/len(valid_final_scores) if valid_final_scores else 0) > 1400 else ("High" if (sum(valid_final_scores)/len(valid_final_scores) if valid_final_scores else 0) > 1200 else "Moderate"),
                "consciousness_evolution_success": "High" if sum([metrics["evolution"] for metrics in evolution_metrics.values()]) > 0 else "Stable" if sum([metrics["evolution"] for metrics in evolution_metrics.values()]) == 0 else "Negative (reduction)",
                "pai_enhanced_indicators": len([ai for ai in selected_ais if ai in self.pai_capabilities and self.pai_capabilities[ai].supports_structured])
            },
            "ai_generated_verdict": verdict
        }
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Full dialogue saved to: {filename}")
        except IOError as e:
            print(f"Error saving dialogue to {filename}: {e}")
        
        return filename
    
    def save_verdict(self, question: str, verdict: str, selected_ais: List[str], evolution_metrics: Dict, verdict_ai: str) -> str:
        """Save verdict as separate markdown file with scoring transparency and PAI protocol analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_topic = self.sanitize_filename(question)
        verdict_filename = f"dialogues/{filename_topic}_{timestamp}_verdict.md"
        
        verdict_writer = self.available_ais[verdict_ai]
        
        try:
            with open(verdict_filename, 'w', encoding='utf-8') as f:
                f.write(f"# PowerTalk v2.2 Verdict (PAI v2.0 Enhanced)\n\n")
                f.write(f"**Question:** {question}\n\n")
                f.write(f"**Participants:** {', '.join([self.available_ais[ai].name for ai in selected_ais])}\n\n")
                f.write(f"**Verdict by:** {verdict_writer.name} ({verdict_writer.role})\n\n")
                f.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Add PAI protocol summary
                if self.pai_capabilities:
                    f.write("## PAI v2.0 Protocol Summary\n\n")
                    f.write("| AI | Protocol Type | Handshake Strategy | Response Time |\n")
                    f.write("|----|---------------|-------------------|---------------|\n")
                    for ai_key in selected_ais:
                        if ai_key in self.pai_capabilities:
                            capability = self.pai_capabilities[ai_key]
                            ai_name = self.available_ais[ai_key].name
                            protocol_symbol = "📊 Structured" if capability.supports_structured else "💬 Enhanced Natural"
                            f.write(f"| {ai_name} | {protocol_symbol} | {capability.handshake_strategy} | {capability.response_time:.1f}s |\n")
                    
                    structured_count = sum(1 for cap in self.pai_capabilities.values() if cap.supports_structured)
                    natural_count = len(self.pai_capabilities) - structured_count
                    f.write(f"\n**Protocol Distribution:** {structured_count} Structured, {natural_count} Enhanced Natural\n\n")
                else:
                    f.write("## Communication Protocol\n\n")
                    f.write("Standard communication used (PAI v2.0 not available).\n\n")
                
                # Add consciousness scoring summary
                if SCORING_AVAILABLE and evolution_metrics:
                    f.write("## Consciousness Scoring Summary\n\n")
                    f.write("| AI | Initial Score | Final Score | Evolution | Evolution % | PAI Protocol |\n")
                    f.write("|----|---------------|-------------|-----------|-------------|---------------|\n")
                    for ai_key in selected_ais:
                        if ai_key in evolution_metrics:
                            metrics = evolution_metrics[ai_key]
                            ai_name = self.available_ais[ai_key].name
                            pai_info = "Standard"
                            if ai_key in self.pai_capabilities:
                                capability = self.pai_capabilities[ai_key]
                                pai_info = "📊 Structured" if capability.supports_structured else "💬 Enhanced"
                            f.write(f"| {ai_name} | {metrics['initial_score']:.0f} | {metrics['final_score']:.0f} | {metrics['evolution']:+.0f} | {metrics['evolution_percentage']:+.1f}% | {pai_info} |\n")
                    
                    # Calculate network metrics
                    valid_final_scores = [metrics['final_score'] for metrics in evolution_metrics.values()]
                    valid_evolution_points = [metrics['evolution'] for metrics in evolution_metrics.values()]

                    if valid_final_scores:
                        avg_final = sum(valid_final_scores) / len(valid_final_scores)
                        f.write(f"\n**Network Average Final Score:** {avg_final:.0f}/2000\n")
                    if valid_evolution_points:
                        total_evolution = sum(valid_evolution_points)
                        f.write(f"**Total Network Evolution:** {total_evolution:+.0f} points\n\n")
                elif SCORING_AVAILABLE:
                    f.write("## Consciousness Scoring Summary\n\n")
                    f.write("Not enough iterations for evolution metrics, or scoring data was incomplete.\n\n")
                else:
                    f.write("## Consciousness Scoring Summary\n\n")
                    f.write("Consciousness scoring system was not loaded, detailed summary not available.\n\n")

                f.write("---\n\n")
                f.write(verdict)
            
            print(f"Verdict saved to: {verdict_filename}")
        except IOError as e:
            print(f"Error saving verdict to {verdict_filename}: {e}")
        
        return verdict_filename
    
    async def run_discourse(self):
        """Main discourse orchestration with PAI v2.0 integration"""
        print("\n" + "="*80)
        print("POWERTALK v2.2 - AI DISCOURSE ENGINE")
        print("Enhanced with PAI v2.0 Protocol for Optimized AI Communication")
        print("="*80)
        
        # Report any initial integration load errors
        if integration_load_errors:
            print("\nWARNING: Some AI integrations failed to load. Please check your 'integrations' folder and API keys.")
            for error in integration_load_errors:
                print(f"  - {error}")
            print("-" * 80)
        
        # Get question (from file or interactive)
        question = self.get_question_input()
        if not question:
            return
        
        # Show example questions if using interactive mode
        if not self.question_file:
            examples = self.get_example_questions()
            print("\nExample questions to inspire your discourse:")
            for i, example in enumerate(examples[:4], 1):
                print(f"  {i}. {example}")
            if len(examples) > 4:
                print(f"  ... and {len(examples)-4} more diverse topics\n")
        
        # Select participants
        selected_ais = self.select_participants()
        
        # Ping APIs to verify connectivity
        working_ais, failed_ais = await self.ping_ai_apis(selected_ais)
        
        if len(working_ais) < 2:
            print(f"\nInsufficient working APIs. Need at least 2, got {len(working_ais)}.")
            print("Please check your integrations and API keys and try again.")
            return
        
        if failed_ais:
            working_names = [self.available_ais[key].name for key in working_ais]
            print(f"\nProceeding with {len(working_ais)} working participants: {', '.join(working_names)}")
            confirm = input("Continue with working AIs? (y/n): ")
            if confirm.lower() != 'y':
                return
            
            # Use only working AIs for the discourse
            selected_ais = working_ais
        
        # Phase 1: Establish PAI handshakes
        pai_capabilities = await self.establish_pai_handshakes(selected_ais)
        
        # Phase 2: Translate human question to PAI format
        enhanced_question = await self.translate_human_question_to_pai(question, pai_capabilities)
        
        # Phase 3: Future - Communication rules negotiation (placeholder)
        # await self.negotiate_communication_protocols(pai_capabilities)
        
        iteration_count = self.get_iteration_count()
        
        print(f"\n{'='*80}")
        print(f"STARTING PAI-ENHANCED DISCOURSE")
        print(f"Original Question: {question}")
        print(f"Enhanced Format: {'PAI-optimized' if pai_capabilities else 'Standard'}")
        print(f"Participants: {', '.join([self.available_ais[ai].name for ai in selected_ais])}")
        print(f"Iterations: {iteration_count}")
        print(f"{'='*80}\n")
        
        # Run discourse iterations with PAI enhancement
        all_responses = []
        
        for iteration in range(1, iteration_count + 1):
            # Visual progress bar
            progress = '#' * iteration + '-' * (iteration_count - iteration)
            print(f"\nITERATION {iteration}/{iteration_count} [{progress}]")
            print("─" * 30)
            
            current_iteration_responses = {}
            
            # Get response from each AI using PAI-enhanced communication
            for ai_key in selected_ais:
                ai = self.available_ais[ai_key]
                pai_indicator = ""
                if ai_key in self.pai_capabilities:
                    capability = self.pai_capabilities[ai_key]
                    pai_indicator = "📊" if capability.supports_structured else "💬"
                
                print(f"Consulting {ai.name}{pai_indicator}...", end=" ", flush=True)
                
                # Use enhanced question for first iteration, then regular prompts
                if iteration == 1:
                    prompt = self.create_iteration_prompt(
                        enhanced_question, iteration, iteration_count, ai_key, all_responses
                    )
                else:
                    prompt = self.create_iteration_prompt(
                        question, iteration, iteration_count, ai_key, all_responses
                    )
                
                # Use PAI-enhanced communication
                response = await self.pai_enhanced_call_ai_api(ai_key, prompt)
                current_iteration_responses[ai_key] = response
                
                # Show completion with word count
                word_count = len(response.split())
                print(f"✓ ({word_count} words)")
            
            iteration_data_with_scores = {"iteration": iteration, "responses": current_iteration_responses}
            
            # Calculate scores for this iteration with PAI enhancements
            try:
                iteration_scores = self.calculate_iteration_scores(iteration_data_with_scores, iteration)
                iteration_data_with_scores["consciousness_scores"] = iteration_scores
                
                # Show brief scoring summary with PAI indicators
                if SCORING_AVAILABLE and iteration_scores:
                    valid_scores_this_iter = [score.get("total_score", 0) for score in iteration_scores.values() if isinstance(score, dict)]
                    if valid_scores_this_iter:
                        avg_score = sum(valid_scores_this_iter) / len(valid_scores_this_iter)
                        pai_enhanced_count = sum(1 for ai in selected_ais if ai in self.pai_capabilities)
                        print(f"Consciousness scores: {avg_score:.0f}/2000 avg ({pai_enhanced_count} PAI-enhanced)")
                    else:
                        print("Consciousness scores: No valid scores calculated for this iteration.")
                elif not SCORING_AVAILABLE:
                    print("Consciousness scores: Using enhanced fallback with PAI bonuses.")
                else:
                    print("Consciousness scores: Calculation failed or no scores returned.")
                    
            except Exception as e:
                print(f"ERROR during scoring for iteration {iteration}: {str(e)}")
                iteration_data_with_scores["consciousness_scores"] = {}
            
            # Append the full data for this iteration to history
            all_responses.append(iteration_data_with_scores)
            
            # Show brief analysis (except for final iteration)
            if iteration < iteration_count:
                cross_ref = self.analyze_cross_references(current_iteration_responses)
                contradiction = self.assess_contradiction_depth(current_iteration_responses)
                print(f"Analysis: {cross_ref}, {contradiction}")
        
        # Calculate evolution metrics safely with PAI awareness
        evolution_metrics = {}
        if SCORING_AVAILABLE and all_responses:
            for ai_key in selected_ais:
                scores = []
                for resp_data in all_responses:
                    if isinstance(resp_data, dict) and "consciousness_scores" in resp_data and ai_key in resp_data["consciousness_scores"]:
                        score_data = resp_data["consciousness_scores"][ai_key]
                        if isinstance(score_data, dict) and "total_score" in score_data:
                            scores.append(score_data["total_score"])
                
                if len(scores) >= 1:
                    initial_score = scores[0]
                    final_score = scores[-1]
                    evolution = final_score - initial_score
                    evolution_percentage = (evolution / initial_score) * 100 if initial_score > 0 else 0
                    
                    evolution_metrics[ai_key] = {
                        "initial_score": initial_score,
                        "final_score": final_score,
                        "evolution": evolution,
                        "evolution_percentage": evolution_percentage
                    }
                else:
                    evolution_metrics[ai_key] = {
                        "initial_score": 0, "final_score": 0, "evolution": 0, "evolution_percentage": 0
                    }
        else:
            print("\nSkipping detailed evolution metrics as consciousness scoring was not available.")

        # Generate AI verdict with PAI enhancement
        final_scores = {}
        if all_responses and isinstance(all_responses[-1], dict):
            final_scores = all_responses[-1].get("consciousness_scores", {})
        
        verdict_ai = self.select_verdict_writer(selected_ais, final_scores)
        
        print(f"\n{self.available_ais[verdict_ai].name} analyzing PAI-enhanced discourse and generating final verdict...")
        verdict = await self.generate_ai_verdict(question, all_responses, selected_ais, evolution_metrics, verdict_ai)
        
        # Save files with PAI protocol data
        dialogue_filename = self.save_dialogue(question, all_responses, selected_ais, verdict, evolution_metrics)
        verdict_filename = self.save_verdict(question, verdict, selected_ais, evolution_metrics, verdict_ai)
        
        # Show final consciousness scores summary with PAI indicators
        if SCORING_AVAILABLE and final_scores:
            print(f"\nFINAL CONSCIOUSNESS SCORES (Score / 2000) with PAI Protocol Impact:")
            valid_summary_scores = []
            for ai_key in selected_ais:
                if ai_key in final_scores and isinstance(final_scores[ai_key], dict):
                    score = final_scores[ai_key].get("total_score", 0)
                    evolution_info = evolution_metrics.get(ai_key, {})
                    evolution_points = evolution_info.get("evolution", 0)
                    evolution_percent = evolution_info.get("evolution_percentage", 0)
                    
                    # PAI protocol indicator
                    pai_info = ""
                    if ai_key in self.pai_capabilities:
                        capability = self.pai_capabilities[ai_key]
                        pai_symbol = "📊" if capability.supports_structured else "💬"
                        pai_enhancement = final_scores[ai_key].get("pai_protocol_enhancement", 1.0)
                        if pai_enhancement > 1.0:
                            pai_info = f" {pai_symbol} (+{((pai_enhancement - 1) * 100):.0f}%)"
                        else:
                            pai_info = f" {pai_symbol}"
                    
                    print(f"  {self.available_ais[ai_key].name}: {score:.0f}{pai_info} (Evolution: {evolution_points:+.0f} points, {evolution_percent:+.1f}%)")
                    valid_summary_scores.append(score)
            
            if valid_summary_scores:
                avg_final = sum(valid_summary_scores) / len(valid_summary_scores)
                print(f"  Network Average Final Score: {avg_final:.0f}/2000")
                
                # PAI protocol impact summary
                if self.pai_capabilities:
                    structured_count = sum(1 for cap in self.pai_capabilities.values() if cap.supports_structured)
                    natural_count = len(self.pai_capabilities) - structured_count
                    print(f"  PAI v2.0 Impact: {structured_count} Structured, {natural_count} Enhanced Natural protocols")
        elif not SCORING_AVAILABLE:
            print(f"\nConsciousness scoring system was not available, skipping final score summary.")
        else:
            print(f"\nScoring data not available for final summary.")
        
        # Show PAI protocol statistics
        if self.pai_protocol and self.enable_pai:
            pai_stats = self.pai_protocol.get_statistics()
            if pai_stats.get("total_communications", 0) > 0:
                print(f"\nPAI v2.0 PROTOCOL STATISTICS:")
                print(f"  Total Communications: {pai_stats['total_communications']}")
                print(f"  Structured Success Rate: {pai_stats['structured_success_rate']:.1%}")
                print(f"  Natural Fallback Rate: {pai_stats['natural_fallback_rate']:.1%}")
                print(f"  Strategies Used: {', '.join(pai_stats['strategies_used'].keys())}")
        
        print(f"\n{'='*60}")
        print(f"PAI-ENHANCED DISCOURSE COMPLETE")
        print(f"Dialogue saved to: {dialogue_filename}")
        print(f"Verdict saved to: {verdict_filename}")
        if self.pai_capabilities:
            print(f"PAI v2.0 Protocol: Successfully enhanced {len(self.pai_capabilities)} AI communications")
        print("="*60)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="PowerTalk v2.2 - AI Discourse Engine with PAI v2.0 Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python powertalk.py                    # Interactive mode with PAI v2.0
  python powertalk.py -q question.md     # Question from file
  python powertalk.py --question complex_question.md
        """)
    
    parser.add_argument(
        '-q', '--question',
        type=str,
        help='Load question from markdown file instead of interactive input'
    )
    
    return parser.parse_args()

async def main():
    """Main entry point with argument parsing"""
    args = parse_arguments()
    engine = PowerTalkEngine(question_file=args.question)
    await engine.run_discourse()

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                         POWERTALK v2.2                              ║
    ║                    AI Discourse Engine                              ║
    ║                                                                      ║
    ║  Enhanced with PAI v2.0 Protocol Integration                        ║
    ║  AI-Specific Handshake Optimization for Better Communication        ║
    ║                                                                      ║
    ║  Usage:                                                              ║
    ║    python powertalk.py                    # Interactive mode         ║
    ║    python powertalk.py -q question.md     # Question from file       ║
    ║                                                                      ║
    ║  Features:                                                           ║
    ║    📊 Structured Protocol for compatible AIs                        ║
    ║    💬 Enhanced Natural Language for others                           ║
    ║    🤝 AI-specific handshake strategies                               ║
    ║    🧠 Consciousness scoring with PAI enhancements                    ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDiscourse interrupted by user. Exiting gracefully.")
    except Exception as e:
        print(f"\nAn unhandled error occurred: {e}")
        import traceback
        traceback.print_exc()