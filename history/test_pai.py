#!/usr/bin/env python3
"""
PAI Protocol Standalone Test Suite
Tests PAI functionality with real AI integrations before PowerTalk integration

Usage:
    python test_pai.py                    # Interactive test mode
    python test_pai.py --auto             # Automated test suite
    python test_pai.py --ai claude        # Test specific AI
"""

import asyncio
import argparse
import json
import sys
import os
from datetime import datetime
from typing import Dict, List

# Import PAI protocol
try:
    from pai import PAIProtocol, pai_communicate, PAIResponse
    print("✓ PAI Protocol imported successfully")
except ImportError as e:
    print(f"✗ Failed to import PAI: {e}")
    print("Make sure pai.py is in the same directory")
    sys.exit(1)

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
    print(f"⚠ Some integrations unavailable: {e}")
    available_integrations = {}

class PAITester:
    def __init__(self):
        self.pai = PAIProtocol(enable_logging=True)
        self.test_results = []
        
    async def test_ai_integration(self, ai_name: str, test_message: str) -> Dict:
        """Test PAI protocol with specific AI integration"""
        if ai_name not in available_integrations:
            return {
                "ai_name": ai_name,
                "status": "unavailable",
                "error": f"Integration for {ai_name} not found"
            }
        
        print(f"\n🧠 Testing PAI with {ai_name.upper()}")
        print("─" * 50)
        
        try:
            integration = available_integrations[ai_name]
            
            # Create AI caller function
            async def ai_caller(message: str) -> str:
                return integration.query(message)
            
            # Test PAI communication
            start_time = datetime.now()
            response = await self.pai.communicate(
                ai_caller=ai_caller,
                ai_name=ai_name,
                message=test_message,
                context="PAI standalone test"
            )
            end_time = datetime.now()
            
            # Calculate response time
            response_time = (end_time - start_time).total_seconds()
            
            # Analyze response
            result = {
                "ai_name": ai_name,
                "status": "success" if response.success else "failed",
                "protocol_used": response.protocol_used,
                "response_time": response_time,
                "response_length": len(str(response.content)),
                "timestamp": response.timestamp,
                "metadata": response.metadata
            }
            
            # Show results
            print(f"Status: {'✓' if response.success else '✗'} {response.protocol_used}")
            print(f"Response time: {response_time:.2f}s")
            print(f"Response length: {len(str(response.content))} chars")
            
            if response.success:
                print(f"Preview: {str(response.content)[:200]}...")
                
                # Try to detect if AI understood structured format
                if self._analyze_structured_understanding(response.content):
                    result["structured_understanding"] = True
                    print("✓ AI shows structured understanding")
                else:
                    result["structured_understanding"] = False
                    print("○ AI used natural language response")
            else:
                print(f"Error: {response.content}")
                result["error"] = response.content
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            error_result = {
                "ai_name": ai_name,
                "status": "error", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(error_result)
            print(f"✗ Error testing {ai_name}: {e}")
            return error_result
    
    def _analyze_structured_understanding(self, response_content: str) -> bool:
        """Analyze if AI response shows understanding of structured format"""
        content_str = str(response_content).lower()
        
        # Check for JSON-like structures
        json_indicators = ["{", "}", "[", "]", "ping", "ack"]
        
        # Check for emoji field references
        emoji_indicators = ["⚙", "💭", "🔀", "emoji", "json", "structured"]
        
        # Check for protocol understanding
        protocol_indicators = ["protocol", "format", "ping", "probe", "handshake"]
        
        json_score = sum(1 for indicator in json_indicators if indicator in content_str)
        emoji_score = sum(1 for indicator in emoji_indicators if indicator in content_str)
        protocol_score = sum(1 for indicator in protocol_indicators if indicator in content_str)
        
        return (json_score >= 2) or (emoji_score >= 1) or (protocol_score >= 2)
    
    async def run_comprehensive_test(self, test_messages: List[str] = None):
        """Run comprehensive test across all available AIs"""
        if test_messages is None:
            test_messages = [
                "Hello, this is a test of structured communication capabilities.",
                "Can you process JSON data with emoji fields?", 
                "I'm testing a new AI-to-AI communication protocol called PAI."
            ]
        
        print("🚀 PAI PROTOCOL COMPREHENSIVE TEST")
        print("=" * 60)
        print(f"Testing {len(available_integrations)} AI integrations")
        print(f"Using {len(test_messages)} test messages")
        print()
        
        # Test each AI with each message
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 TEST MESSAGE {i}: {message}")
            print("-" * 60)
            
            for ai_name in available_integrations.keys():
                await self.test_ai_integration(ai_name, message)
                await asyncio.sleep(1)  # Rate limiting
        
        # Generate summary report
        self.generate_summary_report()
    
    async def interactive_test(self):
        """Interactive test mode - user selects AI and message"""
        print("🎯 PAI PROTOCOL INTERACTIVE TEST")
        print("=" * 40)
        
        # Select AI
        print("\nAvailable AIs:")
        ai_list = list(available_integrations.keys())
        for i, ai_name in enumerate(ai_list, 1):
            print(f"  [{i}] {ai_name}")
        
        while True:
            try:
                choice = input(f"\nSelect AI (1-{len(ai_list)}): ")
                ai_index = int(choice) - 1
                if 0 <= ai_index < len(ai_list):
                    selected_ai = ai_list[ai_index]
                    break
                else:
                    print("Invalid choice, try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Get test message
        message = input("\nEnter test message (or press Enter for default): ").strip()
        if not message:
            message = "Hello! I'm testing the PAI protocol for structured AI communication."
        
        # Run test
        print(f"\n🧪 Testing PAI with {selected_ai}")
        result = await self.test_ai_integration(selected_ai, message)
        
        # Ask for another test
        if input("\nRun another test? (y/n): ").lower().startswith('y'):
            await self.interactive_test()
    
    def generate_summary_report(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 PAI PROTOCOL TEST SUMMARY")
        print("=" * 60)
        
        if not self.test_results:
            print("No test results available.")
            return
        
        # Overall statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["status"] == "success"])
        structured_understanding = len([r for r in self.test_results if r.get("structured_understanding", False)])
        
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"Structured understanding: {structured_understanding}/{successful_tests} ({structured_understanding/max(successful_tests,1)*100:.1f}%)")
        
        # PAI protocol statistics
        pai_stats = self.pai.get_statistics()
        print(f"\nPAI Protocol Usage:")
        if pai_stats.get("total_communications", 0) > 0:
            print(f"  Structured success rate: {pai_stats['structured_success_rate']*100:.1f}%")
            print(f"  Natural fallback rate: {pai_stats['natural_fallback_rate']*100:.1f}%")
            print(f"  Probe failure rate: {pai_stats['probe_failure_rate']*100:.1f}%")
        else:
            print("  No communications recorded")
        
        # Per-AI results
        print(f"\nPer-AI Results:")
        ai_results = {}
        for result in self.test_results:
            ai_name = result["ai_name"]
            if ai_name not in ai_results:
                ai_results[ai_name] = {"total": 0, "success": 0, "structured": 0}
            
            ai_results[ai_name]["total"] += 1
            if result["status"] == "success":
                ai_results[ai_name]["success"] += 1
                if result.get("structured_understanding", False):
                    ai_results[ai_name]["structured"] += 1
        
        for ai_name, stats in ai_results.items():
            success_rate = stats["success"] / stats["total"] * 100
            structured_rate = stats["structured"] / max(stats["success"], 1) * 100
            print(f"  {ai_name}: {success_rate:.1f}% success, {structured_rate:.1f}% structured")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pai_test_results_{timestamp}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "structured_understanding": structured_understanding,
                "pai_statistics": pai_stats
            },
            "per_ai_results": ai_results,
            "detailed_results": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: {filename}")

async def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="PAI Protocol Standalone Test")
    parser.add_argument("--auto", action="store_true", help="Run automated test suite")
    parser.add_argument("--ai", type=str, help="Test specific AI only")
    parser.add_argument("--message", type=str, help="Custom test message")
    
    args = parser.parse_args()
    
    if not available_integrations:
        print("✗ No AI integrations available. Cannot run tests.")
        print("Make sure integrations/ folder exists with working AI modules.")
        return
    
    tester = PAITester()
    
    try:
        if args.auto:
            # Automated comprehensive test
            test_messages = []
            if args.message:
                test_messages = [args.message]
            
            await tester.run_comprehensive_test(test_messages)
            
        elif args.ai:
            # Test specific AI
            if args.ai not in available_integrations:
                print(f"✗ AI '{args.ai}' not available. Choose from: {', '.join(available_integrations.keys())}")
                return
            
            message = args.message or "Hello! Testing PAI protocol with structured communication."
            await tester.test_ai_integration(args.ai, message)
            tester.generate_summary_report()
            
        else:
            # Interactive mode
            await tester.interactive_test()
            
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
    
    print("\n🏁 PAI testing completed")

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                         PAI PROTOCOL TESTER                         ║
    ║                    Standalone Test Suite v1.0                       ║
    ║                                                                      ║
    ║  Tests PAI (Probe, Accept, Inquire) protocol with real AI systems   ║
    ║                                                                      ║
    ║  Usage:                                                              ║
    ║    python test_pai.py                    # Interactive mode          ║
    ║    python test_pai.py --auto             # Automated test suite      ║
    ║    python test_pai.py --ai claude        # Test specific AI          ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())