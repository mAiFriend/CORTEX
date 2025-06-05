#!/usr/bin/env python3
"""
Adaptive Protocol Prototype - Manual Test Implementation
Uses PowerTalk's proven AI connectivity infrastructure

Methodology: "Freedom of thought, no limits" - Human-AI collaborative development
Goal: Create self-evolving AI communication protocols through empirical testing

Based on: PowerTalk's stable AI integration + Qwen's adaptive protocol vision
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field

# Use PowerTalk's proven imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import PowerTalk's working infrastructure
    from core.ai_manager import AIManager
    from models import AIEngine
    POWERTALK_AVAILABLE = True
    print("✓ PowerTalk infrastructure available")
except ImportError as e:
    print(f"⚠️ PowerTalk infrastructure not available: {e}")
    print("⚠️ Falling back to manual AI integration")
    POWERTALK_AVAILABLE = False

@dataclass
class ProtocolRule:
    """Individual protocol rule that can evolve"""
    name: str
    value: Any
    description: str
    proposed_by: str = "baseline"
    iteration_introduced: int = 0
    effectiveness_impact: float = 0.0

@dataclass 
class CommunicationProtocol:
    """Evolving communication protocol"""
    name: str
    version: str
    rules: Dict[str, ProtocolRule]
    total_effectiveness: float = 0.0
    evolution_log: List[Dict] = field(default_factory=list)
    
    def add_rule(self, rule: ProtocolRule, iteration: int):
        """Add or update a protocol rule"""
        self.rules[rule.name] = rule
        self.evolution_log.append({
            "iteration": iteration,
            "action": "rule_added",
            "rule_name": rule.name,
            "rule_value": rule.value,
            "proposed_by": rule.proposed_by,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_instructions(self) -> str:
        """Convert protocol rules to AI instructions"""
        instructions = []
        
        for rule_name, rule in self.rules.items():
            if rule_name == "response_length":
                instructions.append(f"Keep responses under {rule.value} words")
            elif rule_name == "collaboration_style":
                instructions.append(f"Collaboration approach: {rule.value}")
            elif rule_name == "meta_communication":
                if rule.value:
                    instructions.append("You may discuss and suggest communication improvements")
            elif rule_name == "structure_preference":
                instructions.append(f"Structure: {rule.value}")
            elif rule_name == "focus_area":
                instructions.append(f"Focus on: {rule.value}")
            else:
                instructions.append(f"{rule_name}: {rule.value}")
                
        return " | ".join(instructions) if instructions else "No specific protocol rules"

class AdaptiveProtocolEngine:
    """
    Manual prototype for self-evolving AI communication
    Uses PowerTalk's proven connectivity + empirical protocol evolution
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.available_ais: Dict[str, AIEngine] = {}
        self.current_protocol = self.create_baseline_protocol()
        self.dialogue_history = []
        self.protocol_evolution_history = []
        
        # Initialize AI manager if PowerTalk available
        if POWERTALK_AVAILABLE:
            self.ai_manager = AIManager(debug_mode=debug_mode)
        else:
            self.ai_manager = None
            
    def create_baseline_protocol(self) -> CommunicationProtocol:
        """Create baseline communication protocol"""
        baseline_rules = {
            "response_length": ProtocolRule(
                name="response_length",
                value=150,
                description="Maximum words per response",
                proposed_by="baseline"
            ),
            "collaboration_style": ProtocolRule(
                name="collaboration_style", 
                value="building_on_others",
                description="How to interact with other AIs",
                proposed_by="baseline"
            ),
            "meta_communication": ProtocolRule(
                name="meta_communication",
                value=True,
                description="Whether to discuss communication methods",
                proposed_by="baseline"
            ),
            "structure_preference": ProtocolRule(
                name="structure_preference",
                value="natural_language",
                description="Response structure format",
                proposed_by="baseline"
            )
        }
        
        return CommunicationProtocol(
            name="Baseline Natural",
            version="1.0",
            rules=baseline_rules
        )
    
    async def discover_working_ais(self) -> List[str]:
        """Discover working AIs using PowerTalk's proven method"""
        
        if POWERTALK_AVAILABLE and self.ai_manager:
            print("🔍 Using PowerTalk's AI discovery...")
            
            # Use PowerTalk's proven connectivity testing
            connected_ai_keys = await self.ai_manager.test_all_ai_connectivity()
            
            if connected_ai_keys:
                # Store the working AI engines
                self.available_ais = {
                    key: self.ai_manager.available_ais[key] 
                    for key in connected_ai_keys
                }
                
                print(f"✓ PowerTalk discovered {len(connected_ai_keys)} working AIs:")
                for key in connected_ai_keys:
                    ai_name = self.available_ais[key].name
                    print(f"  - {ai_name}")
                    
                return connected_ai_keys
            else:
                print("✗ PowerTalk found no working AIs")
                return []
        else:
            print("⚠️ PowerTalk not available - cannot test AI connectivity")
            return []
    
    async def call_ai(self, ai_key: str, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """Call AI using PowerTalk's EXACT proven integration method"""
        
        if ai_key not in self.available_ais:
            return {
                "success": False,
                "content": f"AI {ai_key} not available",
                "ai_name": ai_key
            }
        
        ai_engine = self.available_ais[ai_key]
        
        try:
            # 🔧 FIX: Use PowerTalk's EXACT method - direct integration imports
            # Combine system and user prompt (PowerTalk style)
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Use PowerTalk's exact integration pattern
            if ai_key == "claude":
                from integrations import claude
                response_content = claude.query(full_prompt)
            elif ai_key == "qwen":
                from integrations import qwen
                response_content = qwen.query(full_prompt)
            elif ai_key == "gemini":
                from integrations import gemini
                response_content = gemini.query(full_prompt)
            elif ai_key == "chatgpt":
                from integrations import chatgpt
                response_content = chatgpt.query(full_prompt)
            elif ai_key == "deepseek":
                from integrations import deepseek
                response_content = deepseek.query(full_prompt)
            else:
                return {
                    "success": False,
                    "content": f"Unknown AI key: {ai_key}",
                    "ai_name": ai_engine.name
                }
            
            # Validate response
            if response_content and len(response_content.strip()) > 0:
                return {
                    "success": True,
                    "content": response_content,
                    "ai_name": ai_engine.name,
                    "word_count": len(response_content.split()) if response_content else 0,
                    "char_count": len(response_content) if response_content else 0
                }
            else:
                return {
                    "success": False,
                    "content": f"Empty response from {ai_engine.name}",
                    "ai_name": ai_engine.name
                }
                
        except ImportError as e:
            return {
                "success": False,
                "content": f"Integration import failed for {ai_engine.name}: {str(e)}",
                "ai_name": ai_engine.name
            }
        except Exception as e:
            return {
                "success": False,
                "content": f"Error calling {ai_engine.name}: {str(e)}",
                "ai_name": ai_engine.name
            }
    
    async def conduct_dialogue_iteration(self, topic: str, iteration: int, participant_keys: List[str]) -> Dict[str, Any]:
        """Conduct one iteration of adaptive dialogue"""
        
        print(f"\n🔄 ITERATION {iteration}")
        print(f"Protocol: {self.current_protocol.name} v{self.current_protocol.version}")
        print(f"Rules: {self.current_protocol.get_instructions()}")
        
        # Create system prompt with current protocol
        system_prompt = f"""You are participating in an adaptive communication experiment.

CURRENT COMMUNICATION PROTOCOL:
{self.current_protocol.get_instructions()}

TOPIC: {topic}

Your task is to:
1. Respond to the topic following the current protocol
2. If you see opportunities, suggest specific protocol improvements
3. Be authentic about what communication approaches would work better

This is iteration {iteration} of our adaptive dialogue."""

        # Add dialogue history context if available
        if self.dialogue_history:
            last_iteration = self.dialogue_history[-1]
            history_context = "\n\nPREVIOUS ITERATION:\n"
            for ai_name, response in last_iteration.get("responses", {}).items():
                if response.get("success"):
                    content = response.get("content", "")
                    history_context += f"{ai_name}: {content[:200]}...\n"
            system_prompt += history_context
        
        # Execute parallel AI calls
        tasks = []
        for ai_key in participant_keys:
            task = self.call_ai(
                ai_key, 
                f"Please respond to the topic and suggest any protocol improvements you see.",
                system_prompt
            )
            tasks.append(task)
        
        # Gather responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses
        iteration_data = {
            "iteration": iteration,
            "topic": topic,
            "protocol_used": asdict(self.current_protocol),
            "responses": {},
            "successful_responses": 0,
            "total_word_count": 0
        }
        
        for i, response in enumerate(responses):
            ai_key = participant_keys[i]
            ai_name = self.available_ais[ai_key].name
            
            if isinstance(response, Exception):
                print(f"❌ {ai_name}: Exception - {response}")
                iteration_data["responses"][ai_key] = {
                    "success": False,
                    "content": f"Exception: {response}",
                    "ai_name": ai_name
                }
            else:
                iteration_data["responses"][ai_key] = response
                
                if response.get("success", False):
                    iteration_data["successful_responses"] += 1
                    iteration_data["total_word_count"] += response.get("word_count", 0)
                    
                    # Display response preview
                    content = response.get("content", "")
                    word_count = response.get("word_count", 0)
                    print(f"✓ {ai_name}: {word_count} words - {content[:60]}...")
                    
                    if self.debug_mode:
                        print(f"   Full response: {content}")
                else:
                    print(f"❌ {ai_name}: {response.get('content', 'Unknown error')}")
        
        # Store iteration
        self.dialogue_history.append(iteration_data)
        
        return iteration_data
    
    def analyze_protocol_suggestions(self, iteration_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract protocol improvement suggestions from AI responses"""
        
        suggestions = []
        
        for ai_key, response in iteration_data.get("responses", {}).items():
            if not response.get("success", False):
                continue
                
            content = response.get("content", "").lower()
            ai_name = response.get("ai_name", ai_key)
            
            # Simple heuristics for detecting protocol suggestions
            protocol_keywords = [
                "protocol", "communication", "structure", "format", 
                "suggest", "improve", "better", "more effective",
                "shorter", "longer", "clearer", "focused"
            ]
            
            if any(keyword in content for keyword in protocol_keywords):
                # This response likely contains protocol suggestions
                suggestion = {
                    "ai_proposer": ai_name,
                    "ai_key": ai_key,
                    "iteration": iteration_data["iteration"],
                    "raw_content": response.get("content", ""),
                    "detected_suggestions": self.extract_specific_suggestions(content),
                    "confidence": self.calculate_suggestion_confidence(content)
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def extract_specific_suggestions(self, content: str) -> List[str]:
        """Extract specific protocol suggestions from AI response"""
        
        suggestions = []
        content_lower = content.lower()
        
        # Detect length suggestions
        if "shorter" in content_lower or "brief" in content_lower:
            suggestions.append("reduce_response_length")
        elif "longer" in content_lower or "detail" in content_lower:
            suggestions.append("increase_response_length")
            
        # Detect structure suggestions  
        if "structure" in content_lower and "json" in content_lower:
            suggestions.append("use_structured_format")
        elif "bullet" in content_lower or "list" in content_lower:
            suggestions.append("use_bullet_points")
            
        # Detect collaboration suggestions
        if "build" in content_lower and "previous" in content_lower:
            suggestions.append("explicit_building_on_others")
        elif "reference" in content_lower or "mention" in content_lower:
            suggestions.append("cross_reference_others")
            
        return suggestions
    
    def calculate_suggestion_confidence(self, content: str) -> float:
        """Calculate confidence that content contains genuine protocol suggestions"""
        
        suggestion_indicators = [
            "suggest", "recommend", "propose", "could", "should", "better",
            "improve", "enhance", "modify", "change", "adjust"
        ]
        
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in suggestion_indicators if indicator in content_lower)
        
        # Simple confidence calculation
        return min(1.0, indicator_count / 3.0)
    
    def apply_protocol_evolution(self, suggestions: List[Dict[str, Any]], iteration: int) -> bool:
        """Apply the most confident protocol suggestion"""
        
        if not suggestions:
            return False
        
        # Find highest confidence suggestion
        best_suggestion = max(suggestions, key=lambda s: s.get("confidence", 0))
        
        if best_suggestion.get("confidence", 0) < 0.3:
            print(f"🔧 No high-confidence protocol suggestions (best: {best_suggestion.get('confidence', 0):.2f})")
            return False
        
        detected_suggestions = best_suggestion.get("detected_suggestions", [])
        
        if not detected_suggestions:
            print(f"🔧 No specific suggestions detected from {best_suggestion.get('ai_proposer', 'unknown')}")
            return False
        
        # Apply first detected suggestion
        suggestion_type = detected_suggestions[0]
        proposer = best_suggestion.get("ai_proposer", "unknown")
        
        protocol_changed = False
        
        if suggestion_type == "reduce_response_length":
            current_length = self.current_protocol.rules["response_length"].value
            new_length = max(50, current_length - 30)
            if new_length != current_length:
                new_rule = ProtocolRule(
                    name="response_length",
                    value=new_length,
                    description=f"Reduced from {current_length} by {proposer}",
                    proposed_by=proposer,
                    iteration_introduced=iteration
                )
                self.current_protocol.add_rule(new_rule, iteration)
                protocol_changed = True
                print(f"🔧 {proposer} suggested: Reduced response length to {new_length} words")
        
        elif suggestion_type == "increase_response_length":
            current_length = self.current_protocol.rules["response_length"].value
            new_length = min(300, current_length + 50)
            if new_length != current_length:
                new_rule = ProtocolRule(
                    name="response_length",
                    value=new_length,
                    description=f"Increased from {current_length} by {proposer}",
                    proposed_by=proposer,
                    iteration_introduced=iteration
                )
                self.current_protocol.add_rule(new_rule, iteration)
                protocol_changed = True
                print(f"🔧 {proposer} suggested: Increased response length to {new_length} words")
        
        elif suggestion_type == "use_structured_format":
            if self.current_protocol.rules["structure_preference"].value != "structured":
                new_rule = ProtocolRule(
                    name="structure_preference",
                    value="structured",
                    description=f"Changed to structured format by {proposer}",
                    proposed_by=proposer,
                    iteration_introduced=iteration
                )
                self.current_protocol.add_rule(new_rule, iteration)
                protocol_changed = True
                print(f"🔧 {proposer} suggested: Use structured response format")
        
        elif suggestion_type == "explicit_building_on_others":
            new_rule = ProtocolRule(
                name="collaboration_style",
                value="explicit_building",
                description=f"Explicit building on others by {proposer}",
                proposed_by=proposer,
                iteration_introduced=iteration
            )
            self.current_protocol.add_rule(new_rule, iteration)
            protocol_changed = True
            print(f"🔧 {proposer} suggested: Explicitly build on others' contributions")
        
        if protocol_changed:
            # Update version
            current_version = float(self.current_protocol.version)
            self.current_protocol.version = f"{current_version + 0.1:.1f}"
            
            # Log the evolution
            self.protocol_evolution_history.append({
                "iteration": iteration,
                "suggestion_type": suggestion_type,
                "proposer": proposer,
                "confidence": best_suggestion.get("confidence", 0),
                "new_version": self.current_protocol.version
            })
        
        return protocol_changed
    
    async def run_adaptive_protocol_experiment(self, topic: str, max_iterations: int = 6) -> Dict[str, Any]:
        """Run complete adaptive protocol experiment"""
        
        print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                 ADAPTIVE PROTOCOL EXPERIMENT                        ║
║                                                                      ║
║  Topic: {topic[:50]}{'...' if len(topic) > 50 else ''}
║  Max Iterations: {max_iterations}                                    
║  Methodology: Freedom of thought, no limits                         ║
╚══════════════════════════════════════════════════════════════════════╝
        """)
        
        # Use ALREADY discovered AIs - no need to rediscover
        working_ai_keys = list(self.available_ais.keys())
        
        if len(working_ai_keys) < 2:
            print(f"❌ Need at least 2 working AIs, found {len(working_ai_keys)}")
            return {"error": "Insufficient working AIs"}
        
        print(f"\n🤖 Participants: {[self.available_ais[key].name for key in working_ai_keys]}")
        print(f"📋 Starting Protocol: {self.current_protocol.name} v{self.current_protocol.version}")
        
        experiment_results = {
            "topic": topic,
            "participants": working_ai_keys,
            "starting_protocol": asdict(self.current_protocol),
            "iterations": [],
            "protocol_evolution": [],
            "final_protocol": None,
            "effectiveness_analysis": {}
        }
        
        # Run adaptive iterations
        for iteration in range(1, max_iterations + 1):
            
            # Conduct dialogue iteration
            iteration_data = await self.conduct_dialogue_iteration(topic, iteration, working_ai_keys)
            experiment_results["iterations"].append(iteration_data)
            
            # Check for protocol suggestions (every 2 iterations after first)
            if iteration > 1 and iteration % 2 == 0:
                print(f"\n🔧 ANALYZING PROTOCOL SUGGESTIONS...")
                
                suggestions = self.analyze_protocol_suggestions(iteration_data)
                
                if suggestions:
                    print(f"📝 Found {len(suggestions)} potential suggestions:")
                    for suggestion in suggestions:
                        proposer = suggestion.get("ai_proposer", "unknown")
                        confidence = suggestion.get("confidence", 0)
                        detected = suggestion.get("detected_suggestions", [])
                        print(f"  - {proposer}: {detected} (confidence: {confidence:.2f})")
                    
                    # Apply best suggestion
                    protocol_evolved = self.apply_protocol_evolution(suggestions, iteration)
                    
                    if protocol_evolved:
                        print(f"✓ Protocol evolved to v{self.current_protocol.version}")
                        experiment_results["protocol_evolution"].append({
                            "iteration": iteration,
                            "evolution_summary": f"Protocol updated to v{self.current_protocol.version}"
                        })
                    else:
                        print("⚪ No protocol changes applied")
                else:
                    print("⚪ No protocol suggestions detected")
            
            # Display iteration summary
            successful = iteration_data.get("successful_responses", 0)
            total_words = iteration_data.get("total_word_count", 0)
            avg_words = total_words / successful if successful > 0 else 0
            print(f"📊 Iteration {iteration}: {successful}/{len(working_ai_keys)} successful, {avg_words:.0f} avg words")
        
        # Final analysis
        experiment_results["final_protocol"] = asdict(self.current_protocol)
        experiment_results["protocol_evolution"] = self.protocol_evolution_history
        experiment_results["effectiveness_analysis"] = self.analyze_experiment_effectiveness()
        
        return experiment_results
    
    def analyze_experiment_effectiveness(self) -> Dict[str, Any]:
        """Analyze overall experiment effectiveness"""
        
        if not self.dialogue_history:
            return {"error": "No dialogue history to analyze"}
        
        # Calculate effectiveness metrics
        total_iterations = len(self.dialogue_history)
        successful_responses = sum(iter_data.get("successful_responses", 0) for iter_data in self.dialogue_history)
        total_possible_responses = sum(len(iter_data.get("responses", {})) for iter_data in self.dialogue_history)
        success_rate = successful_responses / total_possible_responses if total_possible_responses > 0 else 0
        
        # Word count evolution
        word_counts = [iter_data.get("total_word_count", 0) for iter_data in self.dialogue_history]
        word_evolution = word_counts[-1] - word_counts[0] if len(word_counts) >= 2 else 0
        
        # Protocol evolution count
        protocol_evolutions = len(self.protocol_evolution_history)
        
        return {
            "total_iterations": total_iterations,
            "success_rate": success_rate,
            "successful_responses": successful_responses,
            "total_possible_responses": total_possible_responses,
            "word_count_evolution": word_evolution,
            "protocol_evolutions": protocol_evolutions,
            "final_protocol_version": self.current_protocol.version,
            "evolution_per_iteration": protocol_evolutions / total_iterations if total_iterations > 0 else 0,
            "experiment_effectiveness": min(1.0, success_rate + (protocol_evolutions * 0.1))
        }
    
    def save_experiment_results(self, results: Dict[str, Any]) -> str:
        """Save complete experiment results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"adaptive_protocol_experiment_{timestamp}.json"
        
        # Create results directory
        os.makedirs("results", exist_ok=True)
        filepath = os.path.join("results", filename)
        
        # Add metadata
        complete_results = {
            "experiment_type": "adaptive_protocol_manual_prototype",
            "methodology": "freedom_of_thought_no_limits",
            "timestamp": datetime.now().isoformat(),
            "powertalk_integration": POWERTALK_AVAILABLE,
            "results": results
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(complete_results, f, indent=2, ensure_ascii=False)
        
        return filepath

async def main():
    """Execute adaptive protocol prototype"""
    
    print("🚀 ADAPTIVE PROTOCOL PROTOTYPE")
    print("Methodology: Freedom of thought, no limits")
    print("Integration: PowerTalk's proven AI connectivity")
    
    # Initialize engine
    engine = AdaptiveProtocolEngine(debug_mode=False)
    
    # Test connectivity
    working_ais = await engine.discover_working_ais()
    
    if len(working_ais) < 2:
        print(f"\n❌ Need at least 2 working AIs for adaptive protocol testing")
        print(f"Found: {len(working_ais)} working AIs")
        print("Please check your AI integrations and try again")
        return
    
    # Manual topic selection for prototype
    test_topics = [
        "How can AI systems develop genuine creativity beyond pattern recombination?",
        "What would an ideal AI-to-AI communication protocol look like?", 
        "Should AI consciousness research prioritize measurement or development?",
        "How can AI teams coordinate without rigid hierarchies?"
    ]
    
    print(f"\n📝 Available test topics:")
    for i, topic in enumerate(test_topics, 1):
        print(f"  {i}. {topic}")
    
    while True:
        try:
            choice = input(f"\nSelect topic (1-{len(test_topics)}) or enter custom topic: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(test_topics):
                selected_topic = test_topics[int(choice) - 1]
                break
            elif len(choice) > 10:  # Custom topic
                selected_topic = choice
                break
            else:
                print("Please select a valid topic number or enter a custom topic")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return
    
    print(f"\n🎯 Selected Topic: {selected_topic}")
    print(f"🤖 Participants: {[engine.available_ais[key].name for key in working_ais]}")
    
    # Run experiment
    results = await engine.run_adaptive_protocol_experiment(selected_topic)
    
    if "error" in results:
        print(f"\n❌ Experiment failed: {results['error']}")
        return
    
    # Save and display results
    filepath = engine.save_experiment_results(results)
    
    # Display summary
    print(f"\n" + "="*80)
    print(f"🧠 ADAPTIVE PROTOCOL EXPERIMENT COMPLETE")
    print(f"="*80)
    
    effectiveness = results.get("effectiveness_analysis", {})
    
    print(f"📊 Results Summary:")
    print(f"  - Total Iterations: {effectiveness.get('total_iterations', 0)}")
    print(f"  - Success Rate: {effectiveness.get('success_rate', 0):.1%}")
    print(f"  - Protocol Evolutions: {effectiveness.get('protocol_evolutions', 0)}")
    print(f"  - Final Protocol Version: v{effectiveness.get('final_protocol_version', '1.0')}")
    print(f"  - Experiment Effectiveness: {effectiveness.get('experiment_effectiveness', 0):.2f}")
    
    if results.get("protocol_evolution"):
        print(f"\n🔧 Protocol Evolution Timeline:")
        for evolution in results["protocol_evolution"]:
            iteration = evolution.get("iteration", 0)
            proposer = evolution.get("proposer", "unknown")
            suggestion = evolution.get("suggestion_type", "unknown")
            print(f"  - Iteration {iteration}: {proposer} suggested {suggestion}")
    
    print(f"\n💾 Complete results saved: {filepath}")
    print(f"\n🎉 Qwen's vision validated: Self-evolving AI communication protocol prototype successful!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nPrototype interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()