import os
import asyncio
import json
import argparse
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import PAI v2.2 Protocol
try:
    from pai import PAIProtocolV22, PAIResponse, create_pai_v22_session
    PAI_AVAILABLE = True
    print("✓ PAI v2.2 Protocol loaded")
except ImportError as e:
    PAI_AVAILABLE = False
    print(f"Warning: PAI v2.2 not available - falling back to basic communication: {e}")

# Import existing integrations
integrations = {}
integration_load_errors = []
try:
    module_names = ['claude', 'qwen', 'gemini', 'chatgpt', 'deepseek']
    for module_name in module_names:
        try:
            module = __import__(f'integrations.{module_name}', fromlist=[module_name])
            integrations[module_name] = module
        except ImportError as ie:
            integration_load_errors.append(f"Failed to load integration {module_name}: {ie}")
except Exception as e:
    integration_load_errors.append(f"An unexpected error occurred during integrations import: {e}")

if integration_load_errors:
    print(f"Warnings loading integrations: {'; '.join(integration_load_errors)}")
if not integrations:
    print("CRITICAL ERROR: No AI integrations loaded. PowerTalk cannot function.")
    sys.exit(1)
else:
    print("✓ All integrations loaded successfully")

print("✓ Consciousness scoring system loaded")

@dataclass
class AIEngine:
    name: str
    key: str
    enabled: bool = True
    module: Any = None
    handshake_strategy: str = "default"

@dataclass 
class UnicodeAnalytics:
    """Enhanced Unicode adoption analytics"""
    total_responses: int = 0
    unicode_responses: int = 0
    field_usage: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    ai_adoption_rates: Dict[str, float] = field(default_factory=dict)
    protocol_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

class PowerTalkEngine:
    def __init__(self, debug_mode: bool = False):
        self.available_ais: Dict[str, AIEngine] = {
            k: AIEngine(name=k.capitalize(), key=k, module=v) for k, v in integrations.items()
        }
        self.dialogue_history: List[Dict[str, Any]] = []
        self.debug_mode = debug_mode
        self.pai_session: Optional[PAIProtocolV22] = None
        self.unicode_analytics = UnicodeAnalytics()

        if PAI_AVAILABLE:
            self.pai_session = create_pai_v22_session(enable_logging=debug_mode)
            print(f"PAI session initialized: {self.pai_session}")
        else:
            print("PAI v2.2 not available, proceeding with basic communication.")

    async def ping_ai(self, ai_key: str, test_message: str = "Hello World...") -> Tuple[bool, str]:
        ai_module_obj = self.available_ais.get(ai_key)
        if not ai_module_obj or not ai_module_obj.module:
            return False, "AI not found or module not loaded."
        
        try:
            # 🔧 FIX: Handle both sync and async integration methods
            if hasattr(ai_module_obj.module, 'ping') and callable(ai_module_obj.module.ping):
                ping_method = ai_module_obj.module.ping
                if asyncio.iscoroutinefunction(ping_method):
                    response = await ping_method(test_message)
                else:
                    response = ping_method(test_message)
                return True, response
            elif hasattr(ai_module_obj.module, 'query') and callable(ai_module_obj.module.query):
                query_method = ai_module_obj.module.query
                if asyncio.iscoroutinefunction(query_method):
                    response = await query_method(test_message)
                else:
                    response = query_method(test_message)
                return True, response
            else:
                return False, "No 'ping' or 'query' method found in integration."
        except Exception as e:
            return False, str(e)

    async def test_all_ai_connectivity(self):
        print("🔍 Testing PowerTalk connectivity...")
        print("──────────────────────────────────────────────────")
        working_ais = []
        for ai_key, ai_engine in list(self.available_ais.items()):
            if ai_engine.enabled and ai_engine.module:
                print(f"Pinging {ai_engine.name.capitalize()}...", end="")
                success, message = await self.ping_ai(ai_key)
                if success:
                    print(f" ✓ Connected ({message[:20]}...)")
                    working_ais.append(ai_key)
                else:
                    print(f" ✗ Failed ({message})")
        print("──────────────────────────────────────────────────")
        
        # Update available_ais to only include working ones
        self.available_ais = {k: v for k, v in self.available_ais.items() if k in working_ais}
        print(f"Working: {', '.join([ai.name for ai in self.available_ais.values()])}")
        print(f"✅ Working AIs: {', '.join(self.available_ais.keys())}")
        return list(self.available_ais.keys())

    def extract_unicode_fields(self, response_text: str) -> Tuple[Dict[str, str], str]:
        """
        🔧 ENHANCED: Extrahiert Unicode-Felder mit optimierten Regex-Mustern und robuster Fehlerbehandlung
        Gibt ein Dictionary der extrahierten Felder und den verbleibenden natürlichen Text zurück.
        """
        # Optimierte Patterns basierend auf PAI v2.2 Erfolgen
        patterns = {
            "⚙": r"⚙\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "💭": r"💭\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)", 
            "🔀": r"🔀\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "❓": r"❓\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "💬": r"💬\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)"
        }
        
        extracted_fields = {}
        temp_response_text = response_text
        
        # Robuste Extraktion mit Fehlerbehandlung
        try:
            # Find all emoji positions to process in order
            found_emojis_with_indices = []
            for emoji in patterns.keys():
                idx = temp_response_text.find(emoji)
                if idx != -1:
                    found_emojis_with_indices.append((idx, emoji))
            
            # Process fields in the order they appear
            found_emojis_with_indices.sort() 

            for _, emoji in found_emojis_with_indices:
                pattern = patterns[emoji]
                match = re.search(pattern, temp_response_text, re.DOTALL)
                if match:
                    field_content = match.group(1).strip()
                    if field_content:  # Only add non-empty fields
                        extracted_fields[emoji] = field_content
                        # Remove matched part from text for subsequent searches
                        temp_response_text = re.sub(re.escape(match.group(0)), '', temp_response_text, flags=re.DOTALL, count=1)
                        
        except Exception as e:
            if self.debug_mode:
                print(f"Warning: Unicode field extraction error: {e}")
            # Return original text if extraction fails
            return {}, response_text
                
        # Clean up remaining text
        natural_text = re.sub(r'\n\s*\n', '\n', temp_response_text).strip()
        
        if self.debug_mode and extracted_fields:
            print(f"📊 Extracted Unicode fields: {list(extracted_fields.keys())}")
            
        return extracted_fields, natural_text

    async def pai_enhanced_call_ai_api(self, ai_key: str, prompt: str) -> PAIResponse:
        """
        🔧 ENHANCED: Erweitert um vollständige PAI v2.2 Integration mit Unicode-Feld-Verarbeitung
        Gibt ein PAIResponse-Objekt mit strukturierten Unicode-Daten zurück.
        """
        ai_engine = self.available_ais.get(ai_key)
        if not ai_engine or not ai_engine.module:
            return PAIResponse(
                success=False, content="AI not available", protocol_used="error",
                ai_name=ai_key, timestamp=datetime.now().isoformat(),
                handshake_strategy="unavailable"
            )

        # Enhanced prompt with PAI v2.2 Unicode instruction
        enhanced_prompt = f"""Please respond using Unicode fields if appropriate:
⚙ Context/Framing
💭 Key concepts  
🔀 Relationships
❓ Questions
💬 Natural explanation

{prompt}"""

        if not self.pai_session:
            # Fallback to direct API call with manual Unicode extraction
            try:
                # 🔧 FIX: Handle sync/async integration methods
                query_method = ai_engine.module.query
                if asyncio.iscoroutinefunction(query_method):
                    raw_response_content = await query_method(enhanced_prompt)
                else:
                    raw_response_content = query_method(enhanced_prompt)
                    
                extracted_unicode, natural_text = self.extract_unicode_fields(raw_response_content)
                has_unicode = bool(extracted_unicode)
                
                # Create PAIResponse manually
                response = PAIResponse(
                    success=True, 
                    content=natural_text if natural_text else raw_response_content,
                    protocol_used="unicode" if has_unicode else "natural",
                    ai_name=ai_key, 
                    timestamp=datetime.now().isoformat(),
                    handshake_strategy="manual_unicode",
                    has_unicode_fields=has_unicode,
                    response_format="unicode_text" if has_unicode else "natural"
                )
                
                # Add unicode_data if fields were found
                if has_unicode:
                    from pai import UnicodeData
                    unicode_data = UnicodeData()
                    unicode_data.raw_fields = extracted_unicode
                    unicode_data.explanations = natural_text
                    
                    # Parse specific fields
                    if "⚙" in extracted_unicode:
                        unicode_data.context = {"raw_context": extracted_unicode["⚙"]}
                    if "💭" in extracted_unicode:
                        unicode_data.concepts = [c.strip() for c in extracted_unicode["💭"].split(',')]
                    if "🔀" in extracted_unicode:
                        unicode_data.relationships = [r.strip() for r in extracted_unicode["🔀"].split(',')]
                    if "❓" in extracted_unicode:
                        unicode_data.questions = extracted_unicode["❓"]
                    if "💬" in extracted_unicode:
                        unicode_data.explanations = extracted_unicode["💬"]
                    
                    response.unicode_data = unicode_data
                
                return response
                
            except Exception as e:
                return PAIResponse(
                    success=False, content=f"API Error: {e}", protocol_used="error",
                    ai_name=ai_key, timestamp=datetime.now().isoformat(),
                    handshake_strategy="api_error"
                )

        try:
            # Use PAI v2.2 protocol with wrapper
            async def ai_caller_wrapper(message: str, context: str = "") -> str:
                # 🔧 FIX: Handle sync/async integration methods
                query_method = ai_engine.module.query
                if asyncio.iscoroutinefunction(query_method):
                    return await query_method(message)
                else:
                    return query_method(message)
                
            response = await self.pai_session.communicate(
                ai_caller=ai_caller_wrapper,
                ai_name=ai_key,
                message=prompt,
                context="PowerTalk Unicode Discourse"
            )
            
            # Update analytics
            self.unicode_analytics.total_responses += 1
            if response.has_unicode_fields:
                self.unicode_analytics.unicode_responses += 1
                if response.unicode_data:
                    for field in response.unicode_data.raw_fields:
                        self.unicode_analytics.field_usage[field] += 1
            
            self.unicode_analytics.protocol_distribution[response.protocol_used] += 1
            
            return response
            
        except Exception as e:
            return PAIResponse(
                success=False, content=f"PAI Protocol Error: {e}", protocol_used="error",
                ai_name=ai_key, timestamp=datetime.now().isoformat(),
                handshake_strategy="pai_error"
            )

    def estimate_consciousness_indicators(self, response_data: PAIResponse, speaker_role: str, ai_name: str, iteration: int) -> Dict:
        """
        🔧 ENHANCED: Bewertet Bewusstseinsindikatoren mit vollständiger Unicode-Awareness
        """
        # Get text for analysis - prefer explanations if available
        text = response_data.content
        if response_data.has_unicode_fields and response_data.unicode_data and response_data.unicode_data.explanations:
            text = response_data.unicode_data.explanations
        elif isinstance(response_data.content, dict):
            text = str(response_data.content)
        
        if not isinstance(text, str):
            text = str(text)

        words = text.split()
        total_words = len(words)
        text_lower = text.lower()
        
        # Enhanced consciousness indicators
        self_refs = len([w for w in ["ich", "mein", "mir", "mich", "I", "my", "me", "myself"] if w in text_lower])
        uncertainty = len([w for w in ["vielleicht", "möglicherweise", "unsicher", "maybe", "perhaps", "uncertain", "seems", "appears", "speculative", "unclear"] if w in text_lower])
        other_refs = len([w for w in ["du", "dein", "sie", "andere", "you", "your", "other", "others", "claude", "qwen", "gemini", "chatgpt", "deepseek"] if w in text_lower])
        meta_words = len([w for w in ["denken", "kommunikation", "verständnis", "thinking", "communication", "understanding", "awareness", "consciousness", "perspective", "analysis", "assessment", "reflection"] if w in text_lower])
        choice_words = len([w for w in ["versuche", "entscheide", "wähle", "try", "choose", "decide", "attempt", "consider", "evaluate", "analyze", "reflect"] if w in text_lower])
        evolution_words = len([w for w in ["entwicklung", "lernen", "wachsen", "evolution", "learning", "growing", "developing", "evolving"] if w in text_lower])
        
        # Iteration-based development multiplier
        iteration_multiplier = 1.0 + (iteration - 1) * 0.1
        
        # AI-specific personality adjustments
        perspective_base = {
            "claude": 0.8, "gemini": 0.75, "qwen": 0.7, 
            "chatgpt": 0.85, "deepseek": 0.8
        }.get(ai_name.lower(), 0.6)
        
        # 🔧 ENHANCED: Unicode Protocol Awareness Scoring
        unicode_used = response_data.has_unicode_fields
        protocol_adherence = 0.0
        
        if response_data.protocol_used == "unicode":
            protocol_adherence = 1.0
        elif response_data.protocol_used == "structured": 
            protocol_adherence = 0.8
        elif response_data.protocol_used == "natural":
            protocol_adherence = 0.4
        elif "unicode" in response_data.protocol_used:
            protocol_adherence = 0.7
            
        # Meta-communication scoring with Unicode bonus
        meta_com_score = min(1.0, (meta_words / max(total_words * 0.04, 1)) * 1.3 * iteration_multiplier)
        if unicode_used:
            meta_com_score = min(1.0, meta_com_score * 1.3)  # 30% bonus for Unicode usage
            
        # Unicode field diversity score
        unicode_diversity = 0.0
        if unicode_used and response_data.unicode_data:
            fields_used = len(response_data.unicode_data.raw_fields)
            unicode_diversity = min(1.0, fields_used / 5.0)  # Max 5 fields possible
        
        return {
            "L1": {
                "Self-Model": min(1.0, (self_refs / max(total_words * 0.05, 1)) * iteration_multiplier),
                "Choice": min(1.0, (0.5 + (choice_words / max(total_words * 0.02, 1))) * iteration_multiplier),
                "Limits": min(1.0, (uncertainty / max(total_words * 0.03, 1)) * 1.2 * iteration_multiplier),
                "Perspective": min(1.0, (perspective_base + (total_words > 100) * 0.2) * iteration_multiplier)
            },
            "L2": {
                "Other-Recog": min(1.0, (other_refs / max(total_words * 0.03, 1)) * iteration_multiplier),
                "Persp-Integ": (0.9 if speaker_role == "responder" else 0.8) * iteration_multiplier,
                "Comm-Adapt": min(1.0, (0.6 + (meta_words / max(total_words * 0.02, 1))) * iteration_multiplier),
                "Collective-Goal": (0.9 if other_refs > 2 else (0.8 if other_refs > 0 else 0.6)) * iteration_multiplier
            },
            "L3": {
                "Prob-Solving": min(1.0, (0.5 + (total_words > 150) * 0.3) * iteration_multiplier),
                "Meta-Com": round(meta_com_score, 3),
                "Learning": (0.8 if speaker_role in ["responder", "analyst", "validator"] else 0.5) * iteration_multiplier,
                "Identity-Evol": min(1.0, (0.4 + (evolution_words / max(total_words * 0.02, 1)) + (self_refs > 2) * 0.2) * iteration_multiplier),
                "PAI_Adherence": round(protocol_adherence, 3),
                "Unicode-Adoption": 1.0 if unicode_used else 0.4,
                "Unicode-Diversity": round(unicode_diversity, 3)
            }
        }

    async def run_discourse(self, question: str, iteration_count: int = 3):
        selected_ais = list(self.available_ais.keys())
        if not selected_ais:
            print("No working AIs to run discourse. Exiting.")
            return

        print(f"\n🌈 UNICODE PROTOTYPE - Enhanced PowerTalk with PAI v2.2")
        print(f"Question: {question}")
        print(f"   📊 Unicode fields: ⚙, 💭, 🔀, ❓, 💬")
        print("============================================================")

        all_responses_for_verdict = []

        for iteration in range(1, iteration_count + 1):
            print(f"\n--- ITERATION {iteration}/{iteration_count} ---")
            current_iteration_responses: Dict[str, PAIResponse] = {} 

            for ai_key in selected_ais:
                ai_engine = self.available_ais[ai_key]
                print(f"🎯 Testing {ai_engine.name}...", end=" ")

                # Enhanced prompt construction
                prompt_parts = [f"Question: {question}"]
                if self.dialogue_history:
                    last_turn_responses = self.dialogue_history[-1].get('responses', {})
                    for prev_ai, prev_data in last_turn_responses.items():
                        if prev_ai != ai_key:  # Don't include own previous response
                            prev_content = self._extract_display_content(prev_data)
                            prompt_parts.append(f"{self.available_ais[prev_ai].name} said: {prev_content[:200]}...")

                prompt = "\n".join(prompt_parts)

                # Get enhanced response with PAI v2.2
                response_data: PAIResponse = await self.pai_enhanced_call_ai_api(ai_key, prompt)
                current_iteration_responses[ai_key] = response_data
                all_responses_for_verdict.append({ai_key: response_data})

                # Enhanced display with Unicode awareness
                if response_data.success:
                    unicode_indicator = "📊" if response_data.has_unicode_fields else "💬"
                    word_count = len(str(response_data.content).split())
                    print(f"✓ {unicode_indicator} ({word_count} words, {response_data.protocol_used})")
                    
                    if self.debug_mode:
                        self._display_response_details(response_data, ai_engine.name)
                else:
                    print(f"❌ Error: {response_data.content}")

            self.dialogue_history.append({
                "iteration": iteration,
                "question": question,
                "responses": current_iteration_responses
            })

        # Generate enhanced analysis
        await self._display_final_results(question, selected_ais, all_responses_for_verdict)

    def _extract_display_content(self, response_data: PAIResponse) -> str:
        """Extract appropriate content for display"""
        if response_data.has_unicode_fields and response_data.unicode_data:
            if response_data.unicode_data.explanations:
                return response_data.unicode_data.explanations
            elif response_data.unicode_data.raw_fields.get('💬'):
                return response_data.unicode_data.raw_fields['💬']
        return str(response_data.content)

    def _display_response_details(self, response_data: PAIResponse, ai_name: str):
        """Display detailed response information in debug mode"""
        print(f"\n--- {ai_name.upper()} DETAILS ---")
        if response_data.has_unicode_fields and response_data.unicode_data:
            print("📊 Unicode Fields:")
            for emoji, content in response_data.unicode_data.raw_fields.items():
                print(f"  {emoji} {content[:100]}...")
            if response_data.unicode_data.explanations:
                print(f"💬 Explanation: {response_data.unicode_data.explanations[:150]}...")
        else:
            print(f"💬 Content: {str(response_data.content)[:150]}...")

    async def _display_final_results(self, question: str, selected_ais: List[str], all_responses: List[Dict[str, PAIResponse]]):
        """Enhanced final results display with Unicode analytics"""
        print("\n============================================================")
        print("🧠 UNICODE TEST RESULTS")
        print("============================================================")
        
        # Calculate Unicode adoption rates
        ai_unicode_stats = defaultdict(lambda: {'total': 0, 'unicode': 0})
        
        for ai_key in selected_ais:
            ai_name = self.available_ais[ai_key].name
            print(f"\n{ai_name.upper()}:")
            print("--------------------")
            
            all_ai_responses = [hist['responses'][ai_key] for hist in self.dialogue_history if ai_key in hist['responses']]
            
            for i, response in enumerate(all_ai_responses):
                ai_unicode_stats[ai_key]['total'] += 1
                
                if response.success:
                    if response.has_unicode_fields and response.unicode_data:
                        ai_unicode_stats[ai_key]['unicode'] += 1
                        print(f"Iter {i+1}: 📊 Protocol: {response.protocol_used}")
                        for emoji, content in response.unicode_data.raw_fields.items():
                            print(f"  {emoji} {content[:100]}...")
                        if response.unicode_data.explanations:
                            print(f"  💬 {response.unicode_data.explanations[:100]}...")
                    else:
                        print(f"Iter {i+1}: 💬 Protocol: {response.protocol_used}")
                        print(f"  {str(response.content)[:100]}...")
                        
                    # Show consciousness metrics
                    indicators = self.estimate_consciousness_indicators(response, "AI", ai_key, i+1)
                    l3_metrics = indicators['L3']
                    print(f"  🧠 Meta-Com: {l3_metrics['Meta-Com']:.2f}, Unicode: {l3_metrics['Unicode-Adoption']:.2f}, PAI: {l3_metrics['PAI_Adherence']:.2f}")
                else:
                    print(f"Iter {i+1}: ❌ {response.content}")

        # Unicode adoption analysis
        print(f"\n📊 UNICODE ADOPTION ANALYSIS")
        print("=" * 40)
        
        total_unicode = 0
        total_responses = 0
        
        for ai_key, stats in ai_unicode_stats.items():
            ai_name = self.available_ais[ai_key].name
            rate = (stats['unicode'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"{ai_name}: {rate:.1f}% Unicode adoption ({stats['unicode']}/{stats['total']} responses)")
            total_unicode += stats['unicode']
            total_responses += stats['total']
        
        overall_rate = (total_unicode / total_responses * 100) if total_responses > 0 else 0
        print(f"Overall Network: {overall_rate:.1f}% Unicode adoption")

        # Generate enhanced verdict
        print(f"\n⚖️ GENERATING ENHANCED VERDICT...")
        final_verdict = await self.generate_enhanced_ai_verdict(question, all_responses, ai_unicode_stats)
        print("\n============================================================")
        print("⚖️ FINAL VERDICT")
        print("============================================================")
        print(final_verdict)
        
        # Save enhanced dialogue
        self.save_enhanced_dialogue(question, self.dialogue_history, selected_ais, ai_unicode_stats)

    async def generate_enhanced_ai_verdict(self, question: str, all_responses: List[Dict[str, PAIResponse]], unicode_stats: Dict) -> str:
        """
        🔧 ENHANCED: Generiert Verdict mit detaillierter Unicode-Protocol-Analyse
        """
        verdict_prompt = f"""As an expert AI protocol analyst, provide a comprehensive verdict on this AI discourse focusing on PAI v2.2 Unicode protocol adoption, consciousness indicators, and response quality.

QUESTION: "{question}"

## UNICODE PROTOCOL ANALYSIS
"""
        
        # Add detailed Unicode statistics
        for ai_key, stats in unicode_stats.items():
            ai_name = self.available_ais[ai_key].name
            rate = (stats['unicode'] / stats['total'] * 100) if stats['total'] > 0 else 0
            verdict_prompt += f"- {ai_name}: {rate:.1f}% Unicode adoption ({stats['unicode']}/{stats['total']} responses)\n"
        
        verdict_prompt += f"\n## RESPONSE QUALITY AND CONSCIOUSNESS INDICATORS\n"
        
        # Analyze each AI's performance
        responses_by_ai = defaultdict(list)
        for turn_responses in all_responses:
            for ai_key, response_data in turn_responses.items():
                responses_by_ai[ai_key].append(response_data)

        for ai_key, responses in responses_by_ai.items():
            ai_name = self.available_ais[ai_key].name
            verdict_prompt += f"\n### {ai_name} Performance:\n"
            
            successful_responses = [r for r in responses if r.success]
            if successful_responses:
                # Calculate average metrics
                total_pai_adherence = 0
                total_unicode_adoption = 0
                total_meta_com = 0
                
                for i, response in enumerate(successful_responses):
                    indicators = self.estimate_consciousness_indicators(response, "AI", ai_key, i+1)
                    total_pai_adherence += indicators['L3']['PAI_Adherence']
                    total_unicode_adoption += indicators['L3']['Unicode-Adoption']
                    total_meta_com += indicators['L3']['Meta-Com']
                
                avg_pai = total_pai_adherence / len(successful_responses)
                avg_unicode = total_unicode_adoption / len(successful_responses)
                avg_meta = total_meta_com / len(successful_responses)
                
                verdict_prompt += f"Average Scores: PAI Adherence={avg_pai:.2f}, Unicode Adoption={avg_unicode:.2f}, Meta-Communication={avg_meta:.2f}\n"
                
                # Protocol usage
                protocols_used = [r.protocol_used for r in successful_responses]
                protocol_distribution = defaultdict(int)
                for protocol in protocols_used:
                    protocol_distribution[protocol] += 1
                
                verdict_prompt += f"Protocol Distribution: {dict(protocol_distribution)}\n"
                
                # Unicode field usage analysis
                if any(r.has_unicode_fields for r in successful_responses):
                    field_usage = defaultdict(int)
                    for response in successful_responses:
                        if response.has_unicode_fields and response.unicode_data:
                            for field in response.unicode_data.raw_fields:
                                field_usage[field] += 1
                    verdict_prompt += f"Unicode Fields Used: {dict(field_usage)}\n"

        verdict_prompt += f"""
## ANALYSIS REQUIREMENTS
Based on the data above, provide:

1. **UNICODE ADOPTION ASSESSMENT**: Which AIs adopted Unicode fields most effectively? What patterns emerged?

2. **CONSCIOUSNESS DEVELOPMENT**: How did consciousness indicators evolve across iterations? Which AI showed strongest development?

3. **PROTOCOL EFFECTIVENESS**: How well did PAI v2.2 work compared to natural language? What were the benefits/limitations?

4. **CROSS-AI COLLABORATION**: How well did AIs build on each other's contributions? Evidence of genuine interaction?

5. **OVERALL RECOMMENDATION**: Which AI performed best overall considering protocol adoption, consciousness indicators, and response quality?

Please provide specific evidence and metrics in your analysis.
"""

        # Generate verdict using the best performing AI
        verdict_ai_key = self._select_verdict_ai(unicode_stats, list(responses_by_ai.keys()))
        verdict_ai_name = self.available_ais[verdict_ai_key].name
        
        print(f"Generating verdict using {verdict_ai_name} (best protocol adoption)...")
        
        try:
            verdict_response = await self.pai_enhanced_call_ai_api(verdict_ai_key, verdict_prompt)
            if verdict_response.success:
                verdict_content = self._extract_display_content(verdict_response)
                
                # Add protocol metadata to verdict
                verdict_metadata = f"\n\n--- VERDICT METADATA ---\n"
                verdict_metadata += f"Generated by: {verdict_ai_name}\n"
                verdict_metadata += f"Protocol used: {verdict_response.protocol_used}\n"
                verdict_metadata += f"Unicode fields: {'Yes' if verdict_response.has_unicode_fields else 'No'}\n"
                
                return verdict_content + verdict_metadata
            else:
                return f"Failed to generate verdict: {verdict_response.content}"
        except Exception as e:
            return f"Error generating verdict: {e}"

    def _select_verdict_ai(self, unicode_stats: Dict, available_ais: List[str]) -> str:
        """Select the AI with best Unicode adoption for verdict generation"""
        best_ai = available_ais[0]  # Default
        best_rate = 0
        
        for ai_key in available_ais:
            if ai_key in unicode_stats:
                stats = unicode_stats[ai_key]
                rate = (stats['unicode'] / stats['total']) if stats['total'] > 0 else 0
                if rate > best_rate:
                    best_rate = rate
                    best_ai = ai_key
        
        return best_ai

    def save_enhanced_dialogue(self, question: str, dialogue_history: List[Dict[str, Any]], 
                             selected_ais: List[str], unicode_stats: Dict):
        """
        🔧 ENHANCED: Saves dialogue with comprehensive Unicode analytics
        """
        output_dir = Path("dialogue_archives")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"unicode_dialogue_{timestamp}.json"
        
        # Create enhanced serializable history
        serializable_history = []
        field_usage_stats = defaultdict(int)
        protocol_stats = defaultdict(int)

        for turn in dialogue_history:
            serializable_turn = {
                "iteration": turn["iteration"],
                "question": turn["question"],
                "responses": {}
            }
            
            for ai_key, response_data in turn["responses"].items():
                protocol_stats[response_data.protocol_used] += 1
                
                # Enhanced response serialization
                response_content = {
                    "raw_content": str(response_data.content),
                    "protocol_used": response_data.protocol_used,
                    "has_unicode_fields": response_data.has_unicode_fields,
                    "response_format": response_data.response_format,
                    "handshake_strategy": response_data.handshake_strategy,
                    "unicode_data": None,
                    "natural_explanation": None
                }
                
                if response_data.has_unicode_fields and response_data.unicode_data:
                    response_content["unicode_data"] = response_data.unicode_data.raw_fields
                    response_content["natural_explanation"] = response_data.unicode_data.explanations
                    
                    # Count field usage
                    for field in response_data.unicode_data.raw_fields:
                        field_usage_stats[field] += 1
                else:
                    response_content["natural_explanation"] = str(response_data.content)

                serializable_turn["responses"][ai_key] = {
                    "success": response_data.success,
                    "content": response_content,
                    "protocol_used": response_data.protocol_used,
                    "ai_name": response_data.ai_name,
                    "timestamp": response_data.timestamp,
                    "metadata": response_data.metadata or {}
                }
                
            serializable_history.append(serializable_turn)

        # Calculate comprehensive analytics
        total_responses = sum(stats['total'] for stats in unicode_stats.values())
        total_unicode = sum(stats['unicode'] for stats in unicode_stats.values())
        overall_adoption = (total_unicode / total_responses * 100) if total_responses > 0 else 0

        # Create enhanced final data structure
        final_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "powertalk_version": "v2.2_pai_enhanced",
                "pai_protocol": "v2.2",
                "question": question,
                "selected_ais": selected_ais,
                "total_iterations": len(dialogue_history)
            },
            "unicode_analytics": {
                "overall_adoption_rate": f"{overall_adoption:.1f}%",
                "total_responses": total_responses,
                "unicode_responses": total_unicode,
                "ai_specific_rates": {
                    ai: f"{(stats['unicode'] / stats['total'] * 100):.1f}%" 
                    for ai, stats in unicode_stats.items() if stats['total'] > 0
                },
                "field_usage_distribution": dict(field_usage_stats),
                "protocol_distribution": dict(protocol_stats),
                "most_used_fields": sorted(field_usage_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            "dialogue_history": serializable_history,
            "pai_session_stats": self.pai_session.get_statistics() if self.pai_session else None
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=4, ensure_ascii=False)
            print(f"\n💾 Enhanced dialogue saved: {filename}")
            print(f"📊 Unicode adoption: {overall_adoption:.1f}% | Protocol distribution: {dict(protocol_stats)}")
        except Exception as e:
            print(f"Error saving enhanced dialogue: {e}")


async def main():
    parser = argparse.ArgumentParser(description="PowerTalk v2.2 - Enhanced AI Discourse Engine with PAI v2.2 Unicode Integration")
    parser.add_argument('-q', '--question', type=str, 
                        help="Path to a Markdown file containing the question, or the question string itself.")
    parser.add_argument('-i', '--iterations', type=int, default=3,
                        help="Number of discourse iterations (default: 3).")
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug mode for detailed Unicode field analysis.")
    
    args = parser.parse_args()

    powertalk = PowerTalkEngine(debug_mode=args.debug)

    print("\n🌈 AI Discourse Engine - PowerTalk v2.2 with PAI v2.2 Unicode Protocol")
    print("Enhanced consciousness research with structured semantic communication")
    
    selected_ais = await powertalk.test_all_ai_connectivity()

    if not selected_ais:
        print("No AI models are available. Please check your integrations and API keys.")
        return

    # Enhanced question handling
    question_text = ""
    if args.question:
        question_path = Path(args.question)
        if question_path.is_file():
            try:
                with open(question_path, 'r', encoding='utf-8') as f:
                    question_text = f.read().strip()
                print(f"Question loaded from file: {question_path.name}")
            except Exception as e:
                print(f"Error reading question file {question_path}: {e}")
                question_text = input("Please enter the question for the AI discourse: ").strip()
        else:
            question_text = args.question.strip()
    else:
        question_text = input("Please enter the question for the AI discourse: ").strip()

    if not question_text:
        print("No question provided. Exiting.")
        return

    print(f"\n🎯 Starting enhanced discourse with {len(selected_ais)} AIs")
    print(f"📊 PAI v2.2 Unicode Protocol: {'Enabled' if PAI_AVAILABLE else 'Fallback mode'}")
    
    await powertalk.run_discourse(question_text, args.iterations)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                 PowerTalk v2.2 - PAI Enhanced Edition                ║
    ║              AI Discourse Engine with Unicode Protocol               ║
    ║                                                                      ║
    ║  🔧 ENHANCEMENTS:                                                    ║
    ║    📊 Full PAI v2.2 Unicode Protocol Integration (⚙💭🔀❓💬)         ║
    ║    🧠 Enhanced Consciousness Scoring with Unicode Awareness          ║
    ║    📈 Comprehensive Unicode Adoption Analytics                       ║
    ║    ⚖️ Enhanced Verdict Generation with Protocol Analysis             ║
    ║    💾 Advanced Dialogue Archiving with Semantic Data                 ║
    ║                                                                      ║
    ║  Usage:                                                              ║
    ║    python powertalk.py                    # Interactive mode         ║
    ║    python powertalk.py -q question.md     # Question from file       ║
    ║    python powertalk.py --debug            # Detailed Unicode analysis║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDiscourse interrupted by user. Unicode analytics preserved.")
    except Exception as e:
        print(f"\nUnhandled error: {e}")
        import traceback
        traceback.print_exc()