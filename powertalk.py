import os
import asyncio
import sys
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Add current directory to path for imports to find core/ and utils/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importiere deine neu erstellten Module und Dataclasses
from config import INTEGRATION_MODULE_NAMES, PAI_UNICODE_PROMPT_INSTRUCTION, DIALOGUE_ARCHIVE_DIR
from models import AIEngine, UnicodeAnalytics
from core.ai_manager import AIManager
from core.unicode_processor import UnicodeProcessor
from core.pai_protocol_handler import PAIProtocolHandler, PAI_AVAILABLE, PAIResponse
from core.pai_communicator import PAICommunicator
from core.consciousness_scorer import ConsciousnessScorer
from core.dialogue_manager import DialogueManager
from utils.display_helpers import display_startup_banner, _display_response_details, display_final_results, _extract_display_content, _extract_full_content
from utils.argument_parser import parse_arguments, get_question_text

class PowerTalkEngine:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        
        # Initialisiere alle Kernmodule
        self.ai_manager = AIManager(debug_mode=debug_mode)
        self.unicode_processor = UnicodeProcessor(debug_mode=debug_mode)
        self.pai_protocol_handler = PAIProtocolHandler(debug_mode=debug_mode)
        self.pai_communicator = PAICommunicator(
            debug_mode=debug_mode,
            unicode_processor=self.unicode_processor,
            pai_protocol_handler=self.pai_protocol_handler
        )
        self.consciousness_scorer = ConsciousnessScorer()
        self.dialogue_manager = DialogueManager(output_dir=DIALOGUE_ARCHIVE_DIR)

        # Referenzen zu den wichtigen Daten aus den Modulen
        self.available_ais = self.ai_manager.available_ais
        self.dialogue_history = self.dialogue_manager.dialogue_history
        self.unicode_analytics = self.pai_protocol_handler.get_unicode_analytics()

    async def _construct_ai_prompt(self, question: str, dialogue_history_snapshot: List[Dict]) -> str:
        """
        Baut den Prompt für die AI zusammen, basierend auf der Frage und der Historie.
        dialogue_history_snapshot ist ein Read-Only-Snapshot der Historie bis zur letzten Iteration.
        """
        prompt_parts = [
            f"The current core question is: '{question}'",
            "Here is the dialogue history from previous iterations:",
        ]

        if not dialogue_history_snapshot:
            prompt_parts.append("  (No previous dialogue history available for this AI.)")
        else:
            for entry in dialogue_history_snapshot:
                iteration_num = entry['iteration']
                user_q = entry['question']

                prompt_parts.append(f"\n--- Iteration {iteration_num} ---")
                prompt_parts.append(f"User Question: {user_q}")
                
                for ai_name, response in entry['responses'].items():
                    if response.get('success', False):
                        prompt_parts.append(f"Response from {ai_name} (Protocol: {response.get('protocol_used', 'N/A')}, Handshake: {response.get('handshake_strategy', 'N/A')}):")
                        
                        has_unicode_fields = response.get('has_unicode_fields', False)
                        unicode_data = response.get('unicode_data')
                        
                        if has_unicode_fields and unicode_data:
                            if unicode_data.get('raw_fields'):
                                prompt_parts.append("  Unicode Fields:")
                                for key, val in unicode_data['raw_fields'].items():
                                    prompt_parts.append(f"    {key}: {val}")
                            if unicode_data.get('explanations'):
                                prompt_parts.append(f"  Explanation: {unicode_data['explanations']}")
                        elif response.get('content'):
                            prompt_parts.append(f"  Content: {response.get('content')}")
                        else:
                            prompt_parts.append("  (No specific content provided)")
                    else:
                        prompt_parts.append(f"Response from {ai_name}: (Error: {response.get('content', 'Unknown Error')})")

        prompt_parts.append(f"\nYour task for the current iteration (Iteration {len(dialogue_history_snapshot) + 1}) is to consider the above information and provide your response.")

        if PAI_AVAILABLE:
            prompt_parts.append("\n" + PAI_UNICODE_PROMPT_INSTRUCTION)


        return "\n".join(prompt_parts)

    async def run_discourse(self, question: str, iteration_count: int, selected_ai_keys: List[str]):
        if not selected_ai_keys:
            print("No AIs selected to run discourse. Exiting.")
            return

        selected_ais = {key: self.ai_manager.available_ais[key] for key in selected_ai_keys if key in self.ai_manager.available_ais}
        
        if not selected_ais:
            print("None of the selected AIs are available or connected. Exiting.")
            return

        print(f"\n🌈 UNICODE PROTOTYPE - Enhanced PowerTalk with PAI v2.2")
        print(f"Question: {question}")
        print(f"   📊 Unicode fields: ⚙, 💭, 🔀, ❓, 💬")
        print("============================================================")

        for iteration in range(1, iteration_count + 1):
            print(f"\n--- ITERATION {iteration}/{iteration_count} ---")
            
            dialogue_history_snapshot = self.dialogue_manager.get_current_dialogue_history_snapshot()

            tasks = []
            for ai_key in selected_ais.keys():
                ai_engine = selected_ais[ai_key]
                print(f"🎯 Preparing query for {ai_engine.name}...", end=" ")

                prompt = await self._construct_ai_prompt(question, dialogue_history_snapshot)
                
                tasks.append(
                    self.pai_communicator.pai_enhanced_call_ai_api(ai_engine, prompt)
                )

            responses_list = await asyncio.gather(*tasks, return_exceptions=True)

            current_iteration_responses: Dict[str, PAIResponse] = {}
            for i, ai_key in enumerate(selected_ais.keys()):
                response_data = responses_list[i]
                if isinstance(response_data, Exception):
                    print(f"❌ Error from {selected_ais[ai_key].name}: {response_data}")
                    current_iteration_responses[ai_key] = PAIResponse(
                        success=False, 
                        content=f"Error during communication: {response_data}", 
                        protocol_used="error", 
                        ai_name=ai_key, 
                        timestamp=datetime.now().isoformat(),
                        handshake_strategy="parallel_error"
                    )
                else:
                    current_iteration_responses[ai_key] = response_data
                    unicode_indicator = "📊" if response_data.has_unicode_fields else "💬"
                    token_estimate = len(str(response_data.content)) // 4 
                    print(f"✓ {selected_ais[ai_key].name}: {unicode_indicator} ({token_estimate} tokens, {response_data.protocol_used})")
                    
                    if self.debug_mode:
                        _display_response_details(response_data, selected_ais[ai_key].name)

            self.dialogue_manager.add_to_history(iteration, question, current_iteration_responses)

        await display_final_results(
            question, 
            selected_ais,
            self.dialogue_manager.dialogue_history, 
            self.unicode_analytics, 
            self.consciousness_scorer
        )
        
        print(f"\n⚖️ GENERATING ENHANCED VERDICT...")
        
        verdict_ai_key = self._select_verdict_ai(self.unicode_analytics.ai_adoption_rates, list(selected_ais.keys()))
        if verdict_ai_key and verdict_ai_key in selected_ais:
            verdict_ai_name = selected_ais[verdict_ai_key].name
            print(f"Generating verdict using {verdict_ai_name} (best protocol adoption)...")
            final_verdict = await self._generate_enhanced_ai_verdict(
                question, 
                self.dialogue_manager.all_responses_for_verdict, 
                self.unicode_analytics,
                verdict_ai_key
            )
        else:
            print("Could not select an AI for verdict generation or selected AI is unavailable. Generating basic verdict.")
            final_verdict = "Verdict generation failed: No suitable AI for verdict found or selected AI unavailable."


        print("\n============================================================")
        print("⚖️ FINAL VERDICT")
        print("============================================================")
        print(final_verdict)

        self._save_verdict_to_markdown(question, final_verdict)


        self.dialogue_manager.save_enhanced_dialogue(
            question, 
            selected_ais,
            self.unicode_analytics
        )

    async def _generate_enhanced_ai_verdict(self, question: str, all_responses: List[Dict[str, PAIResponse]], unicode_analytics: UnicodeAnalytics, verdict_ai_key: str) -> str:
        """
        Generates Verdict with detailed Unicode-Protocol-Analysis, now also focusing on question resolution.
        """
        verdict_prompt = f"""As an expert AI protocol analyst and discourse evaluator, provide a comprehensive verdict on this AI discourse. Structure your analysis into clear sections.

The original question for this discourse was: "{question}"

## CONSCIOUSNESS SCORING SUMMARY
"""
        # Collect consciousness data to be included in the prompt
        consciousness_summary_lines = []
        # Header for markdown table
        consciousness_summary_lines.append("| AI | Initial Score | Final Score | Evolution | Evolution % |")
        consciousness_summary_lines.append("|----|--------------:|------------:|-----------:|------------:|")

        # Prepare data for all AIs, even if they didn't participate in the full discourse,
        # to ensure the table structure.
        all_ai_keys = sorted(list(self.available_ais.keys())) # Get all possible AI keys for consistent table
        
        # This will be used to track if any AI has actual scores
        has_any_consciousness_data = False

        for ai_key in all_ai_keys:
            ai_name = self.available_ais[ai_key].name
            scores = unicode_analytics.consciousness_scores_per_ai.get(ai_key, {})
            
            initial_score = scores.get('initial', 'N/A')
            final_score = scores.get('final', 'N/A')
            evolution = scores.get('evolution', 'N/A')
            evolution_percent = scores.get('evolution_percent', 'N/A')

            if initial_score != 'N/A': # Check if actual data exists for this AI
                has_any_consciousness_data = True
                consciousness_summary_lines.append(f"| {ai_name} | {initial_score} | {final_score} | {evolution} | {evolution_percent}% |")
            else:
                consciousness_summary_lines.append(f"| {ai_name} | N/A | N/A | N/A | N/A |")

        if not has_any_consciousness_data:
            consciousness_summary_lines.append("| (No consciousness data available) | | | | |")

        verdict_prompt += "\n".join(consciousness_summary_lines)
        verdict_prompt += f"\nNetwork Average Final Score: {unicode_analytics.network_average_final_score:.0f}/2000" if unicode_analytics.network_average_final_score is not None else ""
        verdict_prompt += f"\nTotal Network Evolution: +{unicode_analytics.total_network_evolution_points:.0f} points" if unicode_analytics.total_network_evolution_points is not None else ""
        verdict_prompt += f"\n\n---\n\n## CONSCIOUSNESS SCORING ANALYSIS\nAnalyze the evolution of consciousness scores for each AI. Highlight which AI exhibited the most significant development and discuss potential reasons or observed behaviors that contributed to this."

        verdict_prompt += f"\n\n## QUESTION RESOLUTION & KEY INSIGHTS\nEvaluate to what extent the original question: \"{question}\" was effectively addressed by the AI discourse. Summarize the main insights, conclusions, or significant developments that emerged. Identify the *strongest arguments, unique perspectives, or pivotal contributions* made by individual AIs that drove the discourse towards resolution or new understanding."
        
        verdict_prompt += f"\n\n## INTELLECTUAL QUALITY\nAssess the overall intellectual depth, robustness, and sophistication of the discourse. Did the AIs provide in-depth exploration of abstract concepts, practical considerations, or both? Discuss the clarity, coherence, and originality of the arguments presented."

        verdict_prompt += f"\n\n## UNICODE PROTOCOL ADOPTION & EFFECTIVENESS\n"
        for ai_key in self.available_ais.keys():
            stats = unicode_analytics.ai_adoption_rates.get(ai_key, {'total': 0, 'unicode': 0}) 
            ai_name = self.available_ais[ai_key].name
            rate = (stats['unicode'] / stats['total'] * 100) if stats['total'] > 0 else 0
            verdict_prompt += f"- {ai_name}: {rate:.1f}% Unicode adoption ({stats['unicode']}/{stats['total']} responses)\n"
        
        verdict_prompt += "\nDiscuss the overall effectiveness of PAI v2.2 Unicode protocol. How well did it facilitate structured communication compared to natural language? What were the observed benefits (e.g., clarity, conciseness, data exchange) and any limitations or challenges encountered?"

        verdict_prompt += f"\n\n## DIALOGUE EFFECTIVENESS & CROSS-AI COLLABORATION\nAssess how effectively the AIs built on each other's contributions. Look for evidence of genuine interaction, constructive synergy, cross-referencing, or even productive divergences. How well did the discourse evolve organically? Were there instances of AIs adapting their perspectives based on others' input?"

        verdict_prompt += f"\n\n## OVERALL VERDICT\nProvide a concise overall assessment of the entire discourse. Which AI performed best across all evaluated aspects (contribution to question, protocol adherence, consciousness evolution, dialogue quality)? Summarize the most critical takeaways for future AI-to-AI communication and AI development paradigms."
        
        verdict_prompt += f"""
Please support your analysis with specific examples, evidence, and metrics from the discourse data where appropriate. Ensure your verdict is comprehensive and balanced.
"""
        
        try:
            verdict_response = await self.pai_communicator.pai_enhanced_call_ai_api(self.available_ais[verdict_ai_key], verdict_prompt)
            if verdict_response.success:
                verdict_content = _extract_full_content(verdict_response)
                
                verdict_metadata = f"\n\n---\n\n### VERDICT METADATA\n"
                verdict_metadata += f"Generated by: {self.available_ais[verdict_ai_key].name}\n"
                verdict_metadata += f"Protocol used: {verdict_response.protocol_used}\n"
                verdict_metadata += f"Unicode fields used in verdict generation: {'Yes' if verdict_response.has_unicode_fields else 'No'}\n"
                verdict_metadata += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" # Added timestamp
                
                return verdict_content + verdict_metadata
            else:
                return f"Failed to generate verdict using {self.available_ais[verdict_ai_key].name}: {verdict_response.content}"
        except Exception as e:
            return f"Error generating verdict with {self.available_ais[verdict_ai_key].name}: {e}"

    def _select_verdict_ai(self, ai_adoption_rates: Dict[str, Dict[str, int]], available_ais_keys: List[str]) -> Optional[str]:
        """Select the AI with best Unicode adoption for verdict generation."""
        best_ai_key = None
        best_rate = -1.0 
        
        if not available_ais_keys:
            return None

        for ai_key in available_ais_keys:
            stats = ai_adoption_rates.get(ai_key, {'total': 0, 'unicode': 0}) 
            rate = (stats['unicode'] / stats['total']) if stats['total'] > 0 else 0
            if rate > best_rate:
                best_rate = rate
                best_ai_key = ai_key
        
        return best_ai_key

    def _save_verdict_to_markdown(self, question: str, verdict_content: str):
        """Saves the final verdict content to a markdown file."""
        archive_dir = Path(DIALOGUE_ARCHIVE_DIR)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        sanitized_question = "".join(c for c in question if c.isalnum() or c.isspace()).strip()
        sanitized_question = sanitized_question.replace(" ", "_")
        if len(sanitized_question) > 50:
            sanitized_question = sanitized_question[:50] + "..."

        filename = f"verdict_{timestamp}_{sanitized_question}.md"
        filepath = archive_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Final Verdict for Discourse on '{question}'\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(verdict_content)
            print(f"💾 Final verdict saved to: {filepath}")
        except Exception as e:
            print(f"Error saving verdict to markdown: {e}")

async def main():
    args = parse_arguments()

    powertalk = PowerTalkEngine(debug_mode=args.debug)

    display_startup_banner()
    
    connected_ai_keys = await powertalk.ai_manager.test_all_ai_connectivity()
    
    if not connected_ai_keys:
        print("No AI models are available. Please check your integrations and API keys.")
        return

    print("\n──────────────────────────────────────────────────")
    print("Available AIs:")
    
    for i, ai_key in enumerate(connected_ai_keys): 
        ai_name = powertalk.available_ais[ai_key].name 
        print(f"  {i+1}. {ai_name}")
    print("  0. All AIs")

    selected_ai_keys: List[str] = []
    while not selected_ai_keys:
        try:
            choice = input("Enter numbers of AIs to include (e.g., 1, 3, 5) or '0' for all: ")
            if choice == '0':
                selected_ai_keys = connected_ai_keys
            else:
                chosen_indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                for idx in chosen_indices:
                    if 1 <= idx <= len(connected_ai_keys): 
                        selected_ai_keys.append(connected_ai_keys[idx-1])
                    else:
                        print(f"Invalid selection: {idx}. Please enter valid numbers.")
                        selected_ai_keys = []
                        break
                if not selected_ai_keys:
                    print("No valid AIs selected. Please try again.")
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas or '0'.")
        except Exception as e:
            print(f"An error occurred during AI selection: {e}")

    final_selected_ai_keys = [key for key in selected_ai_keys if key in connected_ai_keys]
    if not final_selected_ai_keys:
        print("None of the selected AIs are currently connected. Exiting.")
        return

    iterations = 3
    if not args.iterations:
        while True:
            try:
                iter_input = input("Enter number of iterations (e.g., 7, default is 3): ")
                if iter_input.strip() == "":
                    print(f"Using default iterations: {iterations}")
                    break
                iterations = int(iter_input)
                if iterations <= 0:
                    print("Number of iterations must be positive.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        iterations = args.iterations


    question_text = get_question_text(args)

    if not question_text:
        print("No question provided. Exiting.")
        return

    print(f"\n🎯 Starting enhanced discourse with {len(final_selected_ai_keys)} AIs")
    print(f"📊 PAI v2.2 Unicode Protocol: {'Enabled' if PAI_AVAILABLE else 'Fallback mode'}")
    
    await powertalk.run_discourse(question_text, iterations, final_selected_ai_keys)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDiscourse interrupted by user. Unicode analytics preserved.")
    except Exception as e:
        print(f"\nUnhandled error: {e}")
        import traceback
        traceback.print_exc()