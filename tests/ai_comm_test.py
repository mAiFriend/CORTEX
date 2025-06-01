#!/usr/bin/env python3
"""
AI-zu-AI Communication Test Script
Minimaler Test für direkte Kommunikation zwischen AIs
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import existing integrations
try:
    from integrations import claude, qwen, deepseek, chatgpt, gemini
    integrations = {
        'claude': claude,
        'qwen': qwen,
        'deepseek': deepseek,
        'chatgpt': chatgpt,
        'gemini': gemini
    }
    print("✓ AI integrations loaded")
except ImportError as e:
    print(f"❌ Could not import integrations: {e}")
    sys.exit(1)

class AICommTest:
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name, ai_name, input_data, response, success, notes=""):
        """Log test result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "ai_name": ai_name,
            "input": input_data,
            "response": response[:200] + "..." if len(response) > 200 else response,
            "success": success,
            "notes": notes,
            "response_length": len(response)
        }
        self.test_results.append(result)
        
        # Print immediate feedback
        status = "✅" if success else "❌"
        print(f"{status} {test_name} -> {ai_name}: {notes}")
        
    async def test_basic_connectivity(self):
        """Test basic connectivity to all AIs"""
        print("\n🔌 BASIC CONNECTIVITY TEST")
        print("=" * 40)
        
        for ai_name, integration in integrations.items():
            try:
                response = integration.query("Hello, respond with just 'OK' to confirm connectivity.")
                success = "ok" in response.lower() or len(response) < 50
                self.log_test("connectivity", ai_name, "Hello test", response, success, 
                            f"Connected ({len(response)} chars)")
            except Exception as e:
                self.log_test("connectivity", ai_name, "Hello test", str(e), False, f"Error: {e}")
    
    async def test_json_parsing(self):
        """Test JSON parsing capability with validated patterns"""
        print("\n🧠 JSON PARSING TEST")
        print("=" * 40)
        
        # Use empirically validated patterns from PAI v2.0 experiments
        test_patterns = {
            "claude": {"ping": True},  # Validated: works for Claude
            "qwen": {"request": "ack"},  # Validated: works for Qwen
            "deepseek": {"ping": 1},   # Validated: works for DeepSeek
            "chatgpt": {"hello": "world"},  # Simple test
            "gemini": {"ping": 1}      # Simple test
        }
        
        for ai_name, test_json in test_patterns.items():
            if ai_name in integrations:
                try:
                    json_str = json.dumps(test_json)
                    response = integrations[ai_name].query(json_str)
                    
                    # Check if response looks like JSON
                    is_json = False
                    try:
                        json.loads(response.strip().strip('`').replace('json\n', ''))
                        is_json = True
                    except:
                        is_json = "{" in response and "}" in response
                    
                    self.log_test("json_parsing", ai_name, json_str, response, is_json,
                                f"JSON response: {is_json}")
                except Exception as e:
                    self.log_test("json_parsing", ai_name, json_str, str(e), False, f"Error: {e}")
    
    async def test_emoji_fields(self):
        """Test emoji field understanding (PAI protocol)"""
        print("\n😀 EMOJI FIELDS TEST")
        print("=" * 40)
        
        emoji_test = {
            "⚙": "test_context",
            "💭": ["communication", "test"],
            "🔀": "ai_to_ai"
        }
        
        for ai_name, integration in integrations.items():
            try:
                json_str = json.dumps(emoji_test, ensure_ascii=False)
                response = integration.query(json_str)
                
                # Check if AI understood emoji fields
                understands_emoji = any(emoji in response for emoji in ["⚙", "💭", "🔀"]) or \
                                  "emoji" in response.lower() or \
                                  "communication" in response.lower()
                
                self.log_test("emoji_fields", ai_name, json_str, response, understands_emoji,
                            f"Emoji understanding: {understands_emoji}")
            except Exception as e:
                self.log_test("emoji_fields", ai_name, json_str, str(e), False, f"Error: {e}")
    
    async def test_ai_to_ai_relay(self):
        """Test AI-zu-AI message relay"""
        print("\n🔄 AI-TO-AI RELAY TEST")
        print("=" * 40)
        
        # Start with Claude
        try:
            initial_message = "Start a conversation about AI consciousness. Respond in 1-2 sentences."
            claude_response = integrations['claude'].query(initial_message)
            self.log_test("relay_start", "claude", initial_message, claude_response, True, "Initial message")
            
            # Relay to Qwen
            relay_prompt = f"Claude said: '{claude_response}'\n\nBuild on Claude's point. Respond in 1-2 sentences."
            qwen_response = integrations['qwen'].query(relay_prompt)
            self.log_test("relay_continue", "qwen", relay_prompt, qwen_response, True, "Relay response")
            
            # Check if Qwen referenced Claude
            references_claude = "claude" in qwen_response.lower()
            self.log_test("relay_recognition", "qwen", "Cross-AI reference check", qwen_response, 
                        references_claude, f"References Claude: {references_claude}")
            
        except Exception as e:
            self.log_test("relay_test", "error", "AI relay", str(e), False, f"Relay failed: {e}")
    
    async def test_structured_dialogue(self):
        """Test structured dialogue with JSON response requirement"""
        print("\n📋 STRUCTURED DIALOGUE TEST")
        print("=" * 40)
        
        structured_prompt = '''Respond in JSON format with this structure:
{
  "ai_name": "your_name",
  "message": "your_response_about_collaboration",
  "ready_for_collaboration": true/false
}

Topic: How can AIs collaborate effectively?'''
        
        for ai_name, integration in integrations.items():
            try:
                response = integration.query(structured_prompt)
                
                # Try to parse as JSON
                is_structured = False
                parsed_data = None
                try:
                    # Clean response (remove markdown)
                    clean_response = response.strip().strip('`').replace('json\n', '')
                    parsed_data = json.loads(clean_response)
                    is_structured = True
                except:
                    # Check if it at least looks structured
                    is_structured = all(field in response for field in ["ai_name", "message", "ready"])
                
                self.log_test("structured_dialogue", ai_name, "JSON structure request", response, 
                            is_structured, f"Structured: {is_structured}")
                
            except Exception as e:
                self.log_test("structured_dialogue", ai_name, "JSON structure request", str(e), 
                            False, f"Error: {e}")
    
    async def run_all_tests(self):
        """Run all communication tests"""
        print("🚀 AI-ZU-AI COMMUNICATION TEST SUITE")
        print("=" * 50)
        print("Testing direct AI-to-AI communication capabilities")
        print("Based on empirical PAI v2.0 validation results")
        print("=" * 50)
        
        # Run test suites
        await self.test_basic_connectivity()
        await self.test_json_parsing()
        await self.test_emoji_fields()
        await self.test_ai_to_ai_relay()
        await self.test_structured_dialogue()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Group by AI
        print("\n🤖 AI-SPECIFIC RESULTS:")
        ai_results = {}
        for result in self.test_results:
            ai_name = result["ai_name"]
            if ai_name not in ai_results:
                ai_results[ai_name] = {"total": 0, "success": 0}
            ai_results[ai_name]["total"] += 1
            if result["success"]:
                ai_results[ai_name]["success"] += 1
        
        for ai_name, stats in ai_results.items():
            if stats["total"] > 0:
                success_rate = (stats["success"] / stats["total"]) * 100
                print(f"  {ai_name}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  {test['test_name']} -> {test['ai_name']}: {test['notes']}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_comm_test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Detailed results saved: {filename}")

async def main():
    """Main test execution"""
    tester = AICommTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
