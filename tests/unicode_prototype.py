#!/usr/bin/env python3
"""
Unicode Prototype using PowerTalk's proven integrations
"""

import asyncio
import json
from datetime import datetime

# Import PowerTalk's working engine
from powertalk import PowerTalkEngine

class UnicodePrototypeEngine(PowerTalkEngine):
    """Extends PowerTalk with Unicode awareness"""
    
    def __init__(self):
        super().__init__()
        self.unicode_responses = []
    
    async def unicode_test_dialogue(self, question: str = None):
        """Quick Unicode test using PowerTalk's working infrastructure"""
        
        if not question:
            question = "What makes AI-to-AI communication different from human communication?"
        
        print("🌈 UNICODE PROTOTYPE - Using PowerTalk Infrastructure")
        print(f"Question: {question}")
        print("=" * 60)
        
        # Use PowerTalk's proven AI selection and connectivity
        available_ais = ["claude", "qwen"]  # Known working from your tests
        
        # Test with working PowerTalk API calls
        results = {}
        
        for ai_key in available_ais:
            print(f"🎯 Testing {ai_key}...")
            
            # Use PowerTalk's working call_ai_api method
            unicode_prompt = f"""
{question}

Please structure your response using Unicode fields if helpful:
⚙ for context/framing
💭 for key concepts  
🔀 for relationships
💬 for explanations

Or respond naturally - whatever feels authentic.
"""
            
            try:
                response = await self.call_ai_api(ai_key, unicode_prompt)
                results[ai_key] = response
                
                # Quick Unicode detection
                unicode_fields = [emoji for emoji in ['⚙', '💭', '🔀', '💬'] if emoji in response]
                if unicode_fields:
                    print(f"   📊 Unicode fields: {', '.join(unicode_fields)}")
                else:
                    print(f"   💬 Natural language response")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[ai_key] = f"Error: {e}"
        
        return results

# Test using PowerTalk's working infrastructure
async def test_with_powertalk():
    engine = UnicodePrototypeEngine()
    
    # Quick connectivity test first
    print("🔍 Testing PowerTalk connectivity...")
    working_ais, failed_ais = await engine.ping_ai_apis(["claude", "qwen"])
    
    if len(working_ais) < 1:
        print("❌ No working AIs - check PowerTalk configuration")
        return
    
    print(f"✅ Working AIs: {', '.join(working_ais)}")
    
    # Run Unicode test with working AIs
    results = await engine.unicode_test_dialogue()
    
    print("\n" + "=" * 60)
    print("🧠 UNICODE TEST RESULTS")
    print("=" * 60)
    
    for ai, response in results.items():
        print(f"\n{ai.upper()}:")
        print("-" * 20)
        print(response[:300] + "..." if len(response) > 300 else response)

if __name__ == "__main__":
    asyncio.run(test_with_powertalk())