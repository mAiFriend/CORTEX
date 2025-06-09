#!/usr/bin/env python3
"""
CORTEX Context Processor - Smart Context Management (STABILIZED)
Handles intelligent context truncation and prompt building with robust error handling
"""

import re
from typing import Dict, List, Optional, Any
from cortex_types import AIResponse


class ContextProcessor:
    """Smart context management for multi-iteration AI conversations"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration and validation"""
        self.config = config
        self.context_config = config.get('context_management', {})
        self.truncation_config = self.context_config.get('truncation', {})
        self.front_loading_config = self.context_config.get('front_loading', {})
        
        # Default truncation settings with validation
        self.default_method = self.truncation_config.get('method', 'smart_sentence_aware')
        self.default_limit = self.truncation_config.get('limit_chars', 1200)
        
        # Validate truncation method
        valid_methods = {'smart_sentence_aware', 'sentence_aware', 'paragraph_aware', 'hard_cut'}
        if self.default_method not in valid_methods:
            print(f"⚠️  Invalid truncation method '{self.default_method}', using 'smart_sentence_aware'")
            self.default_method = 'smart_sentence_aware'
        
        # Validate limit
        if not isinstance(self.default_limit, int) or self.default_limit <= 0:
            print(f"⚠️  Invalid character limit '{self.default_limit}', using 1200")
            self.default_limit = 1200
        
        # Front-loading settings
        self.front_loading_enabled = self.front_loading_config.get('enabled', True)
        self.enforcement_level = self.front_loading_config.get('enforcement_level', 'suggested')
        
        # Validate enforcement level
        valid_levels = {'disabled', 'suggested', 'mandatory'}
        if self.enforcement_level not in valid_levels:
            print(f"⚠️  Invalid enforcement level '{self.enforcement_level}', using 'suggested'")
            self.enforcement_level = 'suggested'
    
    def smart_truncate(self, text: str, method: str = None, limit: int = None) -> str:
        """
        Smart truncation with multiple methods and comprehensive error handling:
        - sentence_aware: Cut at sentence boundaries
        - paragraph_aware: Cut at paragraph boundaries  
        - hard_cut: Simple character limit
        """
        # Input validation
        if not text or not isinstance(text, str):
            return ""
        
        method = method or self.default_method
        limit = limit or self.default_limit
        
        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            limit = self.default_limit
        
        if len(text) <= limit:
            return text
        
        try:
            if method == 'smart_sentence_aware' or method == 'sentence_aware':
                return self._truncate_sentence_aware(text, limit)
            elif method == 'paragraph_aware':
                return self._truncate_paragraph_aware(text, limit)
            elif method == 'hard_cut':
                return self._truncate_hard(text, limit)
            else:
                print(f"⚠️  Unknown truncation method '{method}', using sentence_aware")
                return self._truncate_sentence_aware(text, limit)
        except Exception as e:
            print(f"⚠️  Truncation failed with method '{method}': {e}")
            # Fallback to hard cut
            return self._truncate_hard(text, limit)
    
    def _truncate_sentence_aware(self, text: str, limit: int) -> str:
        """Truncate at sentence boundary with robust regex handling"""
        if len(text) <= limit:
            return text
        
        try:
            # Find sentences using multiple delimiters
            sentence_pattern = r'(?<=[.!?])\s+'
            sentences = re.split(sentence_pattern, text)
            
            result = ""
            for sentence in sentences:
                # Check if adding this sentence would exceed limit
                potential = result + sentence
                if len(potential) <= limit:
                    result = potential
                    # Add space between sentences if not the last one
                    if len(result) < len(text) and not result.endswith(('.', '!', '?')):
                        result += " "
                else:
                    break
            
            # Clean up and add ellipsis if truncated
            result = result.strip()
            if len(result) < len(text) and not result.endswith('...'):
                # Ensure we have space for ellipsis
                if len(result) + 3 > limit:
                    result = result[:limit-3]
                result += "..."
                
            return result if result else self._truncate_hard(text, limit)
            
        except Exception as e:
            print(f"⚠️  Sentence-aware truncation failed: {e}")
            return self._truncate_hard(text, limit)
    
    def _truncate_paragraph_aware(self, text: str, limit: int) -> str:
        """Truncate at paragraph boundary with error handling"""
        if len(text) <= limit:
            return text
        
        try:
            # Split by paragraph boundaries (double newlines)
            paragraphs = text.split('\n\n')
            
            result = ""
            for i, paragraph in enumerate(paragraphs):
                # Calculate potential length with paragraph separators
                separator = "\n\n" if i > 0 else ""
                potential = result + separator + paragraph
                
                if len(potential) <= limit:
                    result = potential
                else:
                    break
            
            # Clean up and add ellipsis if truncated
            result = result.strip()
            if len(result) < len(text) and not result.endswith('...'):
                if len(result) + 3 > limit:
                    result = result[:limit-3]
                result += "..."
            
            # Fallback to sentence-aware if no complete paragraph fits
            return result if result else self._truncate_sentence_aware(text, limit)
            
        except Exception as e:
            print(f"⚠️  Paragraph-aware truncation failed: {e}")
            return self._truncate_sentence_aware(text, limit)
    
    def _truncate_hard(self, text: str, limit: int) -> str:
        """Simple hard character cut with word boundary preference"""
        if len(text) <= limit:
            return text
        
        try:
            # Reserve space for ellipsis
            effective_limit = max(0, limit - 3)
            
            if effective_limit <= 0:
                return "..."
            
            # Try to cut at a word boundary
            cut_text = text[:effective_limit]
            last_space = cut_text.rfind(' ')
            
            # If we found a space in the last 20% of the cut, use it
            if last_space > effective_limit * 0.8:
                return cut_text[:last_space] + "..."
            else:
                return cut_text + "..."
                
        except Exception as e:
            print(f"⚠️  Hard truncation failed: {e}")
            return text[:max(0, limit-3)] + "..." if limit > 3 else text[:limit]
    
    def smart_truncate_all(self, responses: List[AIResponse]) -> Dict[str, str]:
        """Process all AI responses for next iteration context with error handling"""
        truncated_context = {}
        
        try:
            # Filter successful responses
            successful_responses = [r for r in responses if r.success and r.response]
            
            if not successful_responses:
                return {}
            
            # Calculate per-AI limits based on number of responses
            total_limit = self.context_config.get('total_limit_chars', 6000)
            per_ai_limit = max(200, total_limit // len(successful_responses))  # Minimum 200 chars per AI
            
            # Apply smart truncation to each response
            for response in successful_responses:
                try:
                    truncated = self.smart_truncate(
                        response.response,
                        method=self.default_method,
                        limit=per_ai_limit
                    )
                    if truncated:  # Only add non-empty truncated responses
                        truncated_context[response.ai_name] = truncated
                except Exception as e:
                    print(f"⚠️  Failed to truncate response from {response.ai_name}: {e}")
                    # Use fallback truncation
                    truncated_context[response.ai_name] = response.response[:per_ai_limit] + "..."
            
            return truncated_context
            
        except Exception as e:
            print(f"⚠️  Failed to process responses for context: {e}")
            return {}
    
    def build_iteration_prompt(self, ai_name: str, iteration: int, topic: str, 
                              previous_context: Dict[str, str], ruleset: Dict[str, Any]) -> str:
        """Dynamic prompt construction with embedded context and error handling"""
        try:
            # Get AI archetype
            ai_archetypes = {
                "claude": "Claude (Analytical Philosopher)",
                "chatgpt": "ChatGPT (Versatile Collaborator)", 
                "gemini": "Gemini (Creative Synthesizer)",
                "qwen": "Qwen (Efficient Processor)",
                "deepseek": "DeepSeek (Deep Reasoner)"
            }
            
            archetype = ai_archetypes.get(ai_name, f"{ai_name} (AI Collaborator)")
            
            # Build context from previous responses
            context_section = ""
            if previous_context:
                context_entries = []
                for ai, response in previous_context.items():
                    if ai != ai_name and response:  # Don't include own previous response
                        # Sanitize response content
                        sanitized_response = self._sanitize_content(response)
                        context_entries.append(f"{ai}: {sanitized_response}")
                
                if context_entries:
                    context_section = "\nPREVIOUS AI RESPONSES:\n" + "\n\n".join(context_entries) + "\n"
            
            # Apply front-loading rules if enabled
            front_loading_instruction = ""
            if self.front_loading_enabled:
                front_loading_instruction = self._build_front_loading_instruction()
            
            # Build ruleset parameters
            ruleset_params = ""
            if ruleset:
                ruleset_params = "\nACTIVE COMMUNICATION RULES:\n"
                for param, value in ruleset.items():
                    # Sanitize ruleset parameters
                    sanitized_param = self._sanitize_content(str(param))
                    sanitized_value = self._sanitize_content(str(value))
                    ruleset_params += f"- {sanitized_param}: {sanitized_value}\n"
            
            # Construct complete prompt
            prompt_parts = [
                f"Du bist {archetype} im CORTEX Framework.",
                f"\nTOPIC: {self._sanitize_content(topic)}",
                context_section,
                ruleset_params,
                front_loading_instruction,
                f"\nIteration {iteration}: Diskutiere das Thema aus deiner Perspektive. "
                "Beziehe dich auf andere AIs wenn relevant, bringe neue Einsichten ein, "
                "und sei authentisch in deiner Antwort.\n\nAntworte in 200-400 Wörtern."
            ]
            
            return "".join(filter(None, prompt_parts)).strip()
            
        except Exception as e:
            print(f"⚠️  Failed to build prompt for {ai_name}: {e}")
            # Fallback to simple prompt
            return f"Du bist {ai_name}. Diskutiere dieses Thema: {topic}"
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize content to prevent injection attacks and ensure clean prompts"""
        if not content or not isinstance(content, str):
            return ""
        
        try:
            # Remove potential injection patterns
            sanitized = content.strip()
            
            # Remove excessive whitespace
            sanitized = re.sub(r'\s+', ' ', sanitized)
            
            # Limit length to prevent extremely long inputs
            max_length = 5000
            if len(sanitized) > max_length:
                sanitized = sanitized[:max_length] + "..."
            
            return sanitized
            
        except Exception as e:
            print(f"⚠️  Content sanitization failed: {e}")
            return str(content)[:1000]  # Emergency fallback
    
    def _build_front_loading_instruction(self) -> str:
        """Build front-loading instruction based on enforcement level"""
        try:
            if self.enforcement_level == "mandatory":
                return ("\n\nIMPORTANT: Start your response with the key insight or conclusion first, "
                       "then provide supporting details.\n")
            elif self.enforcement_level == "suggested":
                return "\n\n(Consider starting with your main insight for clarity)\n"
            else:  # disabled
                return ""
        except Exception as e:
            print(f"⚠️  Failed to build front-loading instruction: {e}")
            return ""
    
    def calculate_context_limits(self) -> Dict[str, int]:
        """Calculate per-AI context limits based on configuration"""
        try:
            total_limit = self.context_config.get('total_limit_chars', 6000)
            ai_count = len(self.config.get('ai_team', []))
            
            if ai_count == 0:
                return {}
            
            # Base calculation: equal distribution with minimum per AI
            base_per_ai = max(200, total_limit // ai_count)
            
            # Create limits dictionary
            limits = {}
            for ai in self.config.get('ai_team', []):
                limits[ai] = base_per_ai
            
            return limits
            
        except Exception as e:
            print(f"⚠️  Failed to calculate context limits: {e}")
            return {}
    
    def extract_cross_references(self, responses: List[AIResponse]) -> List[Dict[str, str]]:
        """Extract cross-references between AI responses with error handling"""
        references = []
        
        try:
            ai_names = [r.ai_name for r in responses if r.success and r.response]
            
            for response in responses:
                if not response.success or not response.response:
                    continue
                
                # Look for mentions of other AIs
                for other_ai in ai_names:
                    if other_ai != response.ai_name:
                        # Pattern matching for references
                        patterns = [
                            f"{other_ai} mentioned",
                            f"{other_ai} said",
                            f"{other_ai}'s point",
                            f"building on {other_ai}",
                            f"as {other_ai} noted",
                            f"{other_ai} suggested",
                            f"{other_ai} argues",
                            f"agree with {other_ai}",
                            f"disagree with {other_ai}"
                        ]
                        
                        response_lower = response.response.lower()
                        for pattern in patterns:
                            if pattern.lower() in response_lower:
                                references.append({
                                    'from': response.ai_name,
                                    'to': other_ai,
                                    'pattern': pattern,
                                    'iteration': response.iteration
                                })
                                break  # Only count first match per AI pair
            
            return references
            
        except Exception as e:
            print(f"⚠️  Failed to extract cross-references: {e}")
            return []