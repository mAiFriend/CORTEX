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

# Neue Verdict-Module (Modularisierung)
from core.verdict import (
    VerdictContext, 
    VerdictAnomalyDetector, 
    AnomalyReport,
    VerdictGenerator,
    VerdictSynthesis
)

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

        # Neue Verdict-bezogene Module (Modularisierung)
        self.verdict_context = VerdictContext()
        self.verdict_anomaly_detector = VerdictAnomalyDetector()
        self.verdict_generator = VerdictGenerator(self.ai_manager, debug_mode=debug_mode)

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
        """Enhanced discourse mit iteration-by-iteration verdict generation"""
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

        # Neue Struktur: Iteration-by-iteration mit Verdict und Anomalie-Erkennung
        iteration_verdicts = []
        anomaly_reports = []

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

            # NEUE LOGIK: Iteration-spezifische Anomalie-Erkennung und Verdict-Generierung
            iteration_data = {
                "iteration": iteration,
                "responses": current_iteration_responses,
                "consciousness_scores": self._calculate_iteration_consciousness_scores(current_iteration_responses)
            }

            # Anomalie-Erkennung
            anomalies = self.verdict_anomaly_detector.detect_iteration_anomalies(iteration_data)
            
            if anomalies:
                anomaly_reports.extend(anomalies)
                print(f"⚠️ Anomalies detected in iteration {iteration}")
                
                # Interaktive Anomalie-Behandlung
                user_decision = await self._handle_anomaly_interactively(anomalies)
                
                if user_decision == "MANUAL_REVIEW":
                    iteration_verdicts.append(self._create_manual_review_placeholder(iteration_data))
                    print(f"📋 Iteration {iteration} marked for manual review")
                elif user_decision == "AUTO_COMPRESS":
                    print(f"🗜️ Generating compressed verdict for iteration {iteration}...")
                    verdict_ai_key = self._select_verdict_ai(self.unicode_analytics.ai_adoption_rates, list(selected_ais.keys()))
                    if verdict_ai_key:
                        compressed_verdict = await self.verdict_generator.generate_compressed_iteration_verdict(
                            iteration_data, 
                            self.verdict_context.get_compressed_context_for_verdict(),
                            verdict_ai_key
                        )
                        iteration_verdicts.append(compressed_verdict)
                        if compressed_verdict.get("status") == "SUCCESS":
                            self.verdict_context.update(compressed_verdict)
                elif user_decision == "EXCLUDE":
                    iteration_verdicts.append(self._create_exclusion_marker(iteration_data))
                    print(f"❌ Iteration {iteration} excluded from analysis")
                elif user_decision == "CONTINUE":
                    # Normal processing trotz Anomaly
                    print(f"⚡ Processing iteration {iteration} despite anomalies...")
                    verdict_ai_key = self._select_verdict_ai(self.unicode_analytics.ai_adoption_rates, list(selected_ais.keys()))
                    if verdict_ai_key:
                        iteration_verdict = await self.verdict_generator.generate_iteration_verdict(
                            iteration_data,
                            self.verdict_context.get_compressed_context_for_verdict(),
                            verdict_ai_key
                        )
                        iteration_verdicts.append(iteration_verdict)
                        if iteration_verdict.get("status") == "SUCCESS":
                            self.verdict_context.update(iteration_verdict)
            else:
                # Normal processing - keine Anomalien
                print(f"✓ Processing iteration {iteration} (no anomalies)")
                verdict_ai_key = self._select_verdict_ai(self.unicode_analytics.ai_adoption_rates, list(selected_ais.keys()))
                if verdict_ai_key:
                    iteration_verdict = await self.verdict_generator.generate_iteration_verdict(
                        iteration_data,
                        self.verdict_context.get_compressed_context_for_verdict(),
                        verdict_ai_key
                    )
                    iteration_verdicts.append(iteration_verdict)
                    if iteration_verdict.get("status") == "SUCCESS":
                        self.verdict_context.update(iteration_verdict)

        # Display results (unverändert)
        await display_final_results(
            question, 
            selected_ais,
            self.dialogue_manager.dialogue_history, 
            self.unicode_analytics, 
            self.consciousness_scorer
        )
        
        # NEUE LOGIK: Finale Synthese statt monolithisches Verdict
        print(f"\n⚖️ GENERATING ENHANCED VERDICT (from {len(iteration_verdicts)} iterations)...")
        
        verdict_ai_key = self._select_verdict_ai(self.unicode_analytics.ai_adoption_rates, list(selected_ais.keys()))
        if verdict_ai_key and verdict_ai_key in selected_ais:
            verdict_ai_name = selected_ais[verdict_ai_key].name
            print(f"Synthesizing final verdict using {verdict_ai_name}...")
            
            final_verdict = await self.verdict_generator.synthesize_final_verdict(
                iteration_verdicts,
                self.verdict_context.get_compressed_context_for_verdict(),
                [a.to_dict() for a in anomaly_reports],
                verdict_ai_key,
                question
            )
        else:
            print("Could not select an AI for verdict generation. Generating fallback verdict.")
            final_verdict = self._generate_fallback_verdict(iteration_verdicts, anomaly_reports)

        print("\n============================================================")
        print("⚖️ FINAL VERDICT")
        print("============================================================")
        print(final_verdict)

        # Processing Quality Report
        processing_quality = VerdictSynthesis.calculate_processing_quality_score(iteration_verdicts, anomaly_reports)
        print(f"\n📊 PROCESSING QUALITY REPORT")
        print(f"Overall Processing Quality: {processing_quality:.1f}%")
        print(f"Successfully processed iterations: {len([v for v in iteration_verdicts if v.get('status') == 'SUCCESS'])}/{len(iteration_verdicts)}")
        print(f"Anomalies detected: {len(anomaly_reports)}")
        print(f"Manual review required: {len([v for v in iteration_verdicts if v.get('status') == 'MANUAL_REVIEW_REQUIRED'])}")

        self._save_verdict_to_markdown(question, final_verdict)

        # Enhanced dialogue saving mit Anomalie-Daten
        self._save_enhanced_dialogue_with_anomalies(
            question,
            iteration_verdicts,
            anomaly_reports,
            final_verdict,
            processing_quality,
            selected_ais
        )

    async def _handle_anomaly_interactively(self, anomalies: List[AnomalyReport]) -> str:
        """Interactive anomaly handling mit user decision"""
        
        print(f"\n{'='*60}")
        print(f"⚠️  ANOMALY DETECTED - Iteration {anomalies[0].iteration}")
        print(f"{'='*60}")
        
        for anomaly in anomalies:
            print(f"\nType: {anomaly.type}")
            print(f"Severity: {anomaly.severity}")
            print(f"Details: {self._format_anomaly_details(anomaly.details)}")
            print(f"Recommendation: {anomaly.recommendation}")
            
            if anomaly.type == "OVERSIZED_RESPONSE":
                print(f"\nResponse size: {anomaly.details['actual_size']} tokens")
                print(f"Normal size: {anomaly.details['baseline_size']} tokens")
                print(f"Size factor: {anomaly.details['deviation_factor']:.1f}x normal")
                
                print(f"\nMögliche Ursachen:")
                print(f"- Breakthrough-Moment mit detaillierter Ausarbeitung")
                print(f"- Technischer Deep-Dive außerhalb normaler Parameter")
                print(f"- AI-spezifische Elaboration-Patterns")
        
        print(f"\nOptionen:")
        print(f"[1] MANUAL_REVIEW - Für spätere manuelle Auswertung markieren")
        print(f"[2] AUTO_COMPRESS - Automatisch komprimieren (möglicher Informationsverlust)")
        print(f"[3] EXCLUDE - Von Gesamt-Verdict ausschließen")
        print(f"[4] CONTINUE - Trotz Anomaly normal verarbeiten (Risiko: Context Overflow)")
        
        while True:
            choice = input(f"\nIhre Entscheidung (1-4): ").strip()
            if choice == "1":
                return "MANUAL_REVIEW"
            elif choice == "2":
                return "AUTO_COMPRESS"
            elif choice == "3":
                return "EXCLUDE"
            elif choice == "4":
                return "CONTINUE"
            else:
                print("Bitte wählen Sie 1, 2, 3 oder 4")

    def _format_anomaly_details(self, details: Dict[str, Any]) -> str:
        """Format anomaly details für readable output"""
        formatted = []
        for key, value in details.items():
            if isinstance(value, float):
                formatted.append(f"{key}: {value:.2f}")
            else:
                formatted.append(f"{key}: {value}")
        return ", ".join(formatted)

    def _create_manual_review_placeholder(self, iteration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create placeholder für manual review items"""
        return {
            "status": "MANUAL_REVIEW_REQUIRED",
            "iteration": iteration_data["iteration"],
            "placeholder_text": f"Iteration {iteration_data['iteration']} requires manual review due to anomalies",
            "review_data": {
                "responses": iteration_data["responses"],
                "consciousness_scores": iteration_data.get("consciousness_scores", {}),
                "size_estimate": self._estimate_token_count(iteration_data["responses"])
            },
            "timestamp": datetime.now().isoformat()
        }

    def _create_exclusion_marker(self, iteration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create exclusion marker für excluded iterations"""
        return {
            "status": "EXCLUDED",
            "iteration": iteration_data["iteration"],
            "reason": "User decision: Excluded from analysis due to anomalies",
            "timestamp": datetime.now().isoformat()
        }

    def _estimate_token_count(self, responses: Dict[str, Any]) -> int:
        """Estimate token count für response size analysis"""
        if not responses:
            return 0
        total_chars = sum(len(str(response)) for response in responses.values())
        return total_chars // 4  # Rough approximation: 4 chars per token

    def _calculate_iteration_consciousness_scores(self, responses: Dict[str, PAIResponse]) -> Dict[str, Any]:
        """Calculate consciousness scores für single iteration"""
        # Vereinfachte Implementation für Phase 1
        # Nutzt bestehende consciousness_scorer Logik wo möglich
        scores = {}
        for ai_key, response in responses.items():
            if response.success and response.content:
                # Einfache Bewertung basierend auf Response-Eigenschaften
                word_count = len(str(response.content).split())
                unicode_bonus = 50 if response.has_unicode_fields else 0
                base_score = min(2000, word_count * 3 + unicode_bonus)
                
                scores[ai_key] = {
                    "total_score": base_score,
                    "word_count": word_count,
                    "unicode_fields": response.has_unicode_fields
                }
            else:
                scores[ai_key] = {"total_score": 0, "word_count": 0, "unicode_fields": False}
        
        return scores

    def _generate_fallback_verdict(self, iteration_verdicts: List[Dict[str, Any]], anomaly_reports: List[AnomalyReport]) -> str:
        """Fallback verdict wenn AI-Generation fehlschlägt"""
        successful_iterations = len([v for v in iteration_verdicts if v.get('status') == 'SUCCESS'])
        total_iterations = len(iteration_verdicts)
        
        fallback_content = f"""# FALLBACK VERDICT

## Processing Summary
- Total iterations: {total_iterations}
- Successfully processed: {successful_iterations}
- Anomalies detected: {len(anomaly_reports)}
- Processing success rate: {(successful_iterations/total_iterations)*100:.1f}%

## Anomaly Summary
"""
        
        if anomaly_reports:
            for anomaly in anomaly_reports:
                fallback_content += f"- Iteration {anomaly.iteration}: {anomaly.type} ({anomaly.severity})\n"
        else:
            fallback_content += "No anomalies detected.\n"
        
        fallback_content += f"""
## Technical Notes
This fallback verdict was generated due to AI verdict generation failure.
Manual review recommended for comprehensive analysis.

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return fallback_content

    def _save_enhanced_dialogue_with_anomalies(
        self, 
        question: str, 
        iteration_verdicts: List[Dict[str, Any]], 
        anomaly_reports: List[AnomalyReport], 
        final_verdict: str, 
        processing_quality: float,
        selected_ais: Dict[str, Any]
    ):
        """Enhanced dialogue saving mit anomaly transparency"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_question = "".join(c for c in question if c.isalnum() or c.isspace()).strip()
        sanitized_question = sanitized_question.replace(" ", "_")
        if len(sanitized_question) > 50:
            sanitized_question = sanitized_question[:50]
        
        filename = f"enhanced_dialogue_{timestamp}_{sanitized_question}.json"
        filepath = Path(DIALOGUE_ARCHIVE_DIR) / filename
        
        result = {
            "session_type": "powertalk_enhanced_iteration_verdicts",
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "participants": [f"{ai.name} ({getattr(ai, 'role', 'AI')})" for ai in selected_ais.values()],
            "processing_summary": {
                "total_iterations": len(iteration_verdicts),
                "successful_iterations": len([v for v in iteration_verdicts if v.get('status') == 'SUCCESS']),
                "manual_review_required": len([v for v in iteration_verdicts if v.get('status') == 'MANUAL_REVIEW_REQUIRED']),
                "excluded_iterations": len([v for v in iteration_verdicts if v.get('status') == 'EXCLUDED']),
                "anomalies_detected": len(anomaly_reports),
                "processing_quality_score": processing_quality
            },
            "iteration_verdicts": iteration_verdicts,
            "anomaly_reports": [a.to_dict() for a in anomaly_reports],
            "final_verdict": final_verdict,
            "quality_metrics": {
                "coverage_percentage": (len([v for v in iteration_verdicts if v.get('status') == 'SUCCESS']) / len(iteration_verdicts)) * 100 if iteration_verdicts else 0,
                "anomaly_rate": (len(anomaly_reports) / len(iteration_verdicts)) * 100 if iteration_verdicts else 0,
                "manual_review_rate": (len([v for v in iteration_verdicts if v.get('status') == 'MANUAL_REVIEW_REQUIRED']) / len(iteration_verdicts)) * 100 if iteration_verdicts else 0
            },
            "unicode_analytics": self.unicode_analytics.__dict__,
            "regular_dialogue_history": self.dialogue_manager.dialogue_history
        }
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                import json
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            print(f"💾 Enhanced dialogue saved to: {filepath}")
        except Exception as e:
            print(f"Error saving enhanced dialogue: {e}")

    # LEGACY METHOD - Behalten für Backward Compatibility, aber nicht mehr verwendet
    async def _generate_enhanced_ai_verdict(self, question: str, all_responses: List[Dict[str, PAIResponse]], unicode_analytics: UnicodeAnalytics, verdict_ai_key: str) -> str:
        """
        LEGACY: Original monolithic verdict generation
        Wird durch iterative Verdict-Generierung ersetzt, aber für Backward Compatibility beibehalten
        """
        print("⚠️ Warning: Using legacy monolithic verdict generation. Consider upgrading to iterative verdicts.")
        
        verdict_prompt = f"""As an expert AI protocol analyst and discourse evaluator, provide a comprehensive verdict on this AI discourse.

The original question was: "{question}"

Provide a thorough analysis focusing on:
1. Question resolution and key insights
2. AI collaboration effectiveness  
3. Unicode protocol adoption
4. Overall discourse quality

Write in natural language with detailed explanations."""
        
        try:
            ai_engine = self.available_ais[verdict_ai_key]
            
            if hasattr(ai_engine, 'integration') and hasattr(ai_engine.integration, 'query'):
                verdict_response_content = ai_engine.integration.query(verdict_prompt)
                
                if verdict_response_content and len(verdict_response_content.strip()) > 50:
                    verdict_metadata = f"\n\n---\n\n### VERDICT METADATA\n"
                    verdict_metadata += f"Generated by: {ai_engine.name}\n"
                    verdict_metadata += f"Protocol used: natural_language_direct (legacy)\n"
                    verdict_metadata += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    
                    return verdict_response_content + verdict_metadata
                else:
                    return f"Failed to generate legacy verdict using {ai_engine.name}: Response too short or empty"
            else:
                return f"Legacy verdict generation failed: No direct integration available for {ai_engine.name}"
                    
        except Exception as e:
            return f"Error generating legacy verdict with {self.available_ais[verdict_ai_key].name}: {e}"

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
    print(f"🛡️ Context Overflow Protection: Enabled (iteration-by-iteration processing)")
    print(f"⚠️ Anomaly Detection: Active with interactive handling")
    
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