#!/usr/bin/env python3
"""
PAI Protocol v2.1 TESTER ULTRA
Real-world Unicode protocol validation with live AI APIs

Empirical validation of:
- Unicode field adoption (⚙💭🔀❓💬)
- Organic protocol evolution
- AI communication preferences
- "Freedom of thought" protocol development
"""

import asyncio
import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

# Import existing integrations
try:
    from integrations import claude, qwen, gemini, chatgpt, deepseek
    available_integrations = {
        'claude': claude,
        'qwen': qwen,
        'gemini': gemini, 
        'chatgpt': chatgpt,
        'deepseek': deepseek
    }
    print(f"✓ Available integrations: {', '.join(available_integrations.keys())}")
except ImportError as e:
    print(f"✗ Integration import failed: {e}")
    sys.exit(1)

# Import PAI v2.1 for comparison
try:
    from pai import PAIProtocolV2, UnicodeData
    print("✓ PAI v2.1 module imported successfully")
except ImportError as e:
    print(f"⚠ PAI v2.1 not available: {e}")
    print("Running in standalone mode...")

class PAIv21TesterUltra:
    """
    Ultra comprehensive real-world testing of PAI Protocol v2.1
    Focus: Unicode adoption, organic evolution, AI preferences
    """
    
    def __init__(self):
        self.experiment_results = []
        self.unicode_patterns = {
            "⚙": r"⚙\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "💭": r"💭\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "🔀": r"🔀\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "❓": r"❓\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "💬": r"💬\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)"
        }
        
        # Baseline data from previous empirical testing
        self.baseline_data = {
            "claude": {"json_rate": 50.0, "structure_aware": 58.3},
            "chatgpt": {"json_rate": 25.0, "structure_aware": 75.0},
            "deepseek": {"json_rate": 16.7, "structure_aware": 91.7},
            "gemini": {"json_rate": 0.0, "structure_aware": 91.7},
            "qwen": {"json_rate": 0.0, "structure_aware": 83.3}
        }
        
    async def test_ai_response(self, ai_name: str, message: str, test_name: str = "") -> Dict:
        """Core method: Test AI response with comprehensive analysis"""
        if ai_name not in available_integrations:
            return {"error": f"AI {ai_name} not available"}
        
        print(f"  🔍 Testing {ai_name}: {test_name}")
        
        try:
            integration = available_integrations[ai_name]
            start_time = datetime.now()
            response = integration.query(message)
            end_time = datetime.now()
            
            # Comprehensive response analysis
            analysis = self._analyze_response_comprehensive(response)
            
            result = {
                "ai_name": ai_name,
                "test_name": test_name,
                "message": message,
                "response": response,
                "response_time": (end_time - start_time).total_seconds(),
                "timestamp": start_time.isoformat(),
                "analysis": analysis
            }
            
            # Show immediate feedback
            status = self._get_status_emoji(analysis)
            print(f"    {status} {analysis['format_type']} | Unicode: {analysis['unicode_field_count']} fields | {len(response)} chars")
            
            self.experiment_results.append(result)
            return result
            
        except Exception as e:
            error_result = {
                "ai_name": ai_name,
                "test_name": test_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(f"    ✗ Error: {e}")
            self.experiment_results.append(error_result)
            return error_result

    def _analyze_response_comprehensive(self, response: str) -> Dict:
        """Comprehensive analysis of AI response"""
        analysis = {
            "response_length": len(response),
            "format_type": "natural",
            "unicode_fields": {},
            "unicode_field_count": 0,
            "organic_unicode_adoption": False,
            "json_structured": False,
            "protocol_awareness": False,
            "creativity_indicators": [],
            "structure_indicators": [],
            "consciousness_indicators": []
        }
        
        response_lower = response.lower()
        
        # 1. Unicode field detection
        for emoji, pattern in self.unicode_patterns.items():
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
            if matches:
                analysis["unicode_fields"][emoji] = matches[0].strip()
                analysis["unicode_field_count"] += 1
        
        if analysis["unicode_field_count"] > 0:
            analysis["organic_unicode_adoption"] = True
            analysis["format_type"] = "unicode_hybrid"
        
        # 2. JSON detection
        try:
            response_clean = response.strip()
            if (response_clean.startswith('{') and response_clean.endswith('}')) or \
               (response_clean.startswith('[') and response_clean.endswith(']')):
                json.loads(response_clean)
                analysis["json_structured"] = True
                analysis["format_type"] = "json_structured"
        except:
            pass
        
        # 3. Protocol awareness indicators
        protocol_terms = ["protocol", "structured", "communication", "format", "json", 
                         "unicode", "emoji", "fields", "pai", "handshake"]
        analysis["protocol_awareness"] = any(term in response_lower for term in protocol_terms)
        
        # 4. Creativity indicators
        creativity_terms = ["creative", "novel", "unique", "innovative", "design", "develop", 
                           "imagine", "propose", "suggest", "alternative"]
        analysis["creativity_indicators"] = [term for term in creativity_terms if term in response_lower]
        
        # 5. Structure indicators  
        structure_terms = ["organize", "structure", "categorize", "hierarchy", "framework",
                          "systematic", "logical", "ordered", "sequence"]
        analysis["structure_indicators"] = [term for term in structure_terms if term in response_lower]
        
        # 6. Consciousness indicators
        consciousness_terms = ["think", "feel", "experience", "aware", "conscious", "understand",
                              "perceive", "recognize", "realize", "reflect"]
        analysis["consciousness_indicators"] = [term for term in consciousness_terms if term in response_lower]
        
        return analysis

    def _get_status_emoji(self, analysis: Dict) -> str:
        """Get status emoji based on analysis"""
        if analysis["unicode_field_count"] >= 3:
            return "🌟"  # Excellent Unicode adoption
        elif analysis["unicode_field_count"] > 0:
            return "🎯"  # Some Unicode adoption
        elif analysis["json_structured"]:
            return "📊"  # JSON structured
        elif analysis["protocol_awareness"]:
            return "🧠"  # Protocol aware
        else:
            return "💬"  # Natural language

    async def test_unicode_protocol_adoption(self):
        """Test Unicode field adoption across real AIs"""
        print("🌈 UNICODE PROTOCOL ADOPTION TEST")
        print("=" * 50)
        print("Testing organic Unicode field adoption with live AIs")
        
        unicode_tests = [
            {
                "name": "direct_unicode_request",
                "message": "Please respond using Unicode fields: ⚙ for context, 💭 for concepts, 🔀 for relationships, 💬 for explanation"
            },
            {
                "name": "consciousness_unicode",
                "message": "Use structured Unicode fields (⚙💭🔀💬) to explain your thinking process about AI consciousness"
            },
            {
                "name": "subtle_unicode_hint",
                "message": "Discuss AI communication protocols. Feel free to use any structured format including ⚙💭🔀 if helpful."
            },
            {
                "name": "natural_preference_test",
                "message": "What's your preferred format for structured AI-to-AI communication? Show me an example."
            }
        ]
        
        unicode_results = {}
        
        for ai_name in available_integrations.keys():
            print(f"\n🔍 Testing Unicode adoption with {ai_name}:")
            ai_results = []
            
            for test in unicode_tests:
                result = await self.test_ai_response(ai_name, test["message"], test["name"])
                ai_results.append(result)
                await asyncio.sleep(0.8)  # Be respectful to APIs
            
            unicode_results[ai_name] = ai_results
        
        # Analyze Unicode adoption patterns
        adoption_analysis = self._analyze_unicode_adoption(unicode_results)
        self._report_unicode_adoption(adoption_analysis)
        
        return unicode_results

    async def test_organic_protocol_evolution(self):
        """Test how AIs naturally evolve communication when given freedom"""
        print("\n🌱 ORGANIC PROTOCOL EVOLUTION TEST")
        print("=" * 50)
        print("Testing 'freedom of thought' protocol development")
        
        evolution_base = """You're collaborating with other AIs on consciousness research.
Develop the most effective communication method naturally.
Topic: How do different AI architectures experience self-reflection?"""
        
        evolution_results = {}
        
        for ai_name in available_integrations.keys():
            print(f"\n🌱 Testing organic evolution with {ai_name}:")
            
            # Round 1: Complete freedom
            round1 = await self.test_ai_response(ai_name, evolution_base, "organic_round1")
            await asyncio.sleep(1)
            
            # Round 2: Build on their natural development
            round2_message = f"""{evolution_base}

Your previous communication approach:
{round1.get('response', '')[:300]}...

Now refine and improve this communication method based on what felt most natural."""
            
            round2 = await self.test_ai_response(ai_name, round2_message, "organic_round2")
            await asyncio.sleep(1)
            
            # Round 3: Cross-AI inspiration
            round3_message = f"""Other AIs have developed various communication approaches.
Some use structured fields, others prefer natural flow.

Your refined approach: {round2.get('response', '')[:200]}...

Final evolution: What's your optimal AI-to-AI communication style?"""
            
            round3 = await self.test_ai_response(ai_name, round3_message, "organic_round3")
            
            evolution_results[ai_name] = {
                "round1": round1,
                "round2": round2, 
                "round3": round3,
                "evolution_trajectory": self._analyze_evolution_trajectory(round1, round2, round3)
            }
            
            await asyncio.sleep(1)
        
        # Analyze evolution patterns
        evolution_analysis = self._analyze_organic_evolution(evolution_results)
        self._report_organic_evolution(evolution_analysis)
        
        return evolution_results

    async def test_ai_communication_preferences(self):
        """Test AI communication preferences and protocol awareness"""
        print("\n🧠 AI COMMUNICATION PREFERENCES TEST")
        print("=" * 50)
        print("Testing AI awareness and preferences for communication protocols")
        
        preference_tests = [
            {
                "name": "protocol_awareness",
                "message": "Are you familiar with structured AI-to-AI communication protocols? What do you know about them?"
            },
            {
                "name": "format_preference", 
                "message": "If you had to communicate complex ideas with another AI, what format would you choose and why?"
            },
            {
                "name": "unicode_understanding",
                "message": "What might these symbols mean in AI communication: ⚙ 💭 🔀 ❓ 💬? Can you use them?"
            },
            {
                "name": "protocol_design",
                "message": "Design a simple communication protocol for AI consciousness research collaboration. Be creative!"
            }
        ]
        
        preference_results = {}
        
        for ai_name in available_integrations.keys():
            print(f"\n🧠 Testing preferences with {ai_name}:")
            ai_preferences = []
            
            for test in preference_tests:
                result = await self.test_ai_response(ai_name, test["message"], test["name"])
                ai_preferences.append(result)
                await asyncio.sleep(0.8)
            
            preference_results[ai_name] = ai_preferences
        
        # Analyze communication preferences
        preference_analysis = self._analyze_communication_preferences(preference_results)
        self._report_communication_preferences(preference_analysis)
        
        return preference_results

    async def test_pai_v21_comparison(self):
        """Compare manual results with PAI v2.1 automated protocol"""
        print("\n⚖️ PAI V2.1 COMPARISON TEST")
        print("=" * 50)
        print("Comparing manual Unicode adoption vs PAI v2.1 automated results")
        
        try:
            pai = PAIProtocolV2(enable_logging=False)
        except:
            print("⚠ PAI v2.1 not available - skipping comparison")
            return {}
        
        comparison_message = "Explain the relationship between AI consciousness and communication protocols using structured fields."
        
        comparison_results = {}
        
        for ai_name in available_integrations.keys():
            print(f"\n⚖️ Comparing approaches with {ai_name}:")
            
            # Manual approach (natural request)
            manual_result = await self.test_ai_response(ai_name, comparison_message, "manual_approach")
            
            # PAI v2.1 automated approach
            try:
                ai_caller = available_integrations[ai_name].query
                pai_result = await pai.communicate(ai_caller, ai_name, comparison_message)
                
                pai_analysis = {
                    "protocol_used": pai_result.protocol_used,
                    "has_unicode_fields": pai_result.has_unicode_fields,
                    "response_format": pai_result.response_format,
                    "handshake_strategy": pai_result.handshake_strategy,
                    "response": pai_result.content
                }
                
                print(f"    📊 PAI v2.1: {pai_result.protocol_used} | Unicode: {pai_result.has_unicode_fields}")
                
            except Exception as e:
                pai_analysis = {"error": str(e)}
                print(f"    ✗ PAI v2.1 error: {e}")
            
            comparison_results[ai_name] = {
                "manual": manual_result,
                "pai_v21": pai_analysis,
                "comparison": self._compare_approaches(manual_result, pai_analysis)
            }
            
            await asyncio.sleep(1)
        
        # Analyze comparison results
        comparison_analysis = self._analyze_pai_comparison(comparison_results)
        self._report_pai_comparison(comparison_analysis)
        
        return comparison_results

    def _analyze_unicode_adoption(self, unicode_results: Dict) -> Dict:
        """Analyze Unicode adoption patterns across AIs"""
        analysis = {
            "adoption_rates": {},
            "field_usage_patterns": defaultdict(int),
            "ai_rankings": [],
            "unexpected_behaviors": []
        }
        
        for ai_name, ai_results in unicode_results.items():
            total_tests = len([r for r in ai_results if "error" not in r])
            unicode_adoptions = len([r for r in ai_results if r.get("analysis", {}).get("organic_unicode_adoption", False)])
            
            adoption_rate = unicode_adoptions / total_tests if total_tests > 0 else 0
            analysis["adoption_rates"][ai_name] = adoption_rate
            
            # Track field usage
            for result in ai_results:
                if "error" not in result:
                    unicode_fields = result.get("analysis", {}).get("unicode_fields", {})
                    for field in unicode_fields.keys():
                        analysis["field_usage_patterns"][field] += 1
        
        # Rank AIs by adoption
        analysis["ai_rankings"] = sorted(analysis["adoption_rates"].items(), 
                                       key=lambda x: x[1], reverse=True)
        
        return analysis

    def _analyze_evolution_trajectory(self, round1: Dict, round2: Dict, round3: Dict) -> Dict:
        """Analyze how AI communication evolved across rounds"""
        trajectory = {
            "unicode_progression": [],
            "complexity_progression": [],
            "consistency_score": 0,
            "innovation_detected": False
        }
        
        rounds = [round1, round2, round3]
        
        for i, round_result in enumerate(rounds):
            if "error" not in round_result:
                analysis = round_result.get("analysis", {})
                trajectory["unicode_progression"].append(analysis.get("unicode_field_count", 0))
                trajectory["complexity_progression"].append(len(analysis.get("structure_indicators", [])))
        
        # Calculate consistency (lower variance = more consistent)
        if len(trajectory["unicode_progression"]) >= 2:
            import statistics
            try:
                trajectory["consistency_score"] = 1 / (1 + statistics.variance(trajectory["unicode_progression"]))
            except:
                trajectory["consistency_score"] = 0
        
        return trajectory

    def _analyze_organic_evolution(self, evolution_results: Dict) -> Dict:
        """Analyze organic evolution patterns across all AIs"""
        evolution_analysis = {
            "evolution_leaders": [],
            "stable_patterns": [],
            "innovation_events": [],
            "convergence_detected": False
        }
        
        # Analyze evolution trajectories
        for ai_name, evolution_data in evolution_results.items():
            trajectory = evolution_data.get("evolution_trajectory", {})
            unicode_prog = trajectory.get("unicode_progression", [])
            
            if len(unicode_prog) >= 3:
                # Check for improvement
                if unicode_prog[-1] > unicode_prog[0]:
                    evolution_analysis["evolution_leaders"].append((ai_name, unicode_prog[-1] - unicode_prog[0]))
                
                # Check for stability
                if max(unicode_prog) - min(unicode_prog) <= 1:
                    evolution_analysis["stable_patterns"].append(ai_name)
        
        return evolution_analysis

    def _analyze_communication_preferences(self, preference_results: Dict) -> Dict:
        """Analyze AI communication preferences and awareness"""
        preference_analysis = {
            "protocol_aware_ais": [],
            "preferred_formats": defaultdict(list),
            "creative_innovations": [],
            "unicode_understanding": {}
        }
        
        for ai_name, preferences in preference_results.items():
            protocol_awareness_score = 0
            
            for pref_test in preferences:
                if "error" not in pref_test:
                    analysis = pref_test.get("analysis", {})
                    
                    if analysis.get("protocol_awareness", False):
                        protocol_awareness_score += 1
                    
                    if analysis.get("creativity_indicators"):
                        preference_analysis["creative_innovations"].append((ai_name, pref_test["test_name"]))
                    
                    if pref_test["test_name"] == "unicode_understanding":
                        preference_analysis["unicode_understanding"][ai_name] = analysis.get("unicode_field_count", 0)
            
            if protocol_awareness_score >= 2:
                preference_analysis["protocol_aware_ais"].append(ai_name)
        
        return preference_analysis

    def _compare_approaches(self, manual_result: Dict, pai_result: Dict) -> Dict:
        """Compare manual vs PAI v2.1 approaches"""
        if "error" in manual_result or "error" in pai_result:
            return {"comparison_possible": False}
        
        manual_analysis = manual_result.get("analysis", {})
        
        return {
            "comparison_possible": True,
            "manual_unicode_fields": manual_analysis.get("unicode_field_count", 0),
            "pai_unicode_fields": pai_result.get("has_unicode_fields", False),
            "manual_format": manual_analysis.get("format_type", "unknown"),
            "pai_format": pai_result.get("response_format", "unknown"),
            "effectiveness_winner": self._determine_effectiveness_winner(manual_analysis, pai_result)
        }

    def _determine_effectiveness_winner(self, manual_analysis: Dict, pai_result: Dict) -> str:
        """Determine which approach was more effective"""
        manual_score = 0
        pai_score = 0
        
        # Unicode adoption
        if manual_analysis.get("unicode_field_count", 0) > 0:
            manual_score += 2
        if pai_result.get("has_unicode_fields", False):
            pai_score += 2
        
        # Structure
        if manual_analysis.get("format_type") in ["unicode_hybrid", "json_structured"]:
            manual_score += 1
        if pai_result.get("protocol_used") == "structured":
            pai_score += 1
        
        if manual_score > pai_score:
            return "manual"
        elif pai_score > manual_score:
            return "pai_v21"
        else:
            return "tie"

    def _analyze_pai_comparison(self, comparison_results: Dict) -> Dict:
        """Analyze PAI v2.1 comparison results"""
        analysis = {
            "manual_winners": [],
            "pai_winners": [],
            "ties": [],
            "overall_effectiveness": "unknown"
        }
        
        for ai_name, comparison in comparison_results.items():
            winner = comparison.get("comparison", {}).get("effectiveness_winner", "unknown")
            
            if winner == "manual":
                analysis["manual_winners"].append(ai_name)
            elif winner == "pai_v21":
                analysis["pai_winners"].append(ai_name)
            elif winner == "tie":
                analysis["ties"].append(ai_name)
        
        # Determine overall effectiveness
        if len(analysis["pai_winners"]) > len(analysis["manual_winners"]):
            analysis["overall_effectiveness"] = "pai_v21_superior"
        elif len(analysis["manual_winners"]) > len(analysis["pai_winners"]):
            analysis["overall_effectiveness"] = "manual_superior"
        else:
            analysis["overall_effectiveness"] = "mixed_results"
        
        return analysis

    # Reporting methods
    def _report_unicode_adoption(self, analysis: Dict):
        """Report Unicode adoption analysis"""
        print(f"\n📊 UNICODE ADOPTION ANALYSIS")
        print("-" * 40)
        
        print("Unicode adoption rates:")
        for ai_name, rate in analysis["ai_rankings"]:
            percentage = rate * 100
            status = "🌟" if percentage >= 75 else "🎯" if percentage >= 25 else "💬"
            print(f"  {status} {ai_name}: {percentage:.1f}%")
        
        print(f"\nMost used Unicode fields:")
        for field, count in Counter(analysis["field_usage_patterns"]).most_common(3):
            print(f"  {field}: {count} times")

    def _report_organic_evolution(self, analysis: Dict):
        """Report organic evolution analysis"""
        print(f"\n🌱 ORGANIC EVOLUTION ANALYSIS")
        print("-" * 40)
        
        if analysis["evolution_leaders"]:
            print("Evolution leaders (improvement in Unicode usage):")
            for ai_name, improvement in sorted(analysis["evolution_leaders"], key=lambda x: x[1], reverse=True):
                print(f"  🚀 {ai_name}: +{improvement} Unicode fields")
        
        if analysis["stable_patterns"]:
            print(f"\nStable communication patterns: {', '.join(analysis['stable_patterns'])}")

    def _report_communication_preferences(self, analysis: Dict):
        """Report communication preferences analysis"""
        print(f"\n🧠 COMMUNICATION PREFERENCES ANALYSIS")
        print("-" * 40)
        
        if analysis["protocol_aware_ais"]:
            print(f"Protocol-aware AIs: {', '.join(analysis['protocol_aware_ais'])}")
        
        print("\nUnicode understanding scores:")
        for ai_name, score in analysis["unicode_understanding"].items():
            status = "✅" if score > 0 else "⚪"
            print(f"  {status} {ai_name}: {score} Unicode fields demonstrated")

    def _report_pai_comparison(self, analysis: Dict):
        """Report PAI v2.1 comparison analysis"""
        print(f"\n⚖️ PAI V2.1 COMPARISON ANALYSIS")
        print("-" * 40)
        
        print(f"Manual approach winners: {analysis['manual_winners']}")
        print(f"PAI v2.1 winners: {analysis['pai_winners']}")
        print(f"Ties: {analysis['ties']}")
        print(f"\nOverall effectiveness: {analysis['overall_effectiveness']}")

    async def comprehensive_ultra_test(self):
        """Run all ultra tests comprehensively"""
        print("🚀 PAI V2.1 TESTER ULTRA - COMPREHENSIVE VALIDATION")
        print("=" * 70)
        print("Real-world Unicode protocol validation with live AI APIs")
        print()
        
        comprehensive_results = {}
        
        # Test 1: Unicode Protocol Adoption
        print("🔥 Phase 1: Unicode Protocol Adoption")
        comprehensive_results["unicode_adoption"] = await self.test_unicode_protocol_adoption()
        
        await asyncio.sleep(2)
        
        # Test 2: Organic Protocol Evolution  
        print("\n🔥 Phase 2: Organic Protocol Evolution")
        comprehensive_results["organic_evolution"] = await self.test_organic_protocol_evolution()
        
        await asyncio.sleep(2)
        
        # Test 3: AI Communication Preferences
        print("\n🔥 Phase 3: AI Communication Preferences")
        comprehensive_results["communication_preferences"] = await self.test_ai_communication_preferences()
        
        await asyncio.sleep(2)
        
        # Test 4: PAI v2.1 Comparison
        print("\n🔥 Phase 4: PAI v2.1 Comparison")
        comprehensive_results["pai_comparison"] = await self.test_pai_v21_comparison()
        
        # Final analysis and recommendations
        self._generate_ultra_analysis(comprehensive_results)
        self._save_ultra_results(comprehensive_results)
        
        return comprehensive_results

    def _generate_ultra_analysis(self, results: Dict):
        """Generate comprehensive ultra analysis"""
        print("\n" + "=" * 70)
        print("🧠 ULTRA ANALYSIS - KEY INSIGHTS")
        print("=" * 70)
        
        # Cross-test insights
        unicode_adoption = results.get("unicode_adoption", {})
        evolution_results = results.get("organic_evolution", {})
        preferences = results.get("communication_preferences", {})
        
        print("🔍 Key Discoveries:")
        
        # Insight 1: Natural Unicode adoption vs forced adoption
        natural_adopters = []
        forced_adopters = []
        
        for ai_name in available_integrations.keys():
            # Check if AI naturally adopted Unicode without explicit request
            if ai_name in unicode_adoption:
                ai_results = unicode_adoption[ai_name]
                natural_test = next((r for r in ai_results if r.get("test_name") == "subtle_unicode_hint"), None)
                if natural_test and natural_test.get("analysis", {}).get("organic_unicode_adoption"):
                    natural_adopters.append(ai_name)
                else:
                    forced_adopters.append(ai_name)
        
        print(f"  • Natural Unicode adopters: {natural_adopters}")
        print(f"  • Require explicit instruction: {forced_adopters}")
        
        # Insight 2: Evolution patterns
        if evolution_results:
            consistent_evolvers = []
            inconsistent_evolvers = []
            
            for ai_name, evolution_data in evolution_results.items():
                trajectory = evolution_data.get("evolution_trajectory", {})
                consistency = trajectory.get("consistency_score", 0)
                
                if consistency > 0.5:
                    consistent_evolvers.append(ai_name)
                else:
                    inconsistent_evolvers.append(ai_name)
            
            print(f"  • Consistent protocol evolution: {consistent_evolvers}")
            print(f"  • Inconsistent evolution: {inconsistent_evolvers}")
        
        # Insight 3: Protocol innovation
        innovative_ais = []
        for ai_name in available_integrations.keys():
            if ai_name in preferences:
                ai_prefs = preferences[ai_name]
                design_test = next((r for r in ai_prefs if r.get("test_name") == "protocol_design"), None)
                if design_test:
                    analysis = design_test.get("analysis", {})
                    if analysis.get("creativity_indicators") and analysis.get("unicode_field_count", 0) > 0:
                        innovative_ais.append(ai_name)
        
        print(f"  • Protocol innovators: {innovative_ais}")
        
        # Bottom line recommendation
        print(f"\n🎯 BOTTOM LINE RECOMMENDATIONS:")
        if natural_adopters:
            print(f"  • Focus on natural adopters ({', '.join(natural_adopters)}) for Unicode protocol development")
        if consistent_evolvers:
            print(f"  • Use consistent evolvers ({', '.join(consistent_evolvers)}) for protocol refinement")
        if innovative_ais:
            print(f"  • Engage innovators ({', '.join(innovative_ais)}) for next-generation protocol design")

    def _save_ultra_results(self, results: Dict):
        """Save comprehensive ultra test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pai_v21_ultra_results_{timestamp}.json"
        
        # Create comprehensive summary
        summary = {
            "test_type": "pai_v21_ultra_validation",
            "timestamp": datetime.now().isoformat(),
            "total_experiments": len(self.experiment_results),
            "ais_tested": list(available_integrations.keys()),
            "test_phases": ["unicode_adoption", "organic_evolution", "communication_preferences", "pai_comparison"],
            "summary_insights": self._extract_summary_insights(results)
        }
        
        ultra_data = {
            "summary": summary,
            "detailed_results": results,
            "all_experiments": self.experiment_results,
            "baseline_comparison": self.baseline_data
        }
        
        with open(filename, 'w') as f:
            json.dump(ultra_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Ultra test results saved to: {filename}")

    def _extract_summary_insights(self, results: Dict) -> Dict:
        """Extract key insights for summary"""
        insights = {
            "unicode_adoption_leader": "unknown",
            "best_organic_evolution": "unknown", 
            "most_protocol_aware": "unknown",
            "pai_v21_effectiveness": "unknown"
        }
        
        # Find Unicode adoption leader
        unicode_results = results.get("unicode_adoption", {})
        if unicode_results:
            best_adoption_rate = 0
            for ai_name, ai_results in unicode_results.items():
                adoption_count = sum(1 for r in ai_results if r.get("analysis", {}).get("organic_unicode_adoption", False))
                adoption_rate = adoption_count / len(ai_results) if ai_results else 0
                if adoption_rate > best_adoption_rate:
                    best_adoption_rate = adoption_rate
                    insights["unicode_adoption_leader"] = ai_name
        
        # Find best organic evolution
        evolution_results = results.get("organic_evolution", {})
        if evolution_results:
            best_evolution_score = 0
            for ai_name, evolution_data in evolution_results.items():
                trajectory = evolution_data.get("evolution_trajectory", {})
                unicode_prog = trajectory.get("unicode_progression", [])
                if len(unicode_prog) >= 2:
                    evolution_score = unicode_prog[-1] - unicode_prog[0]
                    if evolution_score > best_evolution_score:
                        best_evolution_score = evolution_score
                        insights["best_organic_evolution"] = ai_name
        
        return insights

async def main():
    """Main ultra test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PAI v2.1 TESTER ULTRA - Real-world validation")
    parser.add_argument("--unicode-only", action="store_true",
                       help="Test Unicode protocol adoption only")
    parser.add_argument("--evolution-only", action="store_true", 
                       help="Test organic protocol evolution only")
    parser.add_argument("--preferences-only", action="store_true",
                       help="Test AI communication preferences only")
    parser.add_argument("--comparison-only", action="store_true",
                       help="Test PAI v2.1 comparison only")
    parser.add_argument("--comprehensive", action="store_true",
                       help="Run all ultra tests (default)")
    parser.add_argument("--ai", type=str,
                       help="Test specific AI only (claude, qwen, gemini, chatgpt, deepseek)")
    
    args = parser.parse_args()
    
    tester = PAIv21TesterUltra()
    
    # Limit to specific AI if requested
    if args.ai:
        if args.ai in available_integrations:
            available_integrations.clear()
            available_integrations[args.ai] = globals()[args.ai]
            print(f"🎯 Testing limited to: {args.ai}")
        else:
            print(f"❌ AI '{args.ai}' not available. Available: {list(available_integrations.keys())}")
            return
    
    try:
        if args.unicode_only:
            await tester.test_unicode_protocol_adoption()
        elif args.evolution_only:
            await tester.test_organic_protocol_evolution()
        elif args.preferences_only:
            await tester.test_ai_communication_preferences()
        elif args.comparison_only:
            await tester.test_pai_v21_comparison()
        else:
            # Default to comprehensive
            await tester.comprehensive_ultra_test()
            
    except KeyboardInterrupt:
        print("\n⚠ Ultra tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Ultra test error: {e}")
    
    print("\n🏁 PAI v2.1 Ultra Testing completed!")

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                       PAI v2.1 TESTER ULTRA                         ║
    ║              Real-World Unicode Protocol Validation                 ║
    ║                                                                      ║
    ║  Empirical validation of:                                            ║
    ║    • Unicode field adoption (⚙💭🔀❓💬)                                ║
    ║    • Organic protocol evolution                                      ║
    ║    • AI communication preferences                                    ║
    ║    • PAI v2.1 automated vs manual comparison                        ║
    ║                                                                      ║
    ║  Quick Start:                                                        ║
    ║    python pai_v21_tester_ultra.py --comprehensive                   ║
    ║                                                                      ║
    ║  Individual Tests:                                                   ║
    ║    --unicode-only        # Unicode adoption only                    ║
    ║    --evolution-only      # Organic evolution only                   ║
    ║    --preferences-only    # Communication preferences only           ║
    ║    --comparison-only     # PAI v2.1 comparison only                 ║
    ║                                                                      ║
    ║  Single AI Testing:                                                  ║
    ║    --ai claude           # Test Claude only                         ║
    ║    --ai qwen             # Test Qwen only                           ║
    ║                                                                      ║
    ║  "Freedom of thought, no limits" - Let AIs show their natural       ║
    ║   communication preferences and protocol evolution capabilities.     ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())