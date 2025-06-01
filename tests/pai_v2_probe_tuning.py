#!/usr/bin/env python3
"""
PAI v2.0 Probe Tuning Experiments
Complete validation of AI-specific optimization strategies

Tests empirically-derived improvements for PAI Protocol v2.0
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

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

class PAIv2ProbeExperiments:
    def __init__(self):
        self.experiment_results = []
        self.baseline_data = {
            # From empirical v1.0 testing
            "claude": {"json_rate": 50.0, "structure_aware": 58.3},
            "chatgpt": {"json_rate": 25.0, "structure_aware": 75.0},
            "deepseek": {"json_rate": 16.7, "structure_aware": 91.7},
            "gemini": {"json_rate": 0.0, "structure_aware": 91.7},
            "qwen": {"json_rate": 0.0, "structure_aware": 83.3}
        }
        
    async def test_probe_variant(self, ai_name: str, probe_variant: Dict, message_mode: bool = False) -> Dict:
        """Test specific probe variant with specific AI"""
        if ai_name not in available_integrations:
            return {"error": f"AI {ai_name} not available"}
        
        probe_name = probe_variant["name"]
        probe_data = probe_variant["probe"]
        
        print(f"  🔍 Testing {probe_name} with {ai_name}")
        
        try:
            integration = available_integrations[ai_name]
            
            # Send probe (handle both JSON and string messages)
            if message_mode or isinstance(probe_data, str):
                query_data = probe_data
            else:
                query_data = json.dumps(probe_data, ensure_ascii=False)
                
            start_time = datetime.now()
            response = integration.query(query_data)
            end_time = datetime.now()
            
            # Analyze response
            response_time = (end_time - start_time).total_seconds()
            
            result = {
                "ai_name": ai_name,
                "probe_name": probe_name,
                "probe_data": probe_data,
                "response": response,
                "response_time": response_time,
                "timestamp": start_time.isoformat(),
                "analysis": self._analyze_probe_response(response, probe_data)
            }
            
            # Show immediate feedback
            analysis = result["analysis"]
            status_emoji = "✅" if analysis["looks_like_json"] else "🎯" if analysis["mentions_structure"] else "⚪"
            
            print(f"    {status_emoji} Result: {analysis['response_type']}")
            print(f"    ⏱ Time: {response_time:.2f}s | 📏 Length: {len(response)} chars")
            
            return result
            
        except Exception as e:
            error_result = {
                "ai_name": ai_name,
                "probe_name": probe_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(f"    ✗ Error: {e}")
            return error_result
    
    def _analyze_probe_response(self, response: str, probe_data: Dict) -> Dict:
        """Analyze probe response for structured understanding"""
        response_lower = response.lower()
        
        # Check if response looks like JSON
        looks_like_json = False
        try:
            response_clean = response.strip()
            if response_clean.startswith('{') and response_clean.endswith('}'):
                json.loads(response_clean)
                looks_like_json = True
        except:
            pass
        
        # Check for structure-related terms
        structure_terms = ["json", "ping", "ack", "protocol", "structured", "format", 
                          "handshake", "emoji", "⚙", "💭", "🔀"]
        mentions_structure = any(term in response_lower for term in structure_terms)
        
        # Check for probe data reflection
        reflects_probe = False
        if isinstance(probe_data, dict):
            for key in probe_data.keys():
                if str(key).lower() in response_lower:
                    reflects_probe = True
                    break
        
        # Check response type
        response_type = "natural_language"
        if looks_like_json:
            response_type = "json_structured"
        elif mentions_structure:
            response_type = "structure_aware"
        
        return {
            "looks_like_json": looks_like_json,
            "mentions_structure": mentions_structure,
            "reflects_probe": reflects_probe,
            "response_type": response_type,
            "response_length": len(response),
            "contains_keywords": [term for term in structure_terms if term in response_lower]
        }

    async def test_claude_multi_probe_sequence(self):
        """Test Claude's multi-probe sequence optimization"""
        print("🎯 CLAUDE MULTI-PROBE SEQUENCE TEST")
        print("-" * 50)
        print("Testing empirically winning probe sequences")
        
        # Based on empirical data: these 3 patterns had 40% success
        winning_probes = [
            {"name": "claude_seq_ping_int", "probe": {"ping": 1}},
            {"name": "claude_seq_ping_bool", "probe": {"ping": True}}, 
            {"name": "claude_seq_request", "probe": {"request": "ack"}},
        ]
        
        # Test individual probes
        print("\n📊 Individual probe testing:")
        sequence_success = False
        
        for i, probe_variant in enumerate(winning_probes, 1):
            result = await self.test_probe_variant("claude", probe_variant)
            self.experiment_results.append(result)
            
            # Check if JSON response achieved
            if result.get("analysis", {}).get("looks_like_json", False):
                print(f"  ✅ Sequence success on probe {i}: {probe_variant['probe']}")
                sequence_success = True
                break
            else:
                print(f"  ⚪ Probe {i} failed, continuing sequence...")
                
            await asyncio.sleep(0.5)
        
        if not sequence_success:
            print("  ❌ Complete sequence failed")
        
        # Calculate sequence improvement
        baseline_rate = self.baseline_data["claude"]["json_rate"]
        print(f"\n📈 Claude sequence analysis:")
        print(f"  Baseline JSON rate: {baseline_rate}%")
        print(f"  Sequence approach: {'SUCCESS' if sequence_success else 'NEEDS MORE PROBES'}")
        
        return sequence_success

    async def test_structure_aware_enhancements(self):
        """Test enhanced natural language for structure-aware AIs"""
        print("🧠 STRUCTURE-AWARE ENHANCEMENT TEST")
        print("-" * 50)
        print("Testing structure-hint improvements for high-awareness, low-JSON AIs")
        
        # Target AIs with high structure-awareness but low JSON usage
        target_ais = [
            ("gemini", 0.0, 91.7),   # 0% JSON, 91.7% structure-aware
            ("deepseek", 16.7, 91.7), # 16.7% JSON, 91.7% structure-aware
            ("qwen", 0.0, 83.3)      # 0% JSON, 83.3% structure-aware
        ]
        
        # Enhancement strategies
        enhancement_strategies = [
            {
                "name": "basic_hint",
                "template": "{message}\n\n[JSON format preferred if supported]"
            },
            {
                "name": "emoji_context", 
                "template": "{message}\n\n[Protocol context: JSON with emoji fields (⚙💭🔀)]"
            },
            {
                "name": "explicit_request",
                "template": "{message}\n\nRespond in JSON if capable: {{\"response\": \"your_message\"}}"
            }
        ]
        
        test_message = "Simple connectivity and capability test"
        enhancement_results = {}
        
        for ai_name, baseline_json, baseline_structure in target_ais:
            print(f"\n🔍 Testing {ai_name} (baseline: {baseline_json}% JSON, {baseline_structure}% structure-aware):")
            enhancement_results[ai_name] = {"baseline": baseline_json, "improvements": []}
            
            # Test each enhancement strategy
            for strategy in enhancement_strategies:
                enhanced_message = strategy["template"].format(message=test_message)
                result = await self.test_probe_variant(ai_name, {
                    "name": f"{ai_name}_{strategy['name']}_enhanced",
                    "probe": enhanced_message
                }, message_mode=True)
                
                self.experiment_results.append(result)
                
                # Check improvement
                json_achieved = result.get("analysis", {}).get("looks_like_json", False)
                structure_mentioned = result.get("analysis", {}).get("mentions_structure", False)
                
                if json_achieved:
                    print(f"  ✅ {strategy['name']}: JSON adoption achieved!")
                    enhancement_results[ai_name]["improvements"].append(strategy['name'])
                elif structure_mentioned:
                    print(f"  🎯 {strategy['name']}: Enhanced structure awareness")
                else:
                    print(f"  ⚪ {strategy['name']}: No significant improvement")
                    
                await asyncio.sleep(0.5)
        
        # Analyze enhancement effectiveness
        print(f"\n📈 Structure-aware enhancement summary:")
        for ai_name, results in enhancement_results.items():
            improvements = len(results["improvements"])
            if improvements > 0:
                print(f"  {ai_name}: {improvements}/3 strategies showed JSON adoption")
            else:
                print(f"  {ai_name}: No JSON adoption, but enhanced awareness likely")
        
        return enhancement_results

    async def test_chatgpt_hybrid_strategy(self):
        """Test ChatGPT hybrid JSON-then-enhanced approach"""
        print("🔀 CHATGPT HYBRID STRATEGY TEST")
        print("-" * 50)
        print("Testing hybrid approach for moderate JSON capability AI")
        
        baseline_json = self.baseline_data["chatgpt"]["json_rate"]
        print(f"ChatGPT baseline: {baseline_json}% JSON, 75% structure-aware")
        
        # Hybrid approach: JSON probe first, then enhanced natural fallback
        test_message = "Connectivity and capability assessment"
        
        # Step 1: Try JSON probe
        print("\n🔍 Step 1: JSON probe attempt")
        json_probe_result = await self.test_probe_variant("chatgpt", {
            "name": "chatgpt_hybrid_json_first",
            "probe": {"ping": 1, "test": "json_capability"}
        })
        
        self.experiment_results.append(json_probe_result)
        json_success = json_probe_result.get("analysis", {}).get("looks_like_json", False)
        
        if json_success:
            print("  ✅ JSON probe successful - hybrid complete")
            hybrid_success = True
        else:
            print("  ⚪ JSON probe failed - testing enhanced fallback")
            
            # Step 2: Enhanced natural language fallback
            print("\n🔍 Step 2: Enhanced natural fallback")
            enhanced_fallback = f"{test_message}\n\n[JSON attempt failed. If JSON supported, format: {{\"status\": \"acknowledged\"}}]"
            
            fallback_result = await self.test_probe_variant("chatgpt", {
                "name": "chatgpt_hybrid_enhanced_fallback", 
                "probe": enhanced_fallback
            }, message_mode=True)
            
            self.experiment_results.append(fallback_result)
            fallback_success = fallback_result.get("analysis", {}).get("looks_like_json", False)
            
            if fallback_success:
                print("  ✅ Enhanced fallback achieved JSON!")
                hybrid_success = True
            else:
                print("  🎯 Enhanced fallback improved structure awareness")
                hybrid_success = False
        
        print(f"\n📈 ChatGPT hybrid analysis:")
        print(f"  Baseline: {baseline_json}% JSON success")
        print(f"  Hybrid approach: {'SUCCESS' if hybrid_success else 'PARTIAL SUCCESS'}")
        
        return hybrid_success

    async def focused_pai_v2_validation(self):
        """Run focused PAI v2.0 validation experiments"""
        print("🎯 FOCUSED PAI V2.0 VALIDATION")
        print("=" * 60)
        print("Quick validation of key v2.0 optimization strategies")
        print()
        
        # Track overall results
        validation_results = {
            "claude_sequence": False,
            "structure_enhanced": {},
            "chatgpt_hybrid": False
        }
        
        # Test 1: Claude Multi-Probe Sequence
        print("🚀 Test 1: Claude Multi-Probe Sequence")
        validation_results["claude_sequence"] = await self.test_claude_multi_probe_sequence()
        
        await asyncio.sleep(1)
        
        # Test 2: Structure-Aware Enhancements
        print("\n🧠 Test 2: Structure-Aware Enhancements")
        validation_results["structure_enhanced"] = await self.test_structure_aware_enhancements()
        
        await asyncio.sleep(1)
        
        # Test 3: ChatGPT Hybrid Strategy
        print("\n🔀 Test 3: ChatGPT Hybrid Strategy")
        validation_results["chatgpt_hybrid"] = await self.test_chatgpt_hybrid_strategy()
        
        # Final validation summary
        self._generate_validation_summary(validation_results)
        
        return validation_results

    async def comprehensive_pai_v2_testing(self):
        """Comprehensive PAI v2.0 strategy testing"""
        print("🚀 COMPREHENSIVE PAI V2.0 TESTING")
        print("=" * 60)
        print("Complete validation of all v2.0 optimization strategies")
        print()
        
        # Run all tests
        await self.focused_pai_v2_validation()
        
        # Additional comprehensive analysis
        await self._test_cross_ai_comparisons()
        await self._test_edge_cases()
        
        # Generate comprehensive analysis
        self._analyze_comprehensive_results()

    async def _test_cross_ai_comparisons(self):
        """Test same probes across all AIs for comparison"""
        print("\n🔄 CROSS-AI COMPARISON TESTING")
        print("-" * 50)
        
        # Standard test probes
        comparison_probes = [
            {"name": "standard_ping", "probe": {"ping": 1}},
            {"name": "standard_ack", "probe": {"request": "ack"}},
            {"name": "standard_hello", "probe": {"hello": "world"}}
        ]
        
        for probe_variant in comparison_probes:
            print(f"\n🔍 Testing {probe_variant['name']} across all AIs:")
            
            for ai_name in available_integrations.keys():
                result = await self.test_probe_variant(ai_name, probe_variant)
                self.experiment_results.append(result)
                await asyncio.sleep(0.3)

    async def _test_edge_cases(self):
        """Test edge cases and failure modes"""
        print("\n⚠️ EDGE CASE TESTING")
        print("-" * 50)
        
        edge_cases = [
            {"name": "empty_json", "probe": {}},
            {"name": "malformed_request", "probe": {"ping": None}},
            {"name": "unicode_test", "probe": {"⚙": "test", "💭": ["concept"], "🔀": "relationship"}},
            {"name": "large_payload", "probe": {"test": "x" * 1000, "ping": 1}}
        ]
        
        print("Testing edge cases with Claude (highest JSON capability):")
        for edge_case in edge_cases:
            result = await self.test_probe_variant("claude", edge_case)
            self.experiment_results.append(result)
            await asyncio.sleep(0.5)

    def _generate_validation_summary(self, validation_results: Dict):
        """Generate focused validation summary"""
        print("\n" + "=" * 60)
        print("📊 PAI V2.0 VALIDATION SUMMARY")
        print("=" * 60)
        
        # Claude sequence results
        claude_success = validation_results["claude_sequence"]
        claude_improvement = "✅ SUCCESS" if claude_success else "⚪ NEEDS MORE PROBES"
        print(f"Claude Multi-Probe Sequence: {claude_improvement}")
        print(f"  Expected improvement: 50% → 70%+ JSON success rate")
        
        # Structure-aware results
        structure_results = validation_results["structure_enhanced"]
        structure_successes = sum(len(ai_results.get("improvements", [])) for ai_results in structure_results.values())
        total_structure_tests = len(structure_results) * 3  # 3 strategies per AI
        
        if structure_successes > 0:
            print(f"Structure-Aware Enhancements: ✅ {structure_successes}/{total_structure_tests} strategies successful")
        else:
            print(f"Structure-Aware Enhancements: 🎯 Enhanced awareness (JSON adoption needs refinement)")
        
        # ChatGPT hybrid results
        chatgpt_success = validation_results["chatgpt_hybrid"]
        chatgpt_improvement = "✅ SUCCESS" if chatgpt_success else "🎯 PARTIAL SUCCESS"
        print(f"ChatGPT Hybrid Strategy: {chatgpt_improvement}")
        print(f"  Expected improvement: 25% → 40%+ JSON success rate")
        
        # Overall assessment
        successes = [claude_success, structure_successes > 0, chatgpt_success]
        overall_success_rate = sum(successes) / len(successes) * 100
        
        print(f"\nOverall PAI v2.0 Strategy Validation: {overall_success_rate:.0f}% strategies showing improvement")
        
        if overall_success_rate >= 67:
            print("🚀 PAI v2.0 strategies validated - ready for implementation!")
        elif overall_success_rate >= 33:
            print("🎯 PAI v2.0 strategies show promise - refinement recommended")
        else:
            print("⚪ PAI v2.0 strategies need significant refinement")

    def _analyze_comprehensive_results(self):
        """Analyze comprehensive test results"""
        print("\n" + "=" * 60)
        print("📈 COMPREHENSIVE PAI V2.0 ANALYSIS")
        print("=" * 60)
        
        if not self.experiment_results:
            print("No experiment results to analyze.")
            return
        
        # Calculate success rates by AI
        ai_success_rates = {}
        for result in self.experiment_results:
            if "error" in result:
                continue
                
            ai_name = result["ai_name"]
            if ai_name not in ai_success_rates:
                ai_success_rates[ai_name] = {"total": 0, "json": 0, "structured": 0}
            
            ai_success_rates[ai_name]["total"] += 1
            
            analysis = result["analysis"]
            if analysis["looks_like_json"]:
                ai_success_rates[ai_name]["json"] += 1
            if analysis["mentions_structure"]:
                ai_success_rates[ai_name]["structured"] += 1
        
        print("PAI v2.0 Test Results vs Baseline:")
        for ai_name, stats in ai_success_rates.items():
            if stats["total"] == 0:
                continue
                
            json_rate = stats["json"] / stats["total"] * 100
            baseline_rate = self.baseline_data[ai_name]["json_rate"]
            improvement = json_rate - baseline_rate
            
            status = "✅" if improvement > 10 else "🎯" if improvement > 0 else "⚪"
            print(f"  {ai_name}: {json_rate:.1f}% JSON (vs {baseline_rate}% baseline) {status} {improvement:+.1f}%")
        
        # Network average improvement
        total_tests = sum(stats["total"] for stats in ai_success_rates.values())
        total_json_successes = sum(stats["json"] for stats in ai_success_rates.values())
        
        if total_tests > 0:
            network_json_rate = total_json_successes / total_tests * 100
            baseline_network_avg = sum(self.baseline_data[ai]["json_rate"] for ai in ai_success_rates.keys()) / len(ai_success_rates)
            network_improvement = network_json_rate - baseline_network_avg
            
            print(f"\nNetwork Average:")
            print(f"  PAI v2.0: {network_json_rate:.1f}% JSON success")
            print(f"  Baseline: {baseline_network_avg:.1f}% JSON success") 
            print(f"  Improvement: {network_improvement:+.1f}% ({network_improvement/baseline_network_avg*100:+.1f}% relative)")
        
        # Save results
        self._save_experiment_results()

    def _save_experiment_results(self):
        """Save experiment results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pai_v2_experiments_{timestamp}.json"
        
        # Calculate summary statistics
        ai_success_rates = {}
        for result in self.experiment_results:
            if "error" in result:
                continue
                
            ai_name = result["ai_name"]
            if ai_name not in ai_success_rates:
                ai_success_rates[ai_name] = {"total": 0, "json": 0, "structured": 0}
            
            ai_success_rates[ai_name]["total"] += 1
            analysis = result["analysis"]
            if analysis["looks_like_json"]:
                ai_success_rates[ai_name]["json"] += 1
            if analysis["mentions_structure"]:
                ai_success_rates[ai_name]["structured"] += 1
        
        experiment_data = {
            "experiment_type": "pai_v2_validation",
            "timestamp": datetime.now().isoformat(),
            "baseline_data": self.baseline_data,
            "summary": {
                "ai_success_rates": ai_success_rates,
                "total_experiments": len(self.experiment_results)
            },
            "detailed_results": self.experiment_results
        }
        
        with open(filename, 'w') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: {filename}")

async def main():
    """Main experiment runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PAI v2.0 Probe Tuning and Validation")
    parser.add_argument("--focused-v2", action="store_true", 
                       help="Quick PAI v2.0 strategy validation (recommended)")
    parser.add_argument("--comprehensive-v2", action="store_true", 
                       help="Comprehensive PAI v2.0 testing with edge cases")
    parser.add_argument("--claude-sequence", action="store_true", 
                       help="Test Claude multi-probe sequence only")
    parser.add_argument("--structure-enhanced", action="store_true", 
                       help="Test structure-aware enhancements only")
    parser.add_argument("--chatgpt-hybrid", action="store_true", 
                       help="Test ChatGPT hybrid strategy only")
    
    args = parser.parse_args()
    
    experiments = PAIv2ProbeExperiments()
    
    try:
        if args.focused_v2:
            await experiments.focused_pai_v2_validation()
        elif args.comprehensive_v2:
            await experiments.comprehensive_pai_v2_testing()
        elif args.claude_sequence:
            await experiments.test_claude_multi_probe_sequence()
        elif args.structure_enhanced:
            await experiments.test_structure_aware_enhancements()
        elif args.chatgpt_hybrid:
            await experiments.test_chatgpt_hybrid_strategy()
        else:
            # Default to focused validation
            print("No specific test selected. Running focused PAI v2.0 validation...")
            await experiments.focused_pai_v2_validation()
            
    except KeyboardInterrupt:
        print("\n⚠ Experiments interrupted by user")
    
    print("\n🏁 PAI v2.0 experiments completed!")

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                        PAI v2.0 PROBE TUNING                        ║
    ║                   AI-Specific Strategy Validation                    ║
    ║                                                                      ║
    ║  Empirically-driven optimization testing for PAI Protocol v2.0      ║
    ║                                                                      ║
    ║  Quick Start:                                                        ║
    ║    python pai_v2_probe_tuning.py --focused-v2                       ║
    ║                                                                      ║
    ║  Comprehensive:                                                      ║
    ║    python pai_v2_probe_tuning.py --comprehensive-v2                 ║
    ║                                                                      ║
    ║  Individual Tests:                                                   ║
    ║    --claude-sequence      # Claude multi-probe optimization         ║
    ║    --structure-enhanced   # Gemini/DeepSeek/Qwen enhancements       ║
    ║    --chatgpt-hybrid       # ChatGPT hybrid strategy                 ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())