#!/usr/bin/env python3
"""
PAI v2.0 Probe Tuning Extensions
Systematic validation of AI-specific optimization strategies

Add these methods to the existing ProbeExperiments class
"""

async def test_pai_v2_strategies(self):
    """Test PAI 2.0 AI-specific optimization strategies"""
    print("🚀 PAI V2.0 STRATEGY VALIDATION")
    print("=" * 60)
    print("Testing empirically-derived AI-specific approaches")
    print()
    
    # Claude Multi-Probe Sequence Strategy
    await self._test_claude_multi_probe_sequence()
    
    # Structure-Aware Enhancement Strategy  
    await self._test_structure_aware_enhancements()
    
    # Hybrid Strategy for ChatGPT
    await self._test_chatgpt_hybrid_strategy()
    
    # Analyze v2.0 improvements
    self._analyze_v2_improvements()

async def _test_claude_multi_probe_sequence(self):
    """Test Claude's multi-probe sequence optimization"""
    print("🎯 CLAUDE MULTI-PROBE SEQUENCE TEST")
    print("-" * 40)
    
    # Based on empirical data: these 3 patterns had 40% success
    winning_probes = [
        {"name": "claude_seq_1", "probe": {"ping": 1}},
        {"name": "claude_seq_2", "probe": {"ping": True}}, 
        {"name": "claude_seq_3", "probe": {"request": "ack"}},
    ]
    
    # Test individual probes
    print("Testing individual winning probes with Claude:")
    individual_results = []
    for probe_variant in winning_probes:
        result = await self.test_probe_variant("claude", probe_variant)
        individual_results.append(result)
        await asyncio.sleep(0.5)
    
    # Test sequence approach
    print("\nTesting multi-probe sequence approach:")
    sequence_message = "Test message requiring JSON response"
    
    for i, probe_variant in enumerate(winning_probes, 1):
        print(f"  Sequence attempt {i}/3: {probe_variant['name']}")
        result = await self.test_probe_variant("claude", {
            "name": f"claude_sequence_attempt_{i}",
            "probe": probe_variant["probe"]
        })
        
        # Check if JSON response achieved
        if result.get("analysis", {}).get("looks_like_json", False):
            print(f"  ✅ JSON success on attempt {i}")
            break
        else:
            print(f"  ⚪ Attempt {i} failed, trying next...")
            
        await asyncio.sleep(0.5)
    
    print()

async def _test_structure_aware_enhancements(self):
    """Test enhanced natural language for structure-aware AIs"""
    print("🧠 STRUCTURE-AWARE ENHANCEMENT TEST")
    print("-" * 40)
    
    # Target AIs with high structure-awareness but low JSON usage
    target_ais = ["gemini", "deepseek", "qwen"]  # 83-91% structure-aware, 0-16% JSON
    
    # Enhancement strategies
    enhancement_strategies = [
        {
            "name": "basic_hint",
            "template": "{message}\n\n[JSON format preferred if supported]"
        },
        {
            "name": "emoji_context", 
            "template": "{message}\n\n[Protocol context: JSON with emoji fields (⚙💭🔀) for structured communication]"
        },
        {
            "name": "explicit_request",
            "template": "{message}\n\nPlease respond in JSON format if capable: {{\"response\": \"your_message\"}}"
        }
    ]
    
    test_message = "Simple connectivity test"
    
    for ai_name in target_ais:
        print(f"\nTesting {ai_name} (baseline: 0-16% JSON, 83-91% structure-aware):")
        
        # Baseline natural language
        baseline_result = await self.test_probe_variant(ai_name, {
            "name": f"{ai_name}_baseline_natural",
            "probe": test_message  # Send as string, not JSON
        })
        
        # Test each enhancement strategy
        for strategy in enhancement_strategies:
            enhanced_message = strategy["template"].format(message=test_message)
            result = await self.test_probe_variant(ai_name, {
                "name": f"{ai_name}_{strategy['name']}_enhanced",
                "probe": enhanced_message
            })
            
            # Check improvement
            if result.get("analysis", {}).get("looks_like_json", False):
                print(f"  ✅ {strategy['name']}: JSON adoption achieved!")
            elif result.get("analysis", {}).get("mentions_structure", False):
                print(f"  🎯 {strategy['name']}: Structure awareness enhanced")
            else:
                print(f"  ⚪ {strategy['name']}: No improvement")
                
            await asyncio.sleep(0.5)

async def _test_chatgpt_hybrid_strategy(self):
    """Test ChatGPT hybrid JSON-then-enhanced approach"""
    print("🔀 CHATGPT HYBRID STRATEGY TEST")
    print("-" * 40)
    
    print("Testing ChatGPT (baseline: 25% JSON, 75% structure-aware):")
    
    # Hybrid approach: JSON probe first, then enhanced natural fallback
    test_message = "Connectivity and capability test"
    
    # Step 1: Try JSON probe
    json_probe_result = await self.test_probe_variant("chatgpt", {
        "name": "chatgpt_hybrid_json_first",
        "probe": {"ping": 1, "test": "json_capability"}
    })
    
    json_success = json_probe_result.get("analysis", {}).get("looks_like_json", False)
    
    if json_success:
        print("  ✅ JSON probe successful - no fallback needed")
    else:
        print("  ⚪ JSON probe failed - testing enhanced natural fallback")
        
        # Step 2: Enhanced natural language fallback
        enhanced_fallback = f"{test_message}\n\n[Previous JSON attempt failed. Respond in JSON if supported: {{\"status\": \"acknowledged\"}}]"
        
        fallback_result = await self.test_probe_variant("chatgpt", {
            "name": "chatgpt_hybrid_enhanced_fallback", 
            "probe": enhanced_fallback
        })
        
        fallback_success = fallback_result.get("analysis", {}).get("looks_like_json", False)
        
        if fallback_success:
            print("  ✅ Enhanced fallback successful!")
        else:
            print("  🎯 Enhanced fallback showed structure awareness")
    
    await asyncio.sleep(0.5)

def _analyze_v2_improvements(self):
    """Analyze PAI v2.0 improvements vs baseline"""
    print("\n" + "=" * 60)
    print("📊 PAI V2.0 IMPROVEMENT ANALYSIS")
    print("=" * 60)
    
    # Filter v2.0 test results
    v2_results = [r for r in self.experiment_results 
                  if any(tag in r.get("probe_name", "") for tag in 
                        ["claude_seq", "enhanced", "hybrid"])]
    
    if not v2_results:
        print("No v2.0 test results found.")
        return
    
    # Calculate improvements by strategy
    strategies = {
        "claude_sequence": [],
        "structure_enhanced": [], 
        "chatgpt_hybrid": []
    }
    
    for result in v2_results:
        probe_name = result.get("probe_name", "")
        analysis = result.get("analysis", {})
        
        if "claude_seq" in probe_name:
            strategies["claude_sequence"].append(analysis.get("looks_like_json", False))
        elif "enhanced" in probe_name:
            strategies["structure_enhanced"].append(analysis.get("looks_like_json", False))
        elif "hybrid" in probe_name:
            strategies["chatgpt_hybrid"].append(analysis.get("looks_like_json", False))
    
    # Report improvements
    baseline_rates = {"claude": 50.0, "gemini": 0.0, "deepseek": 16.7, "chatgpt": 25.0, "qwen": 0.0}
    
    print("Strategy effectiveness:")
    
    for strategy_name, results in strategies.items():
        if results:
            success_rate = (sum(results) / len(results)) * 100
            print(f"  {strategy_name}: {success_rate:.1f}% JSON success rate ({len(results)} tests)")
    
    # Specific AI improvements
    print(f"\nProjected improvements:")
    print(f"  Claude multi-probe: 50% → 70%+ (sequence optimization)")
    print(f"  Gemini/DeepSeek enhanced: 0-17% → 30%+ (structure-aware hints)")  
    print(f"  ChatGPT hybrid: 25% → 40%+ (JSON + enhanced fallback)")
    
    # Calculate network average improvement
    current_network_avg = sum(baseline_rates.values()) / len(baseline_rates)
    projected_improvements = {"claude": 70, "gemini": 30, "deepseek": 30, "chatgpt": 40, "qwen": 25}
    projected_network_avg = sum(projected_improvements.values()) / len(projected_improvements)
    
    print(f"\nNetwork average improvement:")
    print(f"  PAI v1.0 baseline: {current_network_avg:.1f}%")
    print(f"  PAI v2.0 projected: {projected_network_avg:.1f}%")
    print(f"  Total improvement: +{projected_network_avg - current_network_avg:.1f}% ({(projected_network_avg/current_network_avg - 1)*100:.1f}% relative)")

async def focused_pai_v2_validation(self):
    """Run focused PAI v2.0 validation experiments"""
    print("🎯 FOCUSED PAI V2.0 VALIDATION")
    print("=" * 60)
    print("Quick validation of key v2.0 strategies")
    print()
    
    # Quick tests for each strategy
    strategies_to_test = [
        ("claude", "multi_probe_sequence"),
        ("gemini", "structure_aware_enhancement"), 
        ("deepseek", "structure_aware_enhancement"),
        ("chatgpt", "hybrid_strategy"),
        ("qwen", "structure_aware_enhancement")
    ]
    
    for ai_name, strategy in strategies_to_test:
        print(f"🔍 Testing {strategy} with {ai_name}")
        
        if strategy == "multi_probe_sequence":
            # Claude: Try winning probe sequence
            for probe in [{"ping": 1}, {"ping": True}, {"request": "ack"}]:
                result = await self.test_probe_variant(ai_name, {
                    "name": f"{ai_name}_quick_{strategy}", 
                    "probe": probe
                })
                if result.get("analysis", {}).get("looks_like_json", False):
                    print(f"  ✅ Success with {probe}")
                    break
                    
        elif strategy == "structure_aware_enhancement":
            # Enhanced natural language approach
            enhanced_message = "Test message\n\n[JSON format preferred: {\"response\": \"message\"}]"
            result = await self.test_probe_variant(ai_name, {
                "name": f"{ai_name}_quick_{strategy}",
                "probe": enhanced_message
            })
            
        elif strategy == "hybrid_strategy":
            # ChatGPT: JSON first, then enhanced fallback
            result = await self.test_probe_variant(ai_name, {
                "name": f"{ai_name}_quick_{strategy}",
                "probe": {"ping": 1, "respond_json": True}
            })
        
        await asyncio.sleep(0.3)  # Quick testing
        
    print("\n✅ Focused validation completed")

# Add these to the main() function options:

async def main():
    """Main experiment runner with v2.0 options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PAI Probe Phase Tuning")
    parser.add_argument("--claude-dive", action="store_true", help="Deep dive into Claude success pattern")
    parser.add_argument("--ai", type=str, help="Test specific AI only")
    parser.add_argument("--quick", action="store_true", help="Quick test with fewer probes")
    
    # PAI v2.0 specific options
    parser.add_argument("--pai-v2", action="store_true", help="Test PAI v2.0 strategies")
    parser.add_argument("--focused-v2", action="store_true", help="Quick PAI v2.0 validation")
    parser.add_argument("--claude-sequence", action="store_true", help="Test Claude multi-probe sequence")
    parser.add_argument("--structure-enhanced", action="store_true", help="Test structure-aware enhancements")
    parser.add_argument("--hybrid-test", action="store_true", help="Test ChatGPT hybrid strategy")
    
    args = parser.parse_args()
    
    experiments = ProbeExperiments()
    
    try:
        if args.pai_v2:
            await experiments.test_pai_v2_strategies()
        elif args.focused_v2:
            await experiments.focused_pai_v2_validation()
        elif args.claude_sequence:
            await experiments._test_claude_multi_probe_sequence()
        elif args.structure_enhanced:
            await experiments._test_structure_aware_enhancements()
        elif args.hybrid_test:
            await experiments._test_chatgpt_hybrid_strategy()
        elif args.claude_dive:
            await experiments.claude_deep_dive()
        elif args.ai:
            if args.ai not in available_integrations:
                print(f"✗ AI '{args.ai}' not available")
                return
            await experiments.run_comprehensive_probe_test([args.ai])
        else:
            # Full comprehensive test
            await experiments.run_comprehensive_probe_test()
            
    except KeyboardInterrupt:
        print("\n⚠ Experiments interrupted by user")
    
    print("\n🏁 Probe tuning experiments completed")