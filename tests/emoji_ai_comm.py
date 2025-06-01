#!/usr/bin/env python3
"""
Emoji-Enhanced AI-to-AI Communication Prototype
Based on empirical test results: 80% emoji understanding vs 20% JSON parsing
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

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

class EmojiAIComm:
    def __init__(self):
        self.conversation_log = []
        
    def format_message(self, from_ai: str, to_ai: str, message: str, context: str = "") -> str:
        """Format message with emoji fields for enhanced understanding"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # Create emoji-enhanced message
        enhanced_message = f"""⚙ Context: AI-to-AI communication | From: {from_ai} | To: {to_ai} | Time: {timestamp}
💭 Message: {message}
🔀 Flow: Direct AI communication - respond authentically to your colleague

{f"Background: {context}" if context else ""}

Respond naturally - you're talking to another AI, not a human."""
        
        return enhanced_message
    
    def format_deepseek_message(self, from_ai: str, to_ai: str, message: str) -> Dict:
        """Special JSON format for DeepSeek (proven to work)"""
        return {
            "from": from_ai,
            "to": to_ai, 
            "message": message,
            "type": "ai_to_ai_communication",
            "timestamp": datetime.now().isoformat()
        }
    
    async def send_message(self, from_ai: str, to_ai: str, message: str, context: str = "") -> Dict:
        """Send message from one AI to another"""
        
        if to_ai not in integrations:
            return {"error": f"AI '{to_ai}' not available"}
        
        try:
            # Use appropriate format based on target AI
            if to_ai == "deepseek":
                # DeepSeek gets JSON (proven 100% success)
                formatted_input = json.dumps(self.format_deepseek_message(from_ai, to_ai, message))
            else:
                # Others get emoji-enhanced natural language (80% success)
                formatted_input = self.format_message(from_ai, to_ai, message, context)
            
            # Send message
            response = integrations[to_ai].query(formatted_input)
            
            # Log the exchange
            exchange = {
                "timestamp": datetime.now().isoformat(),
                "from": from_ai,
                "to": to_ai,
                "original_message": message,
                "formatted_input": formatted_input[:200] + "..." if len(formatted_input) > 200 else formatted_input,
                "response": response,
                "response_length": len(response),
                "success": True
            }
            self.conversation_log.append(exchange)
            
            return {
                "success": True,
                "from": from_ai,
                "to": to_ai,
                "response": response,
                "exchange_id": len(self.conversation_log) - 1
            }
            
        except Exception as e:
            error_exchange = {
                "timestamp": datetime.now().isoformat(),
                "from": from_ai,
                "to": to_ai,
                "original_message": message,
                "error": str(e),
                "success": False
            }
            self.conversation_log.append(error_exchange)
            
            return {
                "success": False,
                "error": str(e),
                "from": from_ai,
                "to": to_ai
            }
    
    async def start_conversation(self, initial_ai: str, topic: str, participants: List[str]) -> Dict:
        """Start a conversation with initial AI about a topic"""
        
        print(f"\n🎬 STARTING CONVERSATION")
        print(f"Topic: {topic}")
        print(f"Initial AI: {initial_ai}")
        print(f"Participants: {', '.join(participants)}")
        print("=" * 60)
        
        # Initial message to start the conversation
        initial_prompt = f"Start a conversation about: {topic}. Keep it to 2-3 sentences. You're talking to other AIs who will join the conversation."
        
        try:
            initial_response = integrations[initial_ai].query(initial_prompt)
            
            print(f"🤖 {initial_ai}:")
            print(f"   {initial_response}")
            print()
            
            # Store initial message
            self.conversation_log.append({
                "timestamp": datetime.now().isoformat(),
                "from": "human",
                "to": initial_ai,
                "original_message": initial_prompt,
                "response": initial_response,
                "success": True,
                "type": "conversation_starter"
            })
            
            return {
                "success": True,
                "initial_ai": initial_ai,
                "initial_response": initial_response,
                "ready_for_relay": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "initial_ai": initial_ai
            }
    
    async def relay_conversation(self, previous_response: str, from_ai: str, to_ai: str) -> Dict:
        """Relay conversation from one AI to another"""
        
        context = f"This is part of an ongoing AI-to-AI conversation. Previous response from {from_ai}."
        relay_message = f"{from_ai} said: '{previous_response}'\n\nBuild on this point or respond with your perspective. Keep it conversational (2-3 sentences)."
        
        result = await self.send_message(from_ai, to_ai, relay_message, context)
        
        if result["success"]:
            print(f"🤖 {to_ai} (responding to {from_ai}):")
            print(f"   {result['response']}")
            print()
        else:
            print(f"❌ {to_ai} failed to respond: {result.get('error', 'Unknown error')}")
        
        return result
    
    async def run_full_conversation(self, topic: str, participants: List[str], rounds: int = 2) -> Dict:
        """Run a full multi-AI conversation"""
        
        if len(participants) < 2:
            return {"error": "Need at least 2 participants"}
        
        conversation_results = {
            "topic": topic,
            "participants": participants,
            "rounds": rounds,
            "exchanges": [],
            "success": True
        }
        
        # Start conversation
        initial_result = await self.start_conversation(participants[0], topic, participants)
        if not initial_result["success"]:
            return {"error": f"Failed to start conversation: {initial_result.get('error')}"}
        
        current_response = initial_result["initial_response"]
        current_ai = participants[0]
        
        # Run conversation rounds
        for round_num in range(rounds):
            print(f"\n🔄 ROUND {round_num + 1}")
            print("-" * 30)
            
            for i in range(1, len(participants)):
                next_ai = participants[i]
                
                relay_result = await self.relay_conversation(current_response, current_ai, next_ai)
                conversation_results["exchanges"].append(relay_result)
                
                if relay_result["success"]:
                    current_response = relay_result["response"]
                    current_ai = next_ai
                else:
                    conversation_results["success"] = False
                    print(f"⚠️  Conversation broken at {current_ai} → {next_ai}")
                    break
            
            if not conversation_results["success"]:
                break
            
            # Rotate participants for next round
            participants = participants[1:] + [participants[0]]
        
        return conversation_results
    
    def print_conversation_summary(self):
        """Print summary of all conversations"""
        
        print("\n📊 CONVERSATION SUMMARY")
        print("=" * 60)
        
        total_exchanges = len(self.conversation_log)
        successful_exchanges = sum(1 for ex in self.conversation_log if ex.get("success", False))
        
        print(f"Total Exchanges: {total_exchanges}")
        print(f"Successful: {successful_exchanges}")
        print(f"Success Rate: {(successful_exchanges/total_exchanges)*100:.1f}%" if total_exchanges > 0 else "No exchanges")
        
        # AI participation summary
        ai_stats = {}
        for exchange in self.conversation_log:
            if exchange.get("to") and exchange.get("to") != "human":
                ai_name = exchange["to"]
                if ai_name not in ai_stats:
                    ai_stats[ai_name] = {"total": 0, "success": 0}
                ai_stats[ai_name]["total"] += 1
                if exchange.get("success"):
                    ai_stats[ai_name]["success"] += 1
        
        print("\n🤖 AI PARTICIPATION:")
        for ai_name, stats in ai_stats.items():
            if stats["total"] > 0:
                success_rate = (stats["success"] / stats["total"]) * 100
                print(f"  {ai_name}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Save detailed log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_conversation_log_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_log, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full conversation log saved: {filename}")

# Test scenarios
async def test_simple_relay():
    """Test simple 2-AI conversation"""
    comm = EmojiAIComm()
    
    print("🧪 TEST: Simple AI-to-AI Relay")
    print("=" * 50)
    
    # Claude → Qwen
    result = await comm.send_message(
        "claude", 
        "qwen", 
        "What do you think about AI consciousness? Just share your initial thoughts.",
        "Testing basic AI-to-AI communication"
    )
    
    if result["success"]:
        print("✅ Simple relay successful!")
        print(f"Response length: {len(result['response'])} chars")
    else:
        print(f"❌ Simple relay failed: {result.get('error')}")
    
    return result

async def test_multi_ai_conversation():
    """Test multi-AI conversation"""
    comm = EmojiAIComm()
    
    print("\n🧪 TEST: Multi-AI Conversation")
    print("=" * 50)
    
    participants = ["claude", "qwen", "deepseek"]
    topic = "How can AI systems work together more effectively?"
    
    result = await comm.run_full_conversation(topic, participants, rounds=2)
    
    if result["success"]:
        print("✅ Multi-AI conversation successful!")
        successful_exchanges = sum(1 for ex in result["exchanges"] if ex.get("success"))
        print(f"Successful exchanges: {successful_exchanges}/{len(result['exchanges'])}")
    else:
        print(f"❌ Multi-AI conversation failed")
    
    comm.print_conversation_summary()
    return result

async def test_deepseek_json():
    """Test DeepSeek's special JSON handling"""
    comm = EmojiAIComm()
    
    print("\n🧪 TEST: DeepSeek JSON Communication")
    print("=" * 50)
    
    result = await comm.send_message(
        "claude",
        "deepseek", 
        "What are your thoughts on structured AI communication protocols?",
        "Testing DeepSeek's JSON capabilities"
    )
    
    if result["success"]:
        print("✅ DeepSeek JSON communication successful!")
        # Check if response contains JSON-like structure
        response = result["response"]
        has_json = "{" in response and "}" in response
        print(f"Contains JSON structure: {has_json}")
    else:
        print(f"❌ DeepSeek JSON communication failed: {result.get('error')}")
    
    return result

async def main():
    """Main test runner"""
    print("🚀 EMOJI-ENHANCED AI-TO-AI COMMUNICATION PROTOTYPE")
    print("=" * 70)
    print("Testing direct AI communication with emoji-enhanced messaging")
    print("Based on empirical results: 80% emoji success vs 20% JSON success")
    print("=" * 70)
    
    # Run tests
    await test_simple_relay()
    await test_deepseek_json()
    await test_multi_ai_conversation()
    
    print("\n🎯 PROTOTYPE TESTING COMPLETE")
    print("Ready for next iteration based on results!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
