# pai_v2.1_test.py

import asyncio
import json
import sys
import os
import inspect 

from datetime import datetime
from collections import defaultdict
print(f"Executing script from: {os.path.abspath(__file__)}")

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pai import PAIProtocolV2, PAIResponse, UnicodeData
    # Importiere die neuen Mock-AIs, die wir definiert haben
    from pai import mock_unicode_ai, mock_json_ai, mock_natural_ai, mock_broken_ai
    print("✓ PAI Protocol v2.1 and Mock AIs imported successfully.")
except ImportError as e:
    print(f"✗ Failed to import PAI Protocol or Mock AIs: {e}")
    print("Make sure pai.py is in the current directory and contains PAIProtocolV2 and the mock_ai functions.")
    sys.exit(1)

class TestPAIProtocolV2_1:
    def __init__(self):
        self.pai = PAIProtocolV2(enable_logging=False)
        self.test_results = []
        self.overall_success = True
        print(f"DEBUG: TestPAIProtocolV2_1 class module: {self.__class__.__module__}")
        print(f"DEBUG: Signature of self.run_test_case at init: {inspect.signature(self.run_test_case)}")

    async def run_test_case(self, test_name: str, ai_caller, ai_name: str, message: str, context: str,
                            expected_protocol: str = None, expected_unicode_fields: list = None,
                            expect_success: bool = True, custom_validation_func=None):
        """Führt einen einzelnen Testfall aus und protokolliert das Ergebnis."""
        print(f"run_test_case called with arguments: {locals().keys()}")
        print(f"\n--- Running Test Case: {test_name} ---")
        print(f"  AI: {ai_name}, Message: '{message[:70]}...'")

        start_time = datetime.now()
        response: PAIResponse = None
        try:
            response = await self.pai.communicate(
                ai_caller=ai_caller,
                ai_name=ai_name,
                message=message,
                context=context
            )
            duration = (datetime.now() - start_time).total_seconds()
            
            test_passed = response.success == expect_success

            # Check if expected protocol is 'structured' when unicode fields are expected
            # This is because unicode parsing leads to 'structured' protocol_used
            protocol_check_value = expected_protocol
            if expected_unicode_fields and expected_protocol == "structured":
                # If unicode fields are expected, the actual protocol should be 'structured'
                # but the response_format might be 'unicode_json' or 'unicode_text'
                if not (response.protocol_used == "structured" and response.has_unicode_fields):
                    print(f"    ✗ Protocol mismatch! Expected structured (with Unicode fields), got '{response.protocol_used}' and has_unicode_fields={response.has_unicode_fields}")
                    test_passed = False
            elif expected_protocol and response.protocol_used != expected_protocol:
                print(f"    ✗ Protocol mismatch! Expected '{expected_protocol}', got '{response.protocol_used}'")
                test_passed = False
            
            if expected_unicode_fields:
                actual_fields = list(response.unicode_data.raw_fields.keys()) if response.unicode_data else []
                if not all(field in actual_fields for field in expected_unicode_fields):
                    print(f"    ✗ Unicode fields mismatch! Expected {expected_unicode_fields}, got {actual_fields}")
                    test_passed = False
                elif not response.has_unicode_fields:
                    print(f"    ✗ Expected Unicode fields but has_unicode_fields is False.")
                    test_passed = False

            if custom_validation_func:
                if not custom_validation_func(response):
                    print(f"    ✗ Custom validation failed for {test_name}.")
                    test_passed = False
            
            if test_passed:
                print(f"    ✓ PASSED. Protocol: {response.protocol_used}, Handshake: {response.handshake_strategy}, Unicode: {response.has_unicode_fields}, Format: {response.response_format}")
            else:
                print(f"    ✗ FAILED. Protocol: {response.protocol_used}, Handshake: {response.handshake_strategy}, Success: {response.success}, Format: {response.response_format}")
                self.overall_success = False

            self.test_results.append({
                "name": test_name,
                "ai_name": ai_name,
                "passed": test_passed,
                "success_flag": response.success,
                "protocol_used": response.protocol_used,
                "handshake_strategy": response.handshake_strategy,
                "has_unicode_fields": response.has_unicode_fields,
                "duration": duration,
                "content_preview": str(response.content)[:100],
                "metadata": response.metadata,
                "unicode_data": response.unicode_data.raw_fields if response.unicode_data else None,
                "response_format": response.response_format
            })

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            print(f"    ✗ FAILED with exception: {e}")
            self.overall_success = False
            self.test_results.append({
                "name": test_name,
                "ai_name": ai_name,
                "passed": False,
                "error": str(e),
                "duration": duration
            })
            
    # Temporärer Debug-Test (in pai_v2.1_test.py hinzufügen):
    async def debug_unicode_strategy():
        pai = PAIProtocolV2(enable_logging=True)
    
        print("=== DEBUG: Testing claude_unicode strategy ===")
        response = await pai.communicate(
            ai_caller=mock_unicode_ai,
            ai_name="claude_unicode",
            message="Test unicode",
            context=""
        )
        print(f"Strategy used: {response.handshake_strategy}")
        print(f"Protocol: {response.protocol_used}")
        print(f"Success: {response.success}")
        print(f"Content preview: {str(response.content)[:200]}")

# Rufe debug_unicode_strategy() vor den anderen Tests auf

    async def run_all_tests(self):
        print("\n" + "="*80)
        print("🚀 Starting Comprehensive PAI Protocol v2.1 Tests")
        print("="*80)
        print(f"DEBUG: Signature of run_test_case when called in run_all_tests: {inspect.signature(self.run_test_case)}")

        # --- Test Cases ---

        # 1. Test Unicode JSON Parsing (Claude strategy, mock_unicode_ai returning textual Unicode)
        await self.run_test_case(
            "TC1: Unicode JSON Parsing (Claude/mock_unicode_ai)",
            mock_unicode_ai, "claude_unicode", # Changed to claude_unicode for explicit Unicode strategy
            "Process this as structured Unicode data: {'key': 'value'}",
            "Test context for unicode json",
            expected_protocol="structured",
            expected_unicode_fields=["⚙", "💭", "🔀", "💬"]
        )

        # 2. Test Natural Language with Embedded Unicode Emojis (Qwen strategy, mock_unicode_ai returning mixed)
        def validate_mixed_unicode(response: PAIResponse):
            return response.response_format == "unicode_text" and "natural language explanation" in response.content and response.has_unicode_fields
        await self.run_test_case(
            "TC2: Natural Language with Embedded Unicode (Qwen/mock_unicode_ai)",
            mock_unicode_ai, "claude_unicode", # Changed to claude_unicode for explicit Unicode strategy
            "Can you respond naturally but also include emoji fields (⚙💭🔀)?",
            "Mixed format test",
            expected_protocol="structured", # It's structured because it has unicode fields
            expected_unicode_fields=["⚙", "💭", "🔀", "❓", "💬"],
            custom_validation_func=validate_mixed_unicode
        )
        
        # 3. Test Pure JSON Response (Gemini strategy, mock_json_ai)
        def validate_json_content(response: PAIResponse):
            # response.content should already be a dict if json parsing was successful
            if isinstance(response.content, dict):
                return response.content.get("status") == "success" and response.response_format == "json"
            return False # Content is not a dict, so it's not valid JSON
        await self.run_test_case(
            "TC3: Pure JSON Response (Gemini/mock_json_ai)",
            mock_json_ai, "gemini",
            "Please provide a structured data response.",
            "JSON preference test",
            expected_protocol="structured",
            custom_validation_func=validate_json_content
        )

        # 4. Test Pure Natural Language Response (Universal strategy, mock_natural_ai)
        await self.run_test_case(
            "TC4: Pure Natural Language (Universal/mock_natural_ai)",
            mock_natural_ai, "unknown_ai", # Nutzt die Universalstrategie
            "Tell me about the weather.",
            "Simple natural language query",
            expected_protocol="natural"
        )

        # 5. Test DeepSeek Technical Unicode Strategy
        def validate_deepseek_technical(response: PAIResponse):
            # The mock_unicode_ai for this scenario returns purely structured unicode content,
            # so the response_format should be 'unicode_json', not 'unicode_text'.
            return response.handshake_strategy == "deepseek_technical_unicode" and response.has_unicode_fields and response.response_format == "unicode_json" # Corrected to expect unicode_json
        await self.run_test_case(
            "TC5: DeepSeek Technical Unicode Strategy",
            mock_unicode_ai, "deepseek_technical_unicode", # Changed to deepseek_technical_unicode for explicit Unicode strategy
            "Run a semantic protocol test using technical Unicode.",
            "DeepSeek protocol context",
            expected_protocol="structured",
            custom_validation_func=validate_deepseek_technical
        )
        
        # 6. Test Handshake Failure & Natural Fallback (Broken AI)
        await self.run_test_case(
            "TC6: Handshake Failure & Natural Fallback (Broken AI)",
            mock_broken_ai, "claude", # Nutzt Claude-Strategie, sollte scheitern
            "Try to get structured response from me.",
            "Error handling test",
            expect_success=False # Erwarten einen Misserfolg oder Fallback zum Error-Protokoll
        )
        
        # 7. Test Unicode Parser - only context field (direct unicode text)
        def validate_single_field_parsing(response: PAIResponse):
            # When only a single Unicode field is present and the rest is empty, it should be unicode_text,
            # but for this very specific mock, it might get parsed as raw text if no other field delimiters are found
            # The key is that `has_unicode_fields` is True and the ⚙ field is present.
            return response.has_unicode_fields and "⚙" in response.unicode_data.raw_fields and len(response.unicode_data.raw_fields) == 1 and response.response_format == "unicode"
        await self.run_test_case(
            "TC7: Unicode Parser - Single Field",
            lambda msg: "⚙: {'data': 'single_field'}", 
            "qwen",
            "Just give me context",
            "",  # Leerer Kontext hinzufügen
            expected_protocol="structured",
            custom_validation_func=validate_single_field_parsing
        )
           
        # 8. Test _extract_concepts and _extract_relationships (internal function test, needs PAIProtocolV2 instance)
        # This test relies on directly instantiating PAIProtocolV2 and calling its internal methods.
        # It won't directly use mock_ai functions as the others.
        def validate_internal_extraction(response: PAIResponse): # 'response' here is just a placeholder, actual test uses internal calls
            pai_instance_for_internal_test = PAIProtocolV2()
            # Test with direct unicode text
            parsed_concepts_data, _ = pai_instance_for_internal_test._try_parse_unicode(f"💭: [\"protocol\", \"testing\"]")
            concepts_result = parsed_concepts_data.concepts

            parsed_relationships_data, _ = pai_instance_for_internal_test._try_parse_unicode(f"🔀: [\"causal_relationship\"]")
            relationships_result = parsed_relationships_data.relationships

            # Assert that the parsing was successful and content is correct
            return "protocol" in concepts_result and "testing" in concepts_result and "causal_relationship" in relationships_result

        await self.run_test_case(
            "TC8: Internal Extraction Functions Test (Concepts & Relationships)",
            mock_natural_ai, "gemini", # Using a mock AI to generate a PAIResponse, but actual validation is on internal logic
            "This is a dummy message for internal test.",
            "internal_extraction_context",
            expect_success=True, # Expect the AI call to succeed, then validate internal functions
            custom_validation_func=validate_internal_extraction
        )


        self.display_summary()

    def display_summary(self):
        """Zeigt eine Zusammenfassung aller Testfälle an."""
        print(f"\n{'='*80}")
        print("📊 PAI Protocol v2.1 Test Summary")
        print(f"{'='*80}")

        if not self.test_results:
            print("❌ No test results available.")
            return

        passed_count = sum(1 for r in self.test_results if r.get('passed'))
        failed_count = len(self.test_results) - passed_count

        print(f"Total Test Cases: {len(self.test_results)}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        print(f"Overall Test Status: {'✅ PASSED' if self.overall_success else '❌ FAILED'}")

        print("\nDetailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result.get('passed') else "❌"
            error_msg = f" (Error: {result['error']})" if 'error' in result else ""
            unicode_info = f" (Unicode Fields: {json.dumps(result['unicode_data'])})" if result['has_unicode_fields'] and result['unicode_data'] else ""
            print(f"  {status_icon} {result['name']}: Protocol='{result.get('protocol_used', 'N/A')}', Success={result.get('success_flag', 'N/A')}, Strategy='{result.get('handshake_strategy', 'N/A')}', Duration={result.get('duration', 0):.2f}s, Format='{result.get('response_format', 'N/A')}'{unicode_info}{error_msg}")

        # Display PAI internal statistics
        pai_stats = self.pai.get_statistics()
        print(f"\nPAI Protocol Internal Statistics:")
        for key, value in pai_stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2%}")
            elif isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")

        # Display Unicode analysis
        unicode_analysis = self.pai.get_unicode_analysis(self.pai.responses_log)
        print("\nUnicode Usage Analysis:")
        if unicode_analysis:
            for key, value in unicode_analysis.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2%}")
                else:
                    print(f"  {key}: {value}")

async def main():
    tester = TestPAIProtocolV2_1()
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nAn unhandled error occurred during testing: {e}")
        import traceback
        traceback.print_exc()