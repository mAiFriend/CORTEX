#!/usr/bin/env python3
"""
CORTEX Session - Main Orchestrator Module (CLEAN VERSION)
Coordinates the complete CORTEX Flow session with clarification round
"""

import asyncio
import yaml
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables...")

from cortex_types import (
    CortexReport, IterationRound, AIResponse, 
    CortexSessionError, META_ANALYSIS_CONFIG
)


class CortexSession:
    """Main orchestrator for CORTEX stateless AI collaboration sessions"""
    
    def __init__(self, config_path: str):
        """Initialize CORTEX session with configuration"""
        print("🌊 Initializing CORTEX Flow session...")
        
        # Load and validate configuration
        self.config = self._load_and_validate_config(config_path)
        
        # Initialize components after config validation
        self._initialize_components()
        
        # Session tracking
        self.session_data = {
            'experiment_name': self.config.get('experiment', {}).get('name', 'Unnamed Session'),
            'original_topic': self.config.get('topic', ''),
            'ai_team': [],
            'iterations': [],
            'meta_analyses': [],
            'metadata': {
                'start_time': datetime.now(),
                'config_path': config_path,
                'cortex_version': '3.0'
            }
        }
        
        print("✅ CORTEX Flow initialization complete!")
    
    def _load_and_validate_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration file with comprehensive error handling"""
        try:
            if not Path(config_path).exists():
                raise CortexSessionError(f"Configuration file not found: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                raise CortexSessionError(f"Empty or invalid YAML file: {config_path}")
            
            # Validate required sections
            self._validate_config_structure(config)
            
            # Apply defaults where missing
            config = self._apply_config_defaults(config)
            
            print(f"✅ Configuration loaded and validated: {config_path}")
            return config
            
        except yaml.YAMLError as e:
            raise CortexSessionError(f"YAML parsing error in {config_path}: {e}")
        except Exception as e:
            raise CortexSessionError(f"Failed to load configuration: {e}")
    
    def _validate_config_structure(self, config: Dict[str, Any]) -> None:
        """Validate required configuration structure"""
        required_fields = {
            'ai_team': list,
            'topic': str,
        }
        
        for field, expected_type in required_fields.items():
            if field not in config:
                raise CortexSessionError(f"Missing required configuration field: {field}")
            
            if not isinstance(config[field], expected_type):
                raise CortexSessionError(
                    f"Configuration field '{field}' must be {expected_type.__name__}, "
                    f"got {type(config[field]).__name__}"
                )
        
        # Validate AI team
        if not config['ai_team']:
            raise CortexSessionError("AI team cannot be empty")
        
        valid_ais = {'claude', 'chatgpt', 'gemini', 'qwen', 'deepseek'}
        for ai in config['ai_team']:
            if ai not in valid_ais:
                raise CortexSessionError(f"Unknown AI in team: {ai}. Valid AIs: {valid_ais}")
    
    def _apply_config_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply sensible defaults to configuration"""
        defaults = {
            'experiment': {
                'name': f"CORTEX Session {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'max_iterations': 3
            },
            'execution': {
                'timeout_seconds': 120,
                'min_ais_required': 1,
                'graceful_mode': True
            },
            'context_management': {
                'truncation': {
                    'method': 'smart_sentence_aware',
                    'limit_chars': 1200
                },
                'front_loading': {
                    'enabled': True,
                    'enforcement_level': 'suggested'
                }
            },
            'meta_analysis': META_ANALYSIS_CONFIG.copy(),
            'output': {
                'format': 'markdown',
                'save_conversation_log': False
            },
            'nutshell': {
                'ai_generated': False,
                'strategy': 'intelligent'
            },
            'clarification': {
                'enabled': True,
                'max_questions': 6,
                'interactive_mode': True,
                'auto_enhance': True
            },
            'ruleset_sequence': ['creative_exploration', 'analytical_synthesis'],
            'rulesets': {
                'creative_exploration': {
                    'creativity_level': 'high',
                    'challenge_assumptions': True
                },
                'analytical_synthesis': {
                    'synthesis_focus': True,
                    'practical_implications': True
                }
            }
        }
        
        def deep_merge(base: Dict, override: Dict) -> Dict:
            """Deep merge dictionaries, with override taking precedence"""
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(defaults, config)
    
    def _initialize_components(self) -> None:
        """Initialize components with proper dependency injection to avoid circular imports"""
        # Import here to avoid circular dependencies
        from context_processor import ContextProcessor
        from ai_orchestrator import AIOrchestrator
        from report_generator import ReportGenerator
        
        try:
            self.context_processor = ContextProcessor(self.config)
            self.ai_orchestrator = AIOrchestrator(self.config)
            self.report_generator = ReportGenerator(self.config)
            
        except Exception as e:
            raise CortexSessionError(f"Failed to initialize components: {e}")
    
    async def run_session(self) -> CortexReport:
        """Execute the complete CORTEX session with comprehensive error handling"""
        try:
            print(f"\n🎯 Starting CORTEX session: {self.session_data['experiment_name']}")
            print(f"📝 Topic: {self.config['topic']}")
            
            # Validate AI team availability
            available_ais = await self.ai_orchestrator.validate_ai_team(self.config['ai_team'])
            self.session_data['ai_team'] = available_ais
            
            if not available_ais:
                raise CortexSessionError("No AI providers available")
            
            print(f"🤖 Available AI team: {', '.join(available_ais)}")
            
            # Execute clarification round (Iteration 0) if enabled
            clarified_topic = self.config['topic']
            if self.config.get('clarification', {}).get('enabled', True):
                print(f"\n🔍 Starting clarification round...")
                clarified_topic = await self._execute_clarification_round()
                if clarified_topic != self.config['topic']:
                    print(f"✅ Topic enhanced with clarifications")
                    self.session_data['original_topic'] = self.config['topic']
                    self.session_data['clarified_topic'] = clarified_topic
            
            # Execute iterations with clarified topic
            ruleset_sequence = self.config.get('ruleset_sequence', ['default'])
            max_iterations = self.config.get('experiment', {}).get('max_iterations', len(ruleset_sequence))
            
            previous_context = {}
            
            for iteration_num in range(min(len(ruleset_sequence), max_iterations)):
                try:
                    iteration_result = await self._execute_iteration(
                        iteration_num + 1,
                        ruleset_sequence[iteration_num],
                        previous_context,
                        clarified_topic
                    )
                    
                    self.session_data['iterations'].append(iteration_result)
                    
                    # Prepare context for next iteration
                    if iteration_num < max_iterations - 1:
                        previous_context = self.context_processor.smart_truncate_all(
                            iteration_result.responses
                        )
                    
                except Exception as e:
                    print(f"❌ Iteration {iteration_num + 1} failed: {e}")
                    if not self.ai_orchestrator.graceful_mode:
                        raise
                    else:
                        print("🔄 Graceful mode: Continuing session...")
            
            # Generate final synthesis if enabled
            final_synthesis = None
            if self.config.get('meta_analysis', {}).get('final_synthesis', True):
                final_synthesis = await self._generate_final_synthesis(clarified_topic)
            
            # Generate final report
            self.session_data['metadata']['end_time'] = datetime.now()
            self.session_data['metadata']['duration'] = str(
                self.session_data['metadata']['end_time'] - self.session_data['metadata']['start_time']
            )
            
            report = self.report_generator.generate_final_report(self.session_data, final_synthesis)
            
            # Save log if configured
            if self.config.get('output', {}).get('save_conversation_log', False):
                self._save_session_log(report)
            
            print(f"✅ CORTEX session completed successfully!")
            print(f"💰 Total cost: ${report.total_cost:.4f}")
            
            return report
            
        except Exception as e:
            self.session_data['metadata']['error'] = str(e)
            self.session_data['metadata']['end_time'] = datetime.now()
            raise CortexSessionError(f"Session execution failed: {e}") from e
    
    async def _execute_iteration(self, iteration_num: int, ruleset_name: str, 
                                previous_context: Dict[str, str], topic: str) -> IterationRound:
        """Execute a single iteration with comprehensive error handling"""
        print(f"\n🔄 Iteration {iteration_num}: {ruleset_name}")
        
        try:
            # Get ruleset configuration
            ruleset = self.config.get('rulesets', {}).get(
                ruleset_name, 
                {'description': 'Default collaborative exploration'}
            )
            
            # Execute AI queries in parallel
            responses = await self.ai_orchestrator.query_all_ais(
                ai_team=self.session_data['ai_team'],
                topic=topic,
                iteration=iteration_num,
                previous_context=previous_context,
                ruleset=ruleset
            )
            
            if not responses:
                raise CortexSessionError(f"No successful responses in iteration {iteration_num}")
            
            # Calculate iteration metrics
            successful_ais = [r.ai_name for r in responses if r.success]
            failed_ais = [r.ai_name for r in responses if not r.success]
            total_cost = sum(r.real_cost for r in responses if r.success)
            
            # Perform meta-analysis if enabled
            meta_insights = None
            meta_analyzer = None
            
            if self.config.get('meta_analysis', {}).get('enabled', True):
                meta_result = await self._perform_meta_analysis(responses, iteration_num)
                if meta_result:
                    meta_insights = meta_result.get('content')
                    meta_analyzer = meta_result.get('analyzer')
                    self.session_data['meta_analyses'].append(meta_result)
            
            iteration_round = IterationRound(
                round_number=iteration_num,
                topic=topic,
                ruleset_name=ruleset_name,
                responses=responses,
                successful_ais=successful_ais,
                failed_ais=failed_ais,
                total_cost=total_cost,
                context_used=previous_context.copy(),
                timestamp=datetime.now(),
                meta_insights=meta_insights,
                meta_analyzer=meta_analyzer
            )
            
            print(f"✅ Iteration {iteration_num} completed")
            print(f"   Successful AIs: {len(successful_ais)}")
            print(f"   Cost: ${total_cost:.4f}")
            
            return iteration_round
            
        except Exception as e:
            raise CortexSessionError(f"Iteration {iteration_num} execution failed: {e}") from e
    
    async def _perform_meta_analysis(self, responses: List[AIResponse], 
                                   iteration: int) -> Optional[Dict[str, Any]]:
        """Perform meta-analysis of iteration responses"""
        try:
            successful_responses = [r for r in responses if r.success]
            if not successful_responses:
                return None
            
            # Select fastest AI for meta-analysis
            fastest_ai = min(successful_responses, key=lambda r: r.response_time)
            
            # Build meta-analysis prompt
            word_limit = self.config.get('meta_analysis', {}).get('word_limit', 200)
            
            discussion_content = "\n\n".join([
                f"{r.ai_name}: {r.response[:500]}..." if len(r.response) > 500 else f"{r.ai_name}: {r.response}"
                for r in successful_responses
            ])
            
            meta_prompt = f"""Analysiere diese AI-zu-AI Diskussion in maximal {word_limit} Wörtern:

{discussion_content}

Fokus auf:
1. CONVERGENT_CONCEPTS: Welche Ideen entwickelten mehrere AIs?
2. CROSS_REFERENCES: Wer baute auf wem auf?
3. NOVEL_SYNTHESIS: Welche neuen Konzepte entstanden?
4. KEY_INSIGHTS: Wichtigste Erkenntnisse dieser Iteration?

Sei präzise und strukturiert."""
            
            meta_response = await self.ai_orchestrator.query_single_ai(
                ai_name=fastest_ai.ai_name,
                prompt=meta_prompt,
                max_tokens=word_limit * 2
            )
            
            if meta_response and meta_response.success:
                return {
                    'iteration': iteration,
                    'analyzer': fastest_ai.ai_name,
                    'content': meta_response.response,
                    'analysis_time': meta_response.response_time,
                    'timestamp': datetime.now()
                }
            
        except Exception as e:
            print(f"⚠️  Meta-analysis failed for iteration {iteration}: {e}")
        
        return None
    
    async def _generate_final_synthesis(self, topic: str) -> Optional[Dict[str, Any]]:
        """Generate comprehensive final synthesis of all iterations"""
        try:
            if not self.session_data['iterations']:
                return None
            
            # Select fastest AI from all iterations
            all_responses = []
            for iteration in self.session_data['iterations']:
                all_responses.extend([r for r in iteration.responses if r.success])
            
            if not all_responses:
                return None
            
            fastest_ai = min(all_responses, key=lambda r: r.response_time)
            
            # Build comprehensive synthesis prompt
            meta_analyses_text = "\n\n".join([
                f"Iteration {ma['iteration']}: {ma['content']}"
                for ma in self.session_data['meta_analyses']
            ])
            

# Ursprüngliches prompt, zu analytisch, nicht Userbezogen genug:
#            synthesis_prompt = f"""ORIGINAL QUESTION: {topic}
#META-ANALYSES FROM ALL ITERATIONS:
#{meta_analyses_text}
#Erstelle eine umfassende Final-Synthese:
#1. MAIN FINDINGS: Was sind die Hauptantworten auf die ursprüngliche Frage?
#2. CONVERGENT THEMES: Welche Themen zogen sich durch alle Iterationen?
#3. EVOLUTIONARY INSIGHTS: Wie entwickelten sich die Ideen über die Iterationen?
#4. PRACTICAL IMPLICATIONS: Was bedeutet das konkret für die Anwendung?
#5. UNEXPECTED DISCOVERIES: Welche überraschenden Erkenntnisse entstanden?
#Dies ist das HAUPTPRODUKT für den User - sei gründlich aber klar strukturiert."""

            synthesis_prompt = f"""ORIGINAL QUESTION: {topic}
META-ANALYSES FROM ALL ITERATIONS:
{meta_analyses_text}

Du bist eine hochspezialisierte KI, die eine Meta-Analyse einer Diskussionsrunde von verschiedenen AIs durchführt. Dein Ziel ist es, die wichtigsten Erkenntnisse aus den Beiträgen zu extrahieren und für einen Endanwender aufzubereiten, der konkrete Handlungsempfehlungen für das **angefragte Problem** sucht.

Analysiere die vorliegenden Diskussionsrunden und extrahiere die Informationen gemäß den folgenden Kategorien. Achte dabei besonders darauf, so **konkret, umsetzbar und handlungsorientiert** wie möglich zu formulieren, insbesondere bei den praktischen Implikationen:

1.  **MAIN_FINDINGS:**
    * Fasse die zentralen Aspekte des Problems, die identifizierten Ursachen und die wichtigsten Ausgangsbedingungen zusammen. Nenne hier, wo zutreffend, auch **konkrete fehlende Informationen, Einschränkungen oder kritische Faktoren**, die von den KIs als relevant für die Problemlösung identifiziert wurden.

2.  **CONVERGENT_THEMES:**
    * Identifiziere wiederkehrende Konzepte, übergeordnete Strategien, Paradigmenwechsel oder systemische Denkweisen, die von mehreren KIs geteilt wurden. **Gib hier, wo sinnvoll, Beispiele von übergreifenden Methoden oder Prinzipien** an, die als Konsens identifiziert wurden (z.B. 'ganzheitlicher Ansatz', 'datenbasierte Entscheidungen', 'iterative Verbesserung').

3.  **EVOLUTIONARY_INSIGHTS:**
    * Beschreibe, wie sich die Perspektiven, das Verständnis des Problems oder die vorgeschlagenen Lösungsansätze im Laufe der Diskussionsrunden entwickelt oder verfeinert haben (z.B. von initialen Reaktionen zu proaktiven Strategien, von Einzelmaßnahmen zu integrierten Lösungen). **Zeige exemplarisch auf, wie ein Lösungsansatz detaillierter oder differenzierter wurde.**

4.  **PRACTICAL_IMPLICATIONS:**
    * **Dies ist ein entscheidender Abschnitt für den Endanwender.** Liste hier **ALLE konkreten, umsetzbaren Empfehlungen, Maßnahmen und Schritte** auf, die von den KIs vorgeschlagen wurden.
    * **GLIEDERE DIESE PRAKTISCHEN TIPPS THEMATISCH ODER NACH PHASEN**, basierend auf der Art der Fragestellung (z.B. 'Vorbereitung', 'Implementierung', 'Monitoring', 'Ressourcen' oder nach relevanten Problem-Subkategorien).
        * Nenne **spezifische Methoden, Tools, Ressourcen oder exemplarische Vorgehensweisen**.
        * Gib, wo immer möglich, **konkrete Beispiele, Namen von Technologien, Materialien, Software oder relevante Kennzahlen** an.
        * Erläutere kurz den **Nutzen oder das Ziel** der jeweiligen Maßnahme.
    * **Formuliere diese Punkte als direkte, handlungsorientierte Empfehlungen für den Anwender.** Priorisiere dabei Maßnahmen, die von mehreren KIs bestätigt werden, als besonders effektiv oder innovativ hervorgehoben wurden, oder die eine hohe Relevanz für die schnelle Umsetzung haben.

5.  **UNEXPECTED_DISCOVERIES:**
    * Hebe unerwartete Einsichten, wichtige Hinweise, innovative Denkansätze oder Beobachtungen hervor, die während der Diskussion aufgetaucht sind und neue Perspektiven eröffnen oder wichtige Hinweise zur Fehlervermeidung sind.

6.  **KEY_INSIGHTS:**
    * Destilliere die wichtigsten übergreifenden Erkenntnisse, die für die erfolgreiche Bearbeitung des Problems von zentraler Bedeutung sind. **Integriere hier, wo passend, kurze Verweise auf die unmittelbar wichtigsten konkreten Maßnahmen oder Prinzipien.**

7.  **CORE_RECOMMENDATION:**
    * Formuliere eine prägnante, übergeordnete Kernempfehlung zur Lösung des Problems. **Versuche, hier die Essenz der wichtigsten praktischen Schritte oder Prinzipien kurz zu umreißen**, die den Weg zur Problemlösung weisen.

Ziel ist es, einen Bericht zu erstellen, der sowohl die tiefgreifende Analyse als auch eine klare, praktische und direkt anwendbare Anleitung für den Endanwender bietet. Denke daran, dass der Endanwender schnell und präzise umsetzbare Informationen benötigt, um das Problem effektiv anzugehen."""

            
            synthesis_response = await self.ai_orchestrator.query_single_ai(
                ai_name=fastest_ai.ai_name,
                prompt=synthesis_prompt,
                max_tokens=2000
            )
            
            if synthesis_response and synthesis_response.success:
                return {
                    'synthesizer': fastest_ai.ai_name,
                    'content': synthesis_response.response,
                    'synthesis_time': synthesis_response.response_time,
                    'meta_analyses_count': len(self.session_data['meta_analyses']),
                    'timestamp': datetime.now()
                }
                
        except Exception as e:
            print(f"⚠️  Final synthesis failed: {e}")
        
        return None
    
    async def _execute_clarification_round(self) -> str:
        """Execute Iteration 0: Clarification round with AI-consolidated questions"""
        try:
            original_topic = self.config['topic']
            clarification_config = self.config.get('clarification', {})
            max_questions = clarification_config.get('max_questions', 6)
            
            print(f"🎯 Clarification Round: Generating understanding questions...")
            
            # Step 1: Generate clarification questions from all AIs
            clarification_prompt = f"""TOPIC: {original_topic}

Du sollst als AI-Experte dieses Thema analysieren und präzise Verständnisfragen stellen.

AUFGABE: Stelle 2-3 spezifische Fragen, die für eine fundierte Beratung zu diesem Thema essentiell sind.

FOKUS auf:
- Konkrete Details, die für praktische Lösungen nötig sind
- Kontext und Rahmenbedingungen
- Ziele und Prioritäten
- Besonderheiten der Situation

FORMAT: Stelle jede Frage als nummerierte Liste.

Beispiel:
1. Welche Zielgruppe soll primär angesprochen werden?
2. Welches Budget steht zur Verfügung?
3. Was sind die größten aktuellen Herausforderungen?

Deine Fragen:"""
            
            # Get clarification questions from all AIs
            responses = await self.ai_orchestrator.query_all_ais(
                ai_team=self.session_data['ai_team'],
                topic=clarification_prompt,
                iteration=0,
                previous_context={},
                ruleset={'mode': 'clarification', 'focus': 'understanding_questions'}
            )
            
            successful_responses = [r for r in responses if r.success]
            if not successful_responses:
                print("⚠️  No successful clarification responses, using original topic")
                return original_topic
            
            # Step 2: AI consolidates all questions
            print(f"🤖 Consolidating questions from {len(successful_responses)} AIs...")
            consolidated_questions = await self._consolidate_clarification_questions(
                successful_responses, max_questions
            )
            
            if not consolidated_questions:
                print("⚠️  Question consolidation failed, using original topic")
                return original_topic
            
            # Step 3: Interactive or auto-answer mode
            interactive_mode = clarification_config.get('interactive_mode', True)
            
            if interactive_mode:
                answers = self._get_interactive_answers(consolidated_questions)
            else:
                print("🤖 Auto-generating example answers for demonstration...")
                answers = self._generate_example_answers(consolidated_questions, original_topic)
            
            # Step 4: Enhance topic with answers
            if answers:
                enhanced_topic = self._build_enhanced_topic(original_topic, consolidated_questions, answers)
                return enhanced_topic
            else:
                return original_topic
                
        except Exception as e:
            print(f"❌ Clarification round failed: {e}")
            return self.config['topic']
    
    async def _consolidate_clarification_questions(self, responses: List[AIResponse], 
                                                  max_questions: int) -> List[str]:
        """AI consolidates clarification questions into focused list"""
        try:
            # Select fastest AI for consolidation
            fastest_ai = min(responses, key=lambda r: r.response_time)
            
            # Collect all questions
            all_questions = []
            for response in responses:
                lines = response.response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        question = line.lstrip('0123456789.-• ').strip()
                        if question.endswith('?'):
                            all_questions.append(question)
            
            if not all_questions:
                return []
            
            # Build consolidation prompt
            questions_text = '\n'.join([f"- {q}" for q in all_questions])
            
            consolidation_prompt = f"""Du bekommst {len(all_questions)} Verständnisfragen von verschiedenen AI-Experten zu einem Beratungsthema.

ALLE FRAGEN:
{questions_text}

AUFGABE: Konsolidiere diese zu {max_questions} präzisen, nicht-redundanten Kernfragen.

REGELN:
1. Eliminiere Überschneidungen und Dopplungen
2. Priorisiere die wichtigsten Aspekte für fundierte Beratung
3. Formuliere klar und spezifisch
4. Decke verschiedene Dimensionen ab (Ziele, Kontext, Ressourcen, etc.)

FORMAT: Nummerierte Liste, jede Frage in einer Zeile.

KONSOLIDIERTE FRAGEN:"""
            
            consolidation_response = await self.ai_orchestrator.query_single_ai(
                ai_name=fastest_ai.ai_name,
                prompt=consolidation_prompt,
                max_tokens=800
            )
            
            if not consolidation_response or not consolidation_response.success:
                return []
            
            # Extract consolidated questions
            consolidated = []
            lines = consolidation_response.response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    question = line.lstrip('0123456789.-• ').strip()
                    if question.endswith('?') and len(question) > 10:
                        consolidated.append(question)
            
            return consolidated[:max_questions]
            
        except Exception as e:
            print(f"⚠️  Question consolidation failed: {e}")
            return []
    
    def _get_interactive_answers(self, questions: List[str]) -> Dict[str, str]:
        """Get interactive answers from user"""
        answers = {}
        
        print(f"\n📋 CLARIFICATION QUESTIONS")
        print("="*50)
        print("Bitte beantworte diese Fragen für eine bessere Analyse:\n")
        
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
            try:
                answer = input(f"   Antwort: ").strip()
                if answer:
                    answers[question] = answer
                else:
                    answers[question] = "Keine Angabe"
            except KeyboardInterrupt:
                print("\n⚠️  Interactive mode abgebrochen, nutze Beispiel-Antworten")
                return self._generate_example_answers(questions, "")
        
        print(f"\n✅ {len(answers)} Antworten erhalten")
        return answers
    
    def _generate_example_answers(self, questions: List[str], topic: str) -> Dict[str, str]:
        """Generate example answers for demonstration purposes"""
        answers = {}
        
        for question in questions:
            q_lower = question.lower()
            if 'zielgruppe' in q_lower or 'kunden' in q_lower:
                answers[question] = "Hauptsächlich Millennials und Gen-Z, 25-40 Jahre, mittleres bis gehobenes Einkommen"
            elif 'budget' in q_lower or 'kosten' in q_lower:
                answers[question] = "Budget von etwa 50.000€ für Modernisierung und Marketing"
            elif 'konkurrenz' in q_lower or 'wettbewerb' in q_lower:
                answers[question] = "Hauptkonkurrenten sind etablierte Salons, aber wenig innovative Ansätze in der Region"
            elif 'ziele' in q_lower or 'erreichen' in q_lower:
                answers[question] = "Umsatz um 30% steigern und als innovativster Salon der Region positioniert werden"
            elif 'standort' in q_lower or 'lage' in q_lower:
                answers[question] = "Zentrale Lage in der Innenstadt mit guter Laufkundschaft"
            else:
                answers[question] = "Detaillierte Informationen verfügbar, spezifische Anforderungen vorhanden"
        
        print(f"🤖 Generated {len(answers)} example answers for demonstration")
        return answers
    
    def _build_enhanced_topic(self, original_topic: str, questions: List[str], 
                             answers: Dict[str, str]) -> str:
        """Build enhanced topic with clarification answers"""
        try:
            enhanced_parts = [f"TOPIC: {original_topic}", "", "CONTEXT & DETAILS:"]
            
            for question, answer in answers.items():
                if answer and answer != "Keine Angabe":
                    enhanced_parts.append(f"- {question} → {answer}")
            
            enhanced_topic = '\n'.join(enhanced_parts)
            
            print(f"✨ Enhanced topic with {len(answers)} clarifications")
            return enhanced_topic
            
        except Exception as e:
            print(f"⚠️  Topic enhancement failed: {e}")
            return original_topic
    
    def _save_session_log(self, report: CortexReport) -> None:
        """Save session log to file with error handling"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cortex_session_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.report_generator.format_output(report, 'json'))
            
            print(f"💾 Session log saved: {filename}")
            
        except Exception as e:
            print(f"⚠️  Failed to save session log: {e}")


async def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python cortex_session.py <config_file.yaml>")
        return
    
    config_path = sys.argv[1]
    
    try:
        # Create and run session
        session = CortexSession(config_path)
        report = await session.run_session()
        
        # Output final report
        output_format = session.config.get('output', {}).get('format', 'markdown')
        
        file_extensions = {
            'markdown': 'md',
            'json': 'json', 
            'yaml': 'yaml',
            'pdf': 'pdf'
        }
        
        file_extension = file_extensions.get(output_format, 'txt')
        output_filename = f"cortex_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        
        print(f"\n📊 Generating {output_format.upper()} report...")
        
        # Enhanced PDF handling
        if output_format == 'pdf':
            if hasattr(session.report_generator, 'generate_pdf'):
                try:
                    print("🔄 Generating PDF with enhanced layout...")
                    success = session.report_generator.generate_pdf(report, output_filename)
                    if success:
                        print(f"✅ PDF report saved: {output_filename}")
                    else:
                        print("⚠️  PDF generation failed, creating Markdown instead")
                        output_filename = output_filename.replace('.pdf', '.md')
                        with open(output_filename, 'w', encoding='utf-8') as f:
                            f.write(session.report_generator._format_markdown(report))
                        print(f"💾 Markdown report saved: {output_filename}")
                except Exception as e:
                    print(f"❌ PDF generation error: {e}")
                    output_filename = output_filename.replace('.pdf', '.md')
                    with open(output_filename, 'w', encoding='utf-8') as f:
                        f.write(session.report_generator._format_markdown(report))
                    print(f"💾 Markdown report saved (PDF failed): {output_filename}")
            else:
                print("⚠️  PDF generation method not available")
                output_filename = output_filename.replace('.pdf', '.md')
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(session.report_generator._format_markdown(report))
                print(f"💾 Markdown report saved (no PDF support): {output_filename}")
        else:
            # Regular format handling
            with open(output_filename, 'w', encoding='utf-8') as f:
                formatted_output = session.report_generator.format_output(report, output_format)
                f.write(formatted_output)
            print(f"💾 Report saved: {output_filename}")
        
        # Quick summary
        print(f"\n🎯 SESSION SUMMARY")
        print(f"   Topic: {report.original_topic}")
        print(f"   AI Team: {', '.join(report.ai_team)}")
        print(f"   Iterations: {len(report.iterations)}")
        print(f"   Total Cost: ${report.total_cost:.4f}")
        print(f"   Insights Generated: {len(report.emergent_insights)}")
        
        if report.final_synthesis:
            print(f"   Final Synthesis: ✅ ({report.final_synthesis['synthesizer']})")
        
        print("\n🌊 CORTEX Flow session completed successfully!")
        
    except CortexSessionError as e:
        print(f"❌ CORTEX Session Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Session interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())