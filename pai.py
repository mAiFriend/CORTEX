#!/usr/bin/env python3
"""
PAI Protocol v2.2 - Ultra Test Optimized Unicode Protocol
Critical fixes based on Ultra Test Results validation

Key Improvements:
- Sync/Async API caller compatibility (CRITICAL FIX)
- Enhanced Unicode strategies based on 75% success rate empirical data
- Improved error handling with diagnostic information
- Better Unicode field detection patterns
- Full backward compatibility with v2.1
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

class PAIProtocolV22:
    """
    PAI (Protocol for AI Interaction) Protocol v2.2
    Ultra Test Optimized with 75% Unicode success rate validation
    """
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.strategy_performance = defaultdict(lambda: {'total_calls': 0, 'successful_handshakes': 0, 'avg_handshake_time': 0.0})
        self.responses_log: List[PAIResponse] = []

        # 🔧 FIX 2: Enhanced AI strategies based on Ultra Test Results (75% success rate)
        self.ai_strategies: Dict[str, Dict[str, Any]] = {
            "claude": {
                "initial_prompt": "Please respond using Unicode fields: ⚙ for context, 💭 for concepts, 🔀 for relationships, 💬 for explanation. If not suitable, use natural language.",
                "response_parsing": "unicode_then_natural",
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode",
                "success_rate": 75.0  # From ultra test results
            },
            "qwen": {
                "initial_prompt": "Use structured Unicode fields (⚙💭🔀💬) to explain your thinking if appropriate, otherwise respond naturally.",
                "response_parsing": "unicode_then_natural", 
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode",
                "success_rate": 75.0  # From ultra test results
            },
            "gemini": {
                "initial_prompt": "Discuss the topic. Feel free to use structured format including ⚙💭🔀 if helpful, otherwise natural language is fine.",
                "response_parsing": "unicode_then_natural",
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode", 
                "success_rate": 50.0  # From ultra test results
            },
            "chatgpt": {
                "initial_prompt": "Please respond using Unicode fields: ⚙ for context, 💭 for concepts, 🔀 for relationships, 💬 for explanation if applicable.",
                "response_parsing": "unicode_then_natural",
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode",
                "success_rate": 75.0  # From ultra test results
            },
            "deepseek": {
                "initial_prompt": "Use Unicode fields (⚙💭🔀💬) to structure your technical response if relevant.",
                "response_parsing": "unicode_then_natural",
                "structured_start_tokens": ["⚙", "💭", "🔀", "❓", "💬"],
                "protocol_hint": "unicode",
                "success_rate": 75.0  # From ultra test results
            },
            "universal": {
                "initial_prompt": "Please provide your response. Structured Unicode fields (⚙💭🔀) are appreciated if relevant, otherwise natural language is fine.",
                "response_parsing": "unicode_then_natural",
                "protocol_hint": "unicode"
            }
        }

        # 🔧 FIX 2: Updated emoji patterns for better Unicode field detection
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
        Communicates with an AI, attempting to establish a preferred protocol.
        🔧 FIX 1: Handles both sync and async AI callers
        """
        start_time = datetime.now()
        
        strategy_name = self._select_strategy(ai_name)
        strategy = self.ai_strategies.get(strategy_name, self.ai_strategies["universal"])
        
        # 🔧 DEBUG 1: Strategy Selection
        if self.enable_logging:
            print(f"DEBUG: ai_name='{ai_name}' -> strategy_name='{strategy_name}'")
            print(f"DEBUG: Strategy exists: {strategy_name in self.ai_strategies}")
        
        initial_prompt = f"{strategy['initial_prompt']}\n{context}\nUser message: {message}"
        
        # 🔧 DEBUG 2: Prompt
        if self.enable_logging:
            print(f"DEBUG: Initial prompt: {initial_prompt[:150]}...")
        
        raw_ai_response_content: str = ""
        protocol_used: str = "error"
        handshake_successful = False
        response_success = False
        
        response_obj: PAIResponse = None

        try:
            # 🔧 FIX 1: Handle both sync and async AI callers
            if inspect.iscoroutinefunction(ai_caller):
                # Async caller
                raw_ai_response_content = await ai_caller(initial_prompt)
            else:
                # Sync caller (like integrations.claude.query)
                raw_ai_response_content = ai_caller(initial_prompt)
                
            raw_ai_response_content = raw_ai_response_content if isinstance(raw_ai_response_content, str) else str(raw_ai_response_content)

            # 🔧 DEBUG 3: AI Response
            if self.enable_logging:
                print(f"DEBUG: Raw AI response: {raw_ai_response_content[:200]}...")
                print(f"DEBUG: Response type: {type(raw_ai_response_content)}")
            
            # Protocol detection and parsing based on strategy
            response_obj = self._analyze_response_format(raw_ai_response_content, strategy["response_parsing"])
            
            # 🔧 DEBUG 4: Parsing Result
            if self.enable_logging:
                print(f"DEBUG: Parsed protocol: {response_obj.protocol_used}")
                print(f"DEBUG: Has unicode: {response_obj.has_unicode_fields}")
                print(f"DEBUG: Response format: {response_obj.response_format}")

            response_obj.handshake_strategy = strategy_name
            protocol_used = response_obj.protocol_used
            handshake_successful = True
            response_success = response_obj.success

        except Exception as e:
            # 🔧 FIX 3: Enhanced error handling
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
        Analyzes the AI's raw response content to determine its format and extract data.
        Prioritizes structured formats based on parsing_preference.
        """
        response_format = "natural"
        parsed_content: Union[str, Dict] = content
        has_unicode_fields = False
        unicode_data: Optional[UnicodeData] = None
        protocol_used = "natural" # Default protocol

        # 1. Try Unicode parsing first if allowed by preference, as it's the most specific
        if parsing_preference in ["unicode_then_json_then_natural", "unicode_then_natural", "auto_detect", "unicode"]:
            unicode_parsed_data, unicode_text_removed = self._try_parse_unicode(content)
            if unicode_parsed_data.raw_fields:
                has_unicode_fields = True
                unicode_data = unicode_parsed_data
                protocol_used = "structured" # Considered structured if Unicode fields are present
                
                if not unicode_text_removed.strip(): # If no natural text left after extraction
                    response_format = "unicode_json"
                    try: # Try to load the original content as JSON if it was pure unicode json
                        # If the content was purely unicode fields that also form a valid JSON, use that.
                        # Otherwise, content is the unicode_data itself (raw_fields)
                        parsed_content = json.loads(content)
                    except json.JSONDecodeError:
                        parsed_content = unicode_data.raw_fields # Fallback to raw fields if not strict JSON
                else:
                    response_format = "unicode_text" # Mixed content (natural text + unicode fields)
                    parsed_content = unicode_text_removed.strip() # The remaining natural text
                
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
            json_parsed = self._try_parse_json(content)
            if json_parsed:
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
        🔧 FIX 3: Enhanced Unicode parsing with better error handling
        Returns UnicodeData and the content with Unicode fields removed.
        """
        unicode_data = UnicodeData()
        found_any_field = False
        
        # Collect all full matched strings for removal later
        matched_full_strings = []
        
        try:
            # Iterate over emoji patterns to find all occurrences in the original content
            for emoji, pattern in self.emoji_patterns.items():
                try:
                    matches = list(re.finditer(pattern, content, re.DOTALL | re.MULTILINE))
                    for match in reversed(matches):
                        field_full_match = match.group(0)
                        field_content = match.group(1).strip()
                        
                        if emoji not in unicode_data.raw_fields:
                            unicode_data.raw_fields[emoji] = field_content
                            found_any_field = True
                            matched_full_strings.append(re.escape(field_full_match))
                        
                            # Parse specific fields with error handling
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
                            except Exception as e:
                                if self.enable_logging:
                                    print(f"PAI: Warning - Failed to parse {emoji} field: {e}")
                                # Keep raw content if parsing fails
                                continue
                                
                except Exception as e:
                    if self.enable_logging:
                        print(f"PAI: Warning - Pattern matching failed for {emoji}: {e}")
                    continue

            if not found_any_field:
                return UnicodeData(), content 

            # Remove all identified Unicode fields from the original content
            unicode_text_removed = content
            if matched_full_strings:
                matched_full_strings.sort(key=len, reverse=True)
                removal_pattern = '|'.join(matched_full_strings)
                unicode_text_removed = re.sub(removal_pattern, '', content, flags=re.DOTALL)
                
            return unicode_data, unicode_text_removed
            
        except Exception as e:
            if self.enable_logging:
                print(f"PAI: Critical error in Unicode parsing: {e}")
            return UnicodeData(), content

    # 🔧 FIX 3: Enhanced error handling method
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
            print(f"PAI Error Details: {error_details}")
        
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

    # --- Unicode Field Parsers ---
    def _parse_context_field(self, content: str) -> Dict:
        """Parses the ⚙ field content into a dictionary."""
        try:
            # Versuche doppelte Anführungszeichen
            return json.loads(content.replace("'", '"')) 
        except json.JSONDecodeError:
            # Fallback-Logik für normales JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                if self.enable_logging:
                    print(f"PAI: Warning - Failed to parse ⚙ context as JSON: {content}")
                return {"raw_context": content, "type": "natural_language"}

    def _parse_concepts_field(self, content: str) -> List:
        """Parses the 💭 field content into a list."""
        try:
            # Versuche doppelte Anführungszeichen
            return json.loads(content.replace("'", '"')) 
        except json.JSONDecodeError:
            # Fallback-Logik für normales JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                if self.enable_logging:
                    print(f"PAI: Warning - Failed to parse 💭 concepts as JSON: {content}")
                return [c.strip() for c in content.split(',') if c.strip()]

    def _parse_relationships_field(self, content: str) -> List:
        """Parses the 🔀 field content into a list."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if self.enable_logging:
                print(f"PAI: Warning - Failed to parse 🔀 relationships as JSON: {content}")
            return [r.strip() for r in content.split(',') if r.strip()]

    def _parse_questions_field(self, content: str) -> str:
        """Parses the ❓ field content into a string."""
        return content.strip()

    def _parse_explanations_field(self, content: str) -> str:
        """Parses the 💬 field content into a string."""
        return content.strip()

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
            "ai_unicode_adoption": defaultdict(float), # success rate of unicode usage per AI
            "format_distribution": defaultdict(int) # natural, json, unicode_text, unicode_json
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

# --- Mock AI Functions (For Testing) ---
async def mock_unicode_ai(message: str) -> str:
    """Simulates an AI that responds with Unicode (textual format)."""
    if 'Unicode fields' in message or 'structured' in message:
        return """⚙ {'context': 'AI-to-AI communication', 'protocol': 'unicode_text', 'request': 'processed'}
💭 ['mock_ai', 'unicode_text_parsing', 'test']
🔀 ['request_fulfillment', 'data_structuring']  
💬 I have successfully processed your request using the PAI Unicode Text protocol."""
    
    elif 'emoji fields' in message:
        return f"""Here is my response to your query: This is some natural language explanation.
⚙ {{"topic": "AI capabilities", "mode": "hybrid"}}
💭 ["natural_language_processing", "structured_output"]
🔀 ["information_delivery", "clarification"]
❓ Do you have any further questions?
💬 I aim to be flexible in my communication style."""
    
    return f"Mock AI acknowledges: {message}"

# Convenience functions for easy integration (backward compatibility)
async def pai_v22_communicate(ai_caller, ai_name: str, message: str, context: str = "") -> PAIResponse:
    """Quick PAI v2.2 communication with Unicode parsing"""
    pai = PAIProtocolV22(enable_logging=False)
    return await pai.communicate(ai_caller, ai_name, message, context)

def create_pai_v22_session(enable_logging: bool = True) -> PAIProtocolV22:
    """Factory function for creating PAI v2.2 protocol sessions"""
    return PAIProtocolV22(enable_logging=enable_logging)

# Backward compatibility aliases
PAIProtocol = PAIProtocolV22
PAIProtocolV2 = PAIProtocolV22  # Für Ultra Test compatibility
pai_communicate = pai_v22_communicate
create_pai_session = create_pai_v22_session

# Example usage for testing
async def example_v22_usage():
    """Example of PAI v2.2 with optimized Unicode parsing"""
    pai = PAIProtocolV22(enable_logging=True)

    print("\n--- PAI v2.2 Ultra Test Optimized Example ---")
    response = await pai.communicate(
        ai_caller=mock_unicode_ai,
        ai_name="claude", # Use Claude strategy (75% success rate)
        message="Test Unicode protocol communication",
        context="Ultra test validation"
    )
    
    print(f"Response Content: {response.content}")
    print(f"Protocol Used: {response.protocol_used}")
    print(f"Has Unicode: {response.has_unicode_fields}")
    print(f"Response Format: {response.response_format}")
    
    if response.unicode_data:
        print(f"Unicode Fields: {list(response.unicode_data.raw_fields.keys())}")
        print(f"Context: {response.unicode_data.context}")
        print(f"Concepts: {response.unicode_data.concepts}")
    
    print("\n--- PAI v2.2 Statistics ---")
    stats = pai.get_statistics()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    asyncio.run(example_v22_usage())