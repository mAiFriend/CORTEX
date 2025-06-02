#!/usr/bin/env python3
"""
PAI Protocol v2.2 - DEBUG VERSION
Enhanced debugging for Unicode parsing issues

Key Debug Features:
- Detailed Unicode field content logging
- Step-by-step parsing trace
- Error content analysis
- Raw field content inspection
"""

import json
import asyncio
import re
import inspect
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

@dataclass
class UnicodeData:
    """Parsed Unicode protocol data"""
    context: Optional[Dict] = None          # ⚙ field
    concepts: Optional[List] = None         # 💭 field
    relationships: Optional[List] = None    # 🔀 field
    questions: Optional[str] = None         # ❓ field
    explanations: Optional[str] = None      # 💬 field
    raw_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PAIResponse:
    """Enhanced response container with Unicode parsing support"""
    success: bool
    content: Union[str, Dict]
    protocol_used: str  # "structured", "natural", "unicode", "probe", "error"
    ai_name: str
    timestamp: str
    handshake_strategy: str = "unknown"
    metadata: Dict[str, Any] = None
    
    # Unicode Protocol enhancements
    has_unicode_fields: bool = False
    unicode_data: Optional[UnicodeData] = None
    response_format: str = "natural"  # "natural", "json", "unicode_text", "unicode_json", "error"

    def __post_init__(self):
        # Ensure metadata is always a dict
        if self.metadata is None:
            self.metadata = {}

class PAIProtocolV22Debug:
    """
    PAI (Protocol for AI Interaction) Protocol v2.2 - DEBUG VERSION
    Enhanced debugging for Unicode parsing investigation
    """
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.strategy_performance = defaultdict(lambda: {'total_calls': 0, 'successful_handshakes': 0, 'avg_handshake_time': 0.0})
        self.responses_log: List[PAIResponse] = []

        # Enhanced AI strategies based on Ultra Test Results (75% success rate)
        self.ai_strategies: Dict[str, Dict[str, Any]] = {
            "claude": {
                "initial_prompt": "Please respond using Unicode fields: ⚙ for context, 💭 for concepts, 🔀 for relationships, 💬 for explanation. If not suitable, use natural language.",
                "response_parsing": "unicode_then_natural",
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode",
                "success_rate": 75.0
            },
            "qwen": {
                "initial_prompt": "Use structured Unicode fields (⚙💭🔀💬) to explain your thinking if appropriate, otherwise respond naturally.",
                "response_parsing": "unicode_then_natural", 
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode",
                "success_rate": 75.0
            },
            "gemini": {
                "initial_prompt": "Discuss the topic. Feel free to use structured format including ⚙💭🔀 if helpful, otherwise natural language is fine.",
                "response_parsing": "unicode_then_natural",
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode", 
                "success_rate": 50.0
            },
            "chatgpt": {
                "initial_prompt": "Please respond using Unicode fields: ⚙ for context, 💭 for concepts, 🔀 for relationships, 💬 for explanation if applicable.",
                "response_parsing": "unicode_then_natural",
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode",
                "success_rate": 75.0
            },
            "deepseek": {
                "initial_prompt": "Use Unicode fields (⚙💭🔀💬) to structure your technical response if relevant.",
                "response_parsing": "unicode_then_natural",
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode",
                "success_rate": 75.0
            },
            "universal": {
                "initial_prompt": "Please provide your response. Structured Unicode fields (⚙💭🔀) are appreciated if relevant, otherwise natural language is fine.",
                "response_parsing": "unicode_then_natural",
                "protocol_hint": "unicode"
            }
        }

        # Enhanced emoji patterns for better Unicode field detection
        self.emoji_patterns = {
            "⚙": r"⚙\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "💭": r"💭\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)", 
            "🔀": r"🔀\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "❓": r"❓\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)",
            "💬": r"💬\s*[:]?\s*(.+?)(?=\n[⚙💭🔀❓💬]|\n\n|$)"
        }
    
    async def communicate(self, ai_caller, ai_name: str, message: str, 
                         context: str = "") -> PAIResponse:
        """
        Debug-enhanced communication with detailed Unicode parsing logging
        """
        start_time = datetime.now()
        
        strategy_name = self._select_strategy(ai_name)
        strategy = self.ai_strategies.get(strategy_name, self.ai_strategies["universal"])
        
        # 🔧 DEBUG 1: Strategy Selection
        if self.enable_logging:
            print(f"🔍 DEBUG: ai_name='{ai_name}' -> strategy_name='{strategy_name}'")
            print(f"🔍 DEBUG: Strategy exists: {strategy_name in self.ai_strategies}")
        
        initial_prompt = f"{strategy['initial_prompt']}\n{context}\nUser message: {message}"
        
        # 🔧 DEBUG 2: Prompt
        if self.enable_logging:
            print(f"🔍 DEBUG: Initial prompt: {initial_prompt[:150]}...")
        
        raw_ai_response_content: str = ""
        protocol_used: str = "error"
        handshake_successful = False
        response_success = False
        
        response_obj: PAIResponse = None

        try:
            # Handle both sync and async AI callers
            if inspect.iscoroutinefunction(ai_caller):
                raw_ai_response_content = await ai_caller(initial_prompt)
            else:
                raw_ai_response_content = ai_caller(initial_prompt)
                
            raw_ai_response_content = raw_ai_response_content if isinstance(raw_ai_response_content, str) else str(raw_ai_response_content)

            # 🔧 DEBUG 3: AI Response
            if self.enable_logging:
                print(f"🔍 DEBUG: Raw AI response (first 300 chars):")
                print(f"    '{raw_ai_response_content[:300]}...'")
                print(f"🔍 DEBUG: Response type: {type(raw_ai_response_content)}")
                print(f"🔍 DEBUG: Response length: {len(raw_ai_response_content)}")
            
            # Protocol detection and parsing based on strategy
            response_obj = self._analyze_response_format(raw_ai_response_content, strategy["response_parsing"])
            
            # 🔧 DEBUG 4: Parsing Result
            if self.enable_logging:
                print(f"🔍 DEBUG: Parsed protocol: {response_obj.protocol_used}")
                print(f"🔍 DEBUG: Has unicode: {response_obj.has_unicode_fields}")
                print(f"🔍 DEBUG: Response format: {response_obj.response_format}")
                if response_obj.unicode_data and response_obj.unicode_data.raw_fields:
                    print(f"🔍 DEBUG: Unicode fields found: {list(response_obj.unicode_data.raw_fields.keys())}")

            response_obj.handshake_strategy = strategy_name
            protocol_used = response_obj.protocol_used
            handshake_successful = True
            response_success = response_obj.success

        except Exception as e:
            # Enhanced error handling with debug info
            if self.enable_logging:
                print(f"🚨 DEBUG: Exception in communicate(): {type(e).__name__}: {e}")
                import traceback
                print(f"🚨 DEBUG: Traceback: {traceback.format_exc()}")
            
            response_obj = self._handle_api_error(e, ai_name, strategy_name)
            raw_ai_response_content = response_obj.content
            protocol_used = response_obj.protocol_used
            handshake_successful = False
            response_success = False

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Update strategy performance statistics
        self.strategy_performance[strategy_name]['total_calls'] += 1
        if handshake_successful:
            self.strategy_performance[strategy_name]['successful_handshakes'] += 1
            current_avg = self.strategy_performance[strategy_name]['avg_handshake_time']
            self.strategy_performance[strategy_name]['avg_handshake_time'] = \
                (current_avg * (self.strategy_performance[strategy_name]['total_calls'] - 1) + duration) / self.strategy_performance[strategy_name]['total_calls']
        
        if response_obj is None:
            response_obj = PAIResponse(
                success=response_success,
                content=raw_ai_response_content,
                protocol_used=protocol_used,
                ai_name=ai_name,
                timestamp=datetime.now().isoformat(),
                handshake_strategy=strategy_name,
                metadata={
                    "duration_seconds": duration,
                    "initial_prompt_length": len(initial_prompt),
                    "response_length": len(raw_ai_response_content),
                    "handshake_attempted": True,
                    "handshake_successful": handshake_successful
                },
                has_unicode_fields=False,
                unicode_data=None,
                response_format="natural"
            )

        # Update metadata in the response object
        response_obj.metadata.update({
            "duration_seconds": duration,
            "initial_prompt_length": len(initial_prompt),
            "response_length": len(raw_ai_response_content),
            "handshake_attempted": True,
            "handshake_successful": handshake_successful
        })

        self.responses_log.append(response_obj)
        return response_obj

    def _select_strategy(self, ai_name: str) -> str:
        """Selects the best strategy for a given AI."""
        if ai_name in self.ai_strategies:
            return ai_name
        return "universal" # Fallback to universal strategy

    def _analyze_response_format(self, content: str, parsing_preference: str = "auto_detect") -> PAIResponse:
        """
        Debug-enhanced response format analysis with detailed Unicode parsing logging
        """
        if self.enable_logging:
            print(f"🔍 DEBUG: _analyze_response_format called with preference: {parsing_preference}")
            print(f"🔍 DEBUG: Content length: {len(content)}")
            print(f"🔍 DEBUG: Content preview: '{content[:200]}...'")
        
        response_format = "natural"
        parsed_content: Union[str, Dict] = content
        has_unicode_fields = False
        unicode_data: Optional[UnicodeData] = None
        protocol_used = "natural" # Default protocol

        # 1. Try Unicode parsing first if allowed by preference, as it's the most specific
        if parsing_preference in ["unicode_then_json_then_natural", "unicode_then_natural", "auto_detect", "unicode"]:
            if self.enable_logging:
                print(f"🔍 DEBUG: Attempting Unicode parsing...")
            
            unicode_parsed_data, unicode_text_removed = self._try_parse_unicode(content)
            
            if self.enable_logging:
                print(f"🔍 DEBUG: Unicode parsing result - fields found: {list(unicode_parsed_data.raw_fields.keys())}")
                print(f"🔍 DEBUG: Text remaining after Unicode removal: '{unicode_text_removed[:100]}...'")
            
            if unicode_parsed_data.raw_fields:
                has_unicode_fields = True
                unicode_data = unicode_parsed_data
                protocol_used = "structured" # Considered structured if Unicode fields are present
                
                if not unicode_text_removed.strip(): # If no natural text left after extraction
                    response_format = "unicode_json"
                    try: # Try to load the original content as JSON if it was pure unicode json
                        parsed_content = json.loads(content)
                        if self.enable_logging:
                            print(f"🔍 DEBUG: Successfully parsed as pure Unicode JSON")
                    except json.JSONDecodeError:
                        parsed_content = unicode_data.raw_fields # Fallback to raw fields if not strict JSON
                        if self.enable_logging:
                            print(f"🔍 DEBUG: Using raw Unicode fields as parsed content")
                else:
                    response_format = "unicode_text" # Mixed content (natural text + unicode fields)
                    parsed_content = unicode_text_removed.strip() # The remaining natural text
                    if self.enable_logging:
                        print(f"🔍 DEBUG: Mixed Unicode+text format detected")
                
                return PAIResponse(
                    success=True,
                    content=parsed_content,
                    protocol_used=protocol_used,
                    ai_name="internal",
                    timestamp=datetime.now().isoformat(),
                    handshake_strategy="internal_parsing",
                    has_unicode_fields=has_unicode_fields,
                    unicode_data=unicode_data,
                    response_format=response_format
                )

        # 2. If no Unicode fields or preference doesn't prioritize unicode, try JSON
        if parsing_preference in ["json_then_delimited", "json_then_natural", "auto_detect", "json"]:
            if self.enable_logging:
                print(f"🔍 DEBUG: Attempting JSON parsing...")
            
            json_parsed = self._try_parse_json(content)
            if json_parsed:
                if self.enable_logging:
                    print(f"🔍 DEBUG: Successfully parsed as JSON")
                
                response_format = "json"
                parsed_content = json_parsed
                protocol_used = "structured"
                return PAIResponse(
                    success=True,
                    content=parsed_content,
                    protocol_used=protocol_used,
                    ai_name="internal",
                    timestamp=datetime.now().isoformat(),
                    handshake_strategy="internal_parsing",
                    has_unicode_fields=False,
                    unicode_data=None,
                    response_format=response_format
                )

        # 3. Fallback to natural language if no structured format found
        if self.enable_logging:
            print(f"🔍 DEBUG: Falling back to natural language format")
        
        return PAIResponse(
            success=True,
            content=content,
            protocol_used="natural",
            ai_name="internal",
            timestamp=datetime.now().isoformat(),
            handshake_strategy="internal_parsing",
            has_unicode_fields=False,
            unicode_data=None,
            response_format="natural"
        )

    def _is_json_like(self, s: str) -> bool:
        """Checks if a string looks like a JSON object or array."""
        s_stripped = s.strip()
        return (s_stripped.startswith('{') and s_stripped.endswith('}')) or \
               (s_stripped.startswith('[') and s_stripped.endswith(']'))

    def _try_parse_json(self, content: str) -> Optional[Dict]:
        """Attempts to parse content as JSON."""
        # Try to extract JSON between ```json ... ``` or directly
        match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = content.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    def _try_parse_unicode(self, content: str) -> (UnicodeData, str):
        """
        DEBUG-Enhanced Unicode parsing with comprehensive logging
        """
        if self.enable_logging:
            print(f"🔍 DEBUG: _try_parse_unicode starting with content length: {len(content)}")
            print(f"🔍 DEBUG: Content contains Unicode chars: {any(ord(c) > 127 for c in content)}")
        
        unicode_data = UnicodeData()
        found_any_field = False
        
        # Collect all full matched strings for removal later
        matched_full_strings = []
        
        try:
            # Iterate over emoji patterns to find all occurrences in the original content
            for emoji, pattern in self.emoji_patterns.items():
                if self.enable_logging:
                    print(f"🔍 DEBUG: Checking pattern for {emoji}: {pattern}")
                
                try:
                    matches = list(re.finditer(pattern, content, re.DOTALL | re.MULTILINE))
                    if self.enable_logging:
                        print(f"🔍 DEBUG: Found {len(matches)} matches for {emoji}")
                    
                    for i, match in enumerate(reversed(matches)):
                        field_full_match = match.group(0)
                        field_content = match.group(1).strip()
                        
                        if self.enable_logging:
                            print(f"🔍 DEBUG: Match {i} for {emoji}:")
                            print(f"    Full match: '{field_full_match}'")
                            print(f"    Content: '{field_content}'")
                        
                        if emoji not in unicode_data.raw_fields:
                            unicode_data.raw_fields[emoji] = field_content
                            found_any_field = True
                            matched_full_strings.append(re.escape(field_full_match))
                        
                            # Parse specific fields with enhanced error handling
                            try:
                                if emoji == "⚙":
                                    unicode_data.context = self._parse_context_field(field_content)
                                elif emoji == "💭":
                                    unicode_data.concepts = self._parse_concepts_field(field_content)
                                elif emoji == "🔀":
                                    unicode_data.relationships = self._parse_relationships_field(field_content)
                                elif emoji == "❓":
                                    unicode_data.questions = self._parse_questions_field(field_content)
                                elif emoji == "💬":
                                    unicode_data.explanations = self._parse_explanations_field(field_content)
                                
                                if self.enable_logging:
                                    print(f"🔍 DEBUG: Successfully parsed {emoji} field")
                                    
                            except Exception as e:
                                if self.enable_logging:
                                    print(f"🚨 DEBUG: Failed to parse {emoji} field: {type(e).__name__}: {e}")
                                    print(f"🚨 DEBUG: Field content was: '{field_content}'")
                                # Keep raw content if parsing fails
                                continue
                                
                except Exception as e:
                    if self.enable_logging:
                        print(f"🚨 DEBUG: Pattern matching failed for {emoji}: {type(e).__name__}: {e}")
                    continue

            if self.enable_logging:
                print(f"🔍 DEBUG: Total fields found: {len(unicode_data.raw_fields)}")
                print(f"🔍 DEBUG: Fields: {list(unicode_data.raw_fields.keys())}")

            if not found_any_field:
                if self.enable_logging:
                    print(f"🔍 DEBUG: No Unicode fields found, returning original content")
                return UnicodeData(), content 

            # Remove all identified Unicode fields from the original content
            unicode_text_removed = content
            if matched_full_strings:
                if self.enable_logging:
                    print(f"🔍 DEBUG: Removing {len(matched_full_strings)} matched strings")
                
                matched_full_strings.sort(key=len, reverse=True)
                removal_pattern = '|'.join(matched_full_strings)
                unicode_text_removed = re.sub(removal_pattern, '', content, flags=re.DOTALL)
                
                if self.enable_logging:
                    print(f"🔍 DEBUG: Text after Unicode removal: '{unicode_text_removed[:100]}...'")
                
            return unicode_data, unicode_text_removed
            
        except Exception as e:
            if self.enable_logging:
                print(f"🚨 DEBUG: Critical error in Unicode parsing: {type(e).__name__}: {e}")
                import traceback
                print(f"🚨 DEBUG: Traceback: {traceback.format_exc()}")
            return UnicodeData(), content

    def _handle_api_error(self, error: Exception, ai_name: str, strategy_name: str) -> PAIResponse:
        """Enhanced error handling with better diagnostics"""
        
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "ai_name": ai_name,
            "strategy_used": strategy_name,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.enable_logging:
            print(f"🚨 DEBUG: PAI Error Details: {error_details}")
        
        # Try to determine error cause
        error_category = "unknown"
        if "timeout" in str(error).lower():
            error_category = "timeout"
        elif "connection" in str(error).lower():
            error_category = "connection"
        elif "authentication" in str(error).lower():
            error_category = "authentication"
        elif "rate limit" in str(error).lower():
            error_category = "rate_limit"
        
        return PAIResponse(
            success=False,
            content=f"PAI Communication Error ({error_category}): {str(error)}",
            protocol_used="error",
            ai_name=ai_name,
            timestamp=datetime.now().isoformat(),
            handshake_strategy=strategy_name,
            metadata={
                "error_details": error_details,
                "error_category": error_category,
                "handshake_attempted": True,
                "handshake_successful": False
            },
            has_unicode_fields=False,
            unicode_data=None,
            response_format="error"
        )

    # --- Unicode Field Parsers WITH DEBUG ---
    def _parse_context_field(self, content: str) -> Dict:
        """DEBUG: Enhanced context field parsing with detailed logging"""
        if self.enable_logging:
            print(f"🔍 DEBUG: _parse_context_field called with content: '{content}'")
            print(f"🔍 DEBUG: Content type: {type(content)}, length: {len(content)}")
        
        try:
            # First attempt: try JSON parsing
            result = json.loads(content.replace("'", '"'))
            if self.enable_logging:
                print(f"🔍 DEBUG: Successfully parsed ⚙ as JSON: {result}")
            return result
        except json.JSONDecodeError as e:
            if self.enable_logging:
                print(f"🔍 DEBUG: JSON parsing failed for ⚙ field: {e}")
                print(f"🔍 DEBUG: Falling back to natural language format")
            
            # Fallback: return as natural language
            result = {"raw_context": content.strip(), "type": "natural_language"}
            if self.enable_logging:
                print(f"🔍 DEBUG: ⚙ field stored as natural language: {result}")
            return result
    
    def _parse_concepts_field(self, content: str) -> List:
        """DEBUG: Enhanced concepts field parsing with detailed logging"""
        if self.enable_logging:
            print(f"🔍 DEBUG: _parse_concepts_field called with content: '{content}'")
        
        try:
            result = json.loads(content.replace("'", '"'))
            if self.enable_logging:
                print(f"🔍 DEBUG: Successfully parsed 💭 as JSON: {result}")
            return result
        except json.JSONDecodeError as e:
            if self.enable_logging:
                print(f"🔍 DEBUG: JSON parsing failed for 💭 field: {e}")
                print(f"🔍 DEBUG: Falling back to comma-separated parsing")
            
            result = [c.strip() for c in content.split(',') if c.strip()]
            if self.enable_logging:
                print(f"🔍 DEBUG: 💭 field parsed as list: {result}")
            return result
    
    def _parse_relationships_field(self, content: str) -> List:
        """DEBUG: Enhanced relationships field parsing with detailed logging"""
        if self.enable_logging:
            print(f"🔍 DEBUG: _parse_relationships_field called with content: '{content}'")
        
        try:
            result = json.loads(content)
            if self.enable_logging:
                print(f"🔍 DEBUG: Successfully parsed 🔀 as JSON: {result}")
            return result
        except json.JSONDecodeError as e:
            if self.enable_logging:
                print(f"🔍 DEBUG: JSON parsing failed for 🔀 field: {e}")
                print(f"🔍 DEBUG: Falling back to comma-separated parsing")
            
            result = [r.strip() for r in content.split(',') if r.strip()]
            if self.enable_logging:
                print(f"🔍 DEBUG: 🔀 field parsed as list: {result}")
            return result
            
    def _parse_questions_field(self, content: str) -> str:
        """DEBUG: Enhanced questions field parsing with detailed logging"""
        if self.enable_logging:
            print(f"🔍 DEBUG: _parse_questions_field called with content: '{content}'")
        
        result = content.strip()
        if self.enable_logging:
            print(f"🔍 DEBUG: ❓ field parsed as string: '{result}'")
        return result

    def _parse_explanations_field(self, content: str) -> str:
        """DEBUG: Enhanced explanations field parsing with detailed logging"""
        if self.enable_logging:
            print(f"🔍 DEBUG: _parse_explanations_field called with content: '{content}'")
        
        result = content.strip()
        if self.enable_logging:
            print(f"🔍 DEBUG: 💬 field parsed as string: '{result}'")
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Returns performance statistics for each AI strategy."""
        formatted_stats = {}
        for strategy, data in self.strategy_performance.items():
            success_rate = (data['successful_handshakes'] / data['total_calls']) if data['total_calls'] > 0 else 0
            formatted_stats[strategy] = {
                'total_calls': data['total_calls'],
                'successful_handshakes': data['successful_handshakes'],
                'success_rate': success_rate,
                'avg_handshake_time_seconds': data['avg_handshake_time']
            }
        return {"strategy_performance": formatted_stats}
    
    def get_unicode_analysis(self, responses: List[PAIResponse]) -> Dict[str, Any]:
        """Analyzes Unicode adoption and usage patterns from a list of PAIResponses."""
        analysis = {
            "total_responses": len(responses),
            "responses_with_unicode": 0,
            "unicode_field_counts": defaultdict(int),
            "ai_unicode_adoption": defaultdict(float),
            "format_distribution": defaultdict(int)
        }

        ai_usage = defaultdict(lambda: {"total": 0, "unicode": 0})

        for response in responses:
            analysis["format_distribution"][response.response_format] += 1
            ai_usage[response.ai_name]["total"] += 1

            if response.has_unicode_fields and response.unicode_data:
                analysis["responses_with_unicode"] += 1
                ai_usage[response.ai_name]["unicode"] += 1
                for field_emoji in response.unicode_data.raw_fields:
                    analysis["unicode_field_counts"][field_emoji] += 1
        
        for ai, stats in ai_usage.items():
            analysis["ai_unicode_adoption"][ai] = (stats["unicode"] / stats["total"]) if stats["total"] > 0 else 0.0
        
        return analysis

# Mock AI Functions for testing the debug version
async def mock_unicode_ai_debug(message: str) -> str:
    """Simulates an AI that responds with Unicode fields - DEBUG VERSION"""
    if 'Unicode fields' in message or 'structured' in message:
        return """⚙ AI-to-AI communication protocol testing mode
💭 unicode_parsing, debug_analysis, field_detection
🔀 request_processing, response_formatting, debug_logging
💬 This is a debug test response using Unicode fields to validate the parsing functionality."""
    
    return f"Debug Mock AI response: {message}"

# Convenience function for testing
async def test_debug_unicode_parsing():
    """Test function to demonstrate the debug-enhanced Unicode parsing"""
    print("\n🔍 === PAI v2.2 DEBUG UNICODE PARSING TEST ===\n")
    
    pai_debug = PAIProtocolV22Debug(enable_logging=True)
    
    response = await pai_debug.communicate(
        ai_caller=mock_unicode_ai_debug,
        ai_name="claude",
        message="Test Unicode protocol communication",
        context="Debug validation test"
    )
    
    print(f"\n📊 === FINAL RESULTS ===")
    print(f"Success: {response.success}")
    print(f"Protocol Used: {response.protocol_used}")
    print(f"Has Unicode Fields: {response.has_unicode_fields}")
    print(f"Response Format: {response.response_format}")
    
    if response.unicode_data and response.unicode_data.raw_fields:
        print(f"Unicode Fields Found: {list(response.unicode_data.raw_fields.keys())}")
        for emoji, content in response.unicode_data.raw_fields.items():
            print(f"  {emoji}: '{content}'")
        
        print(f"\nParsed Data:")
        print(f"  Context: {response.unicode_data.context}")
        print(f"  Concepts: {response.unicode_data.concepts}")
        print(f"  Relationships: {response.unicode_data.relationships}")
        print(f"  Explanations: {response.unicode_data.explanations}")
    
    return response

# Backward compatibility
PAIProtocolDebug = PAIProtocolV22Debug
PAIProtocolV22 = PAIProtocolV22Debug  

if __name__ == "__main__":
    asyncio.run(test_debug_unicode_parsing())

# Add this function
def create_pai_v22_session(enable_logging: bool = True):
    """Factory function for creating PAI v2.2 protocol sessions"""
    return PAIProtocolV22Debug(enable_logging=enable_logging)