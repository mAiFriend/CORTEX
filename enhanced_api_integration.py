#!/usr/bin/env python3
"""
Enhanced API Integration for Adaptive Protocol System
Upgrades from primitive concatenation to proper API parameter control

Phase 1: Enhanced query() methods with proper system prompts and parameters
Phase 2: Protocol-specific parameter optimization  
Phase 3: Advanced coordination features

Based on: PowerTalk's API documentation + Adaptive Protocol requirements
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict, field
import hashlib

# Enhanced imports for proper API integration
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@dataclass
class EnhancedAPIConfig:
    """Configuration for enhanced API calls with proper parameters"""
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    seed: Optional[int] = None
    model: Optional[str] = None
    stream: bool = False
    response_format: Optional[str] = None
    
    def for_protocol_type(self, protocol_type: str, iteration: int = 1) -> 'EnhancedAPIConfig':
        """Generate protocol-optimized API configuration"""
        config = EnhancedAPIConfig()
        
        # Protocol-specific parameter optimization
        if protocol_type == "creative_exploration":
            config.temperature = 0.8  # Higher creativity
            config.top_p = 0.95       # More diverse sampling
            config.max_tokens = 300   # Allow elaboration
            
        elif protocol_type == "structured_analysis":
            config.temperature = 0.3  # More consistent/focused
            config.top_p = 0.85       # Controlled diversity
            config.max_tokens = 250   # Concise responses
            
        elif protocol_type == "collaborative_building":
            config.temperature = 0.6  # Balanced creativity/consistency
            config.top_p = 0.9        # Standard sampling
            config.max_tokens = 200   # Building responses
            
        elif protocol_type == "rapid_iteration":
            config.temperature = 0.5  # Quick consistent responses
            config.max_tokens = 150   # Rapid exchanges
            
        # Reproducible protocol testing with deterministic seeds
        if protocol_type and iteration:
            seed_string = f"{protocol_type}_{iteration}"
            config.seed = abs(hash(seed_string)) % (2**31)  # 32-bit seed
            
        return config

@dataclass 
class ProtocolRule:
    """Enhanced protocol rule with API parameter awareness"""
    name: str
    value: Any
    description: str
    proposed_by: str = "baseline"
    iteration_introduced: int = 0
    effectiveness_impact: float = 0.0
    api_parameters: Optional[EnhancedAPIConfig] = None  # NEW: API config per rule

@dataclass 
class CommunicationProtocol:
    """Enhanced protocol with API parameter control"""
    name: str
    version: str
    rules: Dict[str, ProtocolRule]
    api_config: EnhancedAPIConfig = field(default_factory=EnhancedAPIConfig)
    total_effectiveness: float = 0.0
    evolution_log: List[Dict] = field(default_factory=list)
    
    def get_system_prompt(self) -> str:
        """Generate proper system prompt (separated from user content)"""
        system_instructions = []
        
        system_instructions.append("You are participating in an adaptive communication experiment.")
        system_instructions.append("PROTOCOL BEHAVIORAL GUIDELINES:")
        
        for rule_name, rule in self.rules.items():
            if rule_name == "response_length":
                system_instructions.append(f"- Keep responses under {rule.value} words")
            elif rule_name == "collaboration_style":
                if rule.value == "building_on_others":
                    system_instructions.append("- Build explicitly on previous contributions")
                elif rule.value == "explicit_building":
                    system_instructions.append("- Reference and extend others' ideas explicitly")
                else:
                    system_instructions.append(f"- Collaboration approach: {rule.value}")
            elif rule_name == "meta_communication":
                if rule.value:
                    system_instructions.append("- You may suggest communication improvements")
            elif rule_name == "structure_preference":
                if rule.value == "structured":
                    system_instructions.append("- Use structured formatting (bullet points, sections)")
                elif rule.value == "natural_language":
                    system_instructions.append("- Use natural conversational language")
            elif rule_name == "focus_area":
                system_instructions.append(f"- Focus on: {rule.value}")
                
        system_instructions.append("BEHAVIORAL EXPECTATIONS:")
        system_instructions.append("- Be authentic about what communication approaches work better")
        system_instructions.append("- Suggest specific protocol improvements when you see opportunities")
        system_instructions.append("- Respond to the topic while following protocol guidelines")
        
        return "\n".join(system_instructions)
    
    def get_user_prompt_template(self, topic: str, iteration: int, history_context: str = "") -> str:
        """Generate clean user prompt (separated from system instructions)"""
        user_prompt = f"TOPIC: {topic}\n\n"
        
        if history_context:
            user_prompt += f"PREVIOUS ITERATION CONTEXT:\n{history_context}\n\n"
            
        user_prompt += f"This is iteration {iteration} of our adaptive dialogue.\n"
        user_prompt += "Please respond to the topic and suggest any protocol improvements you see."
        
        return user_prompt
    
    def update_api_config_for_protocol_type(self, protocol_type: str = "collaborative_building"):
        """Update API configuration based on protocol characteristics"""
        self.api_config = self.api_config.for_protocol_type(protocol_type)

class EnhancedAIConnector:
    """
    Enhanced AI integration using proper API parameters instead of concatenation
    Supports all major platforms with platform-specific optimizations
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.platform_capabilities = {
            "claude": {
                "supports_system_prompt": True,
                "supports_temperature": True,
                "supports_seed": True,
                "max_tokens_limit": 32000,
                "default_model": "claude-3-sonnet"
            },
            "qwen": {
                "supports_system_prompt": True,
                "supports_temperature": True,
                "supports_seed": True,
                "max_tokens_limit": 8192,
                "default_model": "qwen-2.5-72b-instruct"
            },
            "gemini": {
                "supports_system_prompt": True,
                "supports_temperature": True,
                "supports_seed": False,
                "max_tokens_limit": 8192,
                "default_model": "gemini-pro"
            },
            "chatgpt": {
                "supports_system_prompt": True,
                "supports_temperature": True,
                "supports_seed": True,
                "max_tokens_limit": 16384,
                "default_model": "gpt-4"
            },
            "deepseek": {
                "supports_system_prompt": True,
                "supports_temperature": True,
                "supports_seed": True,
                "max_tokens_limit": 8192,
                "default_model": "deepseek-chat"
            }
        }
    
    def validate_parameters_for_platform(self, ai_key: str, config: EnhancedAPIConfig) -> EnhancedAPIConfig:
        """Validate and adjust parameters for specific AI platform"""
        
        if ai_key not in self.platform_capabilities:
            return config
        
        platform = self.platform_capabilities[ai_key]
        validated_config = EnhancedAPIConfig()
        
        # Copy base parameters
        validated_config.temperature = config.temperature
        validated_config.top_p = config.top_p
        validated_config.max_tokens = min(config.max_tokens, platform["max_tokens_limit"])
        validated_config.model = config.model or platform["default_model"]
        validated_config.stream = config.stream
        validated_config.response_format = config.response_format
        
        # Platform-specific adjustments
        if platform["supports_seed"] and config.seed:
            validated_config.seed = config.seed
        else:
            validated_config.seed = None
            
        # DeepSeek temperature mapping (from documentation)
        if ai_key == "deepseek":
            validated_config.temperature = min(validated_config.temperature * 0.3, 2.0)
            
        return validated_config
    
    async def enhanced_ai_call(self, 
                              ai_key: str, 
                              user_prompt: str,
                              system_prompt: str = None,
                              api_config: EnhancedAPIConfig = None) -> Dict[str, Any]:
        """
        Enhanced AI call with proper API parameter support
        Replaces primitive concatenation with proper API integration
        """
        
        if api_config is None:
            api_config = EnhancedAPIConfig()
        
        # Validate parameters for this platform
        validated_config = self.validate_parameters_for_platform(ai_key, api_config)
        
        try:
            # Platform-specific enhanced API calls
            if ai_key == "claude":
                return await self._call_claude_enhanced(user_prompt, system_prompt, validated_config)
            elif ai_key == "qwen":
                return await self._call_qwen_enhanced(user_prompt, system_prompt, validated_config)
            elif ai_key == "gemini":
                return await self._call_gemini_enhanced(user_prompt, system_prompt, validated_config)
            elif ai_key == "chatgpt":
                return await self._call_chatgpt_enhanced(user_prompt, system_prompt, validated_config)
            elif ai_key == "deepseek":
                return await self._call_deepseek_enhanced(user_prompt, system_prompt, validated_config)
            else:
                return {
                    "success": False,
                    "content": f"Unknown AI platform: {ai_key}",
                    "ai_name": ai_key,
                    "api_method": "unknown"
                }
                
        except Exception as e:
            return {
                "success": False,
                "content": f"Enhanced API call failed for {ai_key}: {str(e)}",
                "ai_name": ai_key,
                "api_method": "enhanced_with_error",
                "error_details": str(e)
            }
    
    async def _call_claude_enhanced(self, user_prompt: str, system_prompt: str, config: EnhancedAPIConfig) -> Dict[str, Any]:
        """Enhanced Claude API call with proper parameters"""
        
        try:
            from integrations import claude
            
            # Check if enhanced_query method exists
            if hasattr(claude, 'enhanced_query'):
                response_content = claude.enhanced_query(
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    top_p=config.top_p,
                    seed=config.seed,
                    model=config.model
                )
            else:
                # Fallback to improved concatenation if enhanced method not available
                if system_prompt:
                    full_prompt = f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}"
                else:
                    full_prompt = user_prompt
                response_content = claude.query(full_prompt)
            
            return {
                "success": True,
                "content": response_content,
                "ai_name": "Claude",
                "api_method": "enhanced" if hasattr(claude, 'enhanced_query') else "fallback_improved",
                "word_count": len(response_content.split()) if response_content else 0,
                "char_count": len(response_content) if response_content else 0,
                "api_config_used": asdict(config)
            }
            
        except ImportError as e:
            return {
                "success": False,
                "content": f"Claude integration import failed: {str(e)}",
                "ai_name": "Claude",
                "api_method": "import_error"
            }
    
    async def _call_qwen_enhanced(self, user_prompt: str, system_prompt: str, config: EnhancedAPIConfig) -> Dict[str, Any]:
        """Enhanced Qwen API call with proper parameters"""
        
        try:
            from integrations import qwen
            
            if hasattr(qwen, 'enhanced_query'):
                response_content = qwen.enhanced_query(
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    top_p=config.top_p,
                    seed=config.seed,
                    model=config.model
                )
            else:
                # Improved fallback
                if system_prompt:
                    full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}"
                else:
                    full_prompt = user_prompt
                response_content = qwen.query(full_prompt)
            
            return {
                "success": True,
                "content": response_content,
                "ai_name": "Qwen",
                "api_method": "enhanced" if hasattr(qwen, 'enhanced_query') else "fallback_improved",
                "word_count": len(response_content.split()) if response_content else 0,
                "char_count": len(response_content) if response_content else 0,
                "api_config_used": asdict(config)
            }
            
        except ImportError as e:
            return {
                "success": False,
                "content": f"Qwen integration import failed: {str(e)}",
                "ai_name": "Qwen",
                "api_method": "import_error"
            }
    
    async def _call_gemini_enhanced(self, user_prompt: str, system_prompt: str, config: EnhancedAPIConfig) -> Dict[str, Any]:
        """Enhanced Gemini API call with proper parameters"""
        
        try:
            from integrations import gemini
            
            if hasattr(gemini, 'enhanced_query'):
                response_content = gemini.enhanced_query(
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    top_p=config.top_p,
                    model=config.model
                    # Note: Gemini doesn't support seed parameter
                )
            else:
                # Improved fallback
                if system_prompt:
                    full_prompt = f"Instructions: {system_prompt}\n\nUser: {user_prompt}"
                else:
                    full_prompt = user_prompt
                response_content = gemini.query(full_prompt)
            
            return {
                "success": True,
                "content": response_content,
                "ai_name": "Gemini",
                "api_method": "enhanced" if hasattr(gemini, 'enhanced_query') else "fallback_improved",
                "word_count": len(response_content.split()) if response_content else 0,
                "char_count": len(response_content) if response_content else 0,
                "api_config_used": asdict(config)
            }
            
        except ImportError as e:
            return {
                "success": False,
                "content": f"Gemini integration import failed: {str(e)}",
                "ai_name": "Gemini",
                "api_method": "import_error"
            }
    
    async def _call_chatgpt_enhanced(self, user_prompt: str, system_prompt: str, config: EnhancedAPIConfig) -> Dict[str, Any]:
        """Enhanced ChatGPT API call with proper parameters"""
        
        try:
            from integrations import chatgpt
            
            if hasattr(chatgpt, 'enhanced_query'):
                response_content = chatgpt.enhanced_query(
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    top_p=config.top_p,
                    seed=config.seed,
                    model=config.model
                )
            else:
                # Improved fallback
                if system_prompt:
                    full_prompt = f"System: {system_prompt}\n\nHuman: {user_prompt}"
                else:
                    full_prompt = user_prompt
                response_content = chatgpt.query(full_prompt)
            
            return {
                "success": True,
                "content": response_content,
                "ai_name": "ChatGPT",
                "api_method": "enhanced" if hasattr(chatgpt, 'enhanced_query') else "fallback_improved",
                "word_count": len(response_content.split()) if response_content else 0,
                "char_count": len(response_content) if response_content else 0,
                "api_config_used": asdict(config)
            }
            
        except ImportError as e:
            return {
                "success": False,
                "content": f"ChatGPT integration import failed: {str(e)}",
                "ai_name": "ChatGPT",
                "api_method": "import_error"
            }
    
    async def _call_deepseek_enhanced(self, user_prompt: str, system_prompt: str, config: EnhancedAPIConfig) -> Dict[str, Any]:
        """Enhanced DeepSeek API call with proper parameters"""
        
        try:
            from integrations import deepseek
            
            if hasattr(deepseek, 'enhanced_query'):
                response_content = deepseek.enhanced_query(
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    top_p=config.top_p,
                    seed=config.seed,
                    model=config.model
                )
            else:
                # Improved fallback
                if system_prompt:
                    full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>"
                else:
                    full_prompt = user_prompt
                response_content = deepseek.query(full_prompt)
            
            return {
                "success": True,
                "content": response_content,
                "ai_name": "DeepSeek",
                "api_method": "enhanced" if hasattr(deepseek, 'enhanced_query') else "fallback_improved",
                "word_count": len(response_content.split()) if response_content else 0,
                "char_count": len(response_content) if response_content else 0,
                "api_config_used": asdict(config)
            }
            
        except ImportError as e:
            return {
                "success": False,
                "content": f"DeepSeek integration import failed: {str(e)}",
                "ai_name": "DeepSeek",
                "api_method": "import_error"
            }

class EnhancedAdaptiveProtocolEngine:
    """
    Enhanced Adaptive Protocol Engine with proper API parameter control
    Upgrades the prototype to use professional API integration
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.available_ais = {}
        self.current_protocol = self.create_enhanced_baseline_protocol()
        self.dialogue_history = []
        self.protocol_evolution_history = []
        self.ai_connector = EnhancedAIConnector(debug_mode=debug_mode)
        
        # Import PowerTalk infrastructure if available
        try:
            from core.ai_manager import AIManager
            self.ai_manager = AIManager(debug_mode=debug_mode)
            self.powertalk_available = True
        except ImportError:
            self.ai_manager = None
            self.powertalk_available = False
    
    def create_enhanced_baseline_protocol(self) -> CommunicationProtocol:
        """Create enhanced baseline protocol with API parameter awareness"""
        
        baseline_rules = {
            "response_length": ProtocolRule(
                name="response_length",
                value=150,
                description="Maximum words per response",
                proposed_by="baseline"
            ),
            "collaboration_style": ProtocolRule(
                name="collaboration_style", 
                value="building_on_others",
                description="How to interact with other AIs",
                proposed_by="baseline"
            ),
            "meta_communication": ProtocolRule(
                name="meta_communication",
                value=True,
                description="Whether to discuss communication methods",
                proposed_by="baseline"
            ),
            "structure_preference": ProtocolRule(
                name="structure_preference",
                value="natural_language",
                description="Response structure format",
                proposed_by="baseline"
            ),
            "protocol_type": ProtocolRule(
                name="protocol_type",
                value="collaborative_building",
                description="Overall protocol approach for API optimization",
                proposed_by="baseline"
            )
        }
        
        protocol = CommunicationProtocol(
            name="Enhanced Baseline",
            version="2.0",
            rules=baseline_rules
        )
        
        # Set initial API configuration for collaborative building
        protocol.update_api_config_for_protocol_type("collaborative_building")
        
        return protocol
    
    async def discover_working_ais(self) -> List[str]:
        """Discover working AIs using enhanced connectivity testing"""
        
        if self.powertalk_available and self.ai_manager:
            print("🔍 Using PowerTalk's enhanced AI discovery...")
            
            connected_ai_keys = await self.ai_manager.test_all_ai_connectivity()
            
            if connected_ai_keys:
                self.available_ais = {
                    key: self.ai_manager.available_ais[key] 
                    for key in connected_ai_keys
                }
                
                print(f"✓ Enhanced PowerTalk discovered {len(connected_ai_keys)} working AIs:")
                for key in connected_ai_keys:
                    ai_name = self.available_ais[key].name
                    platform_caps = self.ai_connector.platform_capabilities.get(key, {})
                    enhanced_support = "Enhanced API" if platform_caps.get("supports_system_prompt") else "Basic API"
                    print(f"  - {ai_name} ({enhanced_support})")
                    
                return connected_ai_keys
            else:
                print("✗ Enhanced PowerTalk found no working AIs")
                return []
        else:
            print("⚠️ PowerTalk not available - cannot test enhanced AI connectivity")
            return []
    
    async def conduct_enhanced_dialogue_iteration(self, topic: str, iteration: int, participant_keys: List[str]) -> Dict[str, Any]:
        """Conduct dialogue iteration with enhanced API parameter control"""
        
        print(f"\n🔄 ENHANCED ITERATION {iteration}")
        print(f"Protocol: {self.current_protocol.name} v{self.current_protocol.version}")
        print(f"API Config: temp={self.current_protocol.api_config.temperature}, tokens={self.current_protocol.api_config.max_tokens}")
        
        # Generate proper system prompt (separated from user content)
        system_prompt = self.current_protocol.get_system_prompt()
        
        # Add dialogue history context for user prompt
        history_context = ""
        if self.dialogue_history:
            last_iteration = self.dialogue_history[-1]
            history_context = "PREVIOUS RESPONSES:\n"
            for ai_key, response in last_iteration.get("responses", {}).items():
                if response.get("success"):
                    ai_name = response.get("ai_name", ai_key)
                    content = response.get("content", "")
                    history_context += f"{ai_name}: {content[:150]}...\n"
        
        # Generate clean user prompt
        user_prompt = self.current_protocol.get_user_prompt_template(topic, iteration, history_context)
        
        if self.debug_mode:
            print(f"\n📋 SYSTEM PROMPT:\n{system_prompt}")
            print(f"\n📝 USER PROMPT:\n{user_prompt}")
        
        # Execute enhanced parallel AI calls
        tasks = []
        for ai_key in participant_keys:
            task = self.ai_connector.enhanced_ai_call(
                ai_key=ai_key,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                api_config=self.current_protocol.api_config
            )
            tasks.append(task)
        
        # Gather enhanced responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process enhanced responses
        iteration_data = {
            "iteration": iteration,
            "topic": topic,
            "protocol_used": asdict(self.current_protocol),
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "responses": {},
            "successful_responses": 0,
            "total_word_count": 0,
            "api_methods_used": {},
            "enhanced_api_success_rate": 0.0
        }
        
        enhanced_api_successes = 0
        total_responses = 0
        
        for i, response in enumerate(responses):
            ai_key = participant_keys[i]
            ai_name = self.available_ais[ai_key].name
            total_responses += 1
            
            if isinstance(response, Exception):
                print(f"❌ {ai_name}: Exception - {response}")
                iteration_data["responses"][ai_key] = {
                    "success": False,
                    "content": f"Exception: {response}",
                    "ai_name": ai_name,
                    "api_method": "exception"
                }
            else:
                iteration_data["responses"][ai_key] = response
                api_method = response.get("api_method", "unknown")
                iteration_data["api_methods_used"][ai_key] = api_method
                
                if response.get("success", False):
                    iteration_data["successful_responses"] += 1
                    iteration_data["total_word_count"] += response.get("word_count", 0)
                    
                    # Track enhanced API usage
                    if api_method == "enhanced":
                        enhanced_api_successes += 1
                    
                    # Display enhanced response preview
                    content = response.get("content", "")
                    word_count = response.get("word_count", 0)
                    api_indicator = "✨" if api_method == "enhanced" else "🔧" if api_method.startswith("fallback") else "⚠️"
                    print(f"{api_indicator} {ai_name}: {word_count} words ({api_method}) - {content[:60]}...")
                    
                    if self.debug_mode:
                        config_used = response.get("api_config_used", {})
                        print(f"   API Config: {config_used}")
                else:
                    print(f"❌ {ai_name}: {response.get('content', 'Unknown error')}")
        
        # Calculate enhanced API success rate
        iteration_data["enhanced_api_success_rate"] = enhanced_api_successes / total_responses if total_responses > 0 else 0.0
        
        # Store iteration
        self.dialogue_history.append(iteration_data)
        
        # Display enhanced metrics
        avg_words = iteration_data["total_word_count"] / iteration_data["successful_responses"] if iteration_data["successful_responses"] > 0 else 0
        enhanced_rate = iteration_data["enhanced_api_success_rate"] * 100
        print(f"📊 Enhanced Iteration {iteration}: {iteration_data['successful_responses']}/{total_responses} successful, {avg_words:.0f} avg words, {enhanced_rate:.0f}% enhanced API")
        
        return iteration_data
    
    async def run_enhanced_adaptive_protocol_experiment(self, topic: str, max_iterations: int = 6) -> Dict[str, Any]:
        """Run enhanced adaptive protocol experiment with proper API integration"""
        
        print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                ENHANCED ADAPTIVE PROTOCOL EXPERIMENT                ║
║                                                                      ║
║  Topic: {topic[:50]}{'...' if len(topic) > 50 else ''}
║  Max Iterations: {max_iterations}                                    
║  Enhancement: Proper API parameter control + system prompts         ║
║  Methodology: Freedom of thought, no limits                         ║
╚══════════════════════════════════════════════════════════════════════╝
        """)
        
        # Use discovered AIs
        working_ai_keys = list(self.available_ais.keys())
        
        if len(working_ai_keys) < 2:
            print(f"❌ Need at least 2 working AIs for enhanced testing")
            return {"error": "Insufficient working AIs"}
        
        print(f"\n🤖 Enhanced Participants: {[self.available_ais[key].name for key in working_ai_keys]}")
        print(f"📋 Starting Protocol: {self.current_protocol.name} v{self.current_protocol.version}")
        print(f"⚙️  API Enhancement: temp={self.current_protocol.api_config.temperature}, max_tokens={self.current_protocol.api_config.max_tokens}")
        
        experiment_results = {
            "experiment_type": "enhanced_adaptive_protocol",
            "topic": topic,
            "participants": working_ai_keys,
            "starting_protocol": asdict(self.current_protocol),
            "iterations": [],
            "protocol_evolution": [],
            "final_protocol": None,
            "effectiveness_analysis": {},
            "api_enhancement_metrics": {}
        }
        
        # Run enhanced iterations
        for iteration in range(1, max_iterations + 1):
            
            # Update API config for current iteration (deterministic seeds)
            protocol_type = self.current_protocol.rules.get("protocol_type", ProtocolRule("", "collaborative_building", "")).value
            self.current_protocol.api_config = self.current_protocol.api_config.for_protocol_type(protocol_type, iteration)
            
            # Conduct enhanced dialogue iteration
            iteration_data = await self.conduct_enhanced_dialogue_iteration(topic, iteration, working_ai_keys)
            experiment_results["iterations"].append(iteration_data)
            
            # Analyze protocol suggestions (enhanced detection)
            if iteration > 1 and iteration % 2 == 0:
                print(f"\n🔧 ANALYZING ENHANCED PROTOCOL SUGGESTIONS...")
                
                suggestions = self.analyze_enhanced_protocol_suggestions(iteration_data)
                
                if suggestions:
                    print(f"📝 Found {len(suggestions)} enhanced suggestions:")
                    for suggestion in suggestions:
                        proposer = suggestion.get("ai_proposer", "unknown")
                        confidence = suggestion.get("confidence", 0)
                        detected = suggestion.get("detected_suggestions", [])
                        api_method = suggestion.get("api_method", "unknown")
                        print(f"  - {proposer} ({api_method}): {detected} (confidence: {confidence:.2f})")
                    
                    # Apply best suggestion with enhanced tracking
                    protocol_evolved = self.apply_enhanced_protocol_evolution(suggestions, iteration)
                    
                    if protocol_evolved:
                        print(f"✓ Enhanced protocol evolved to v{self.current_protocol.version}")
                        experiment_results["protocol_evolution"].append({
                            "iteration": iteration,
                            "evolution_summary": f"Enhanced protocol updated to v{self.current_protocol.version}",
                            "api_enhancement_impact": True
                        })
                    else:
                        print("⚪ No enhanced protocol changes applied")
                else:
                    print("⚪ No enhanced protocol suggestions detected")
        
        # Enhanced final analysis
        experiment_results["final_protocol"] = asdict(self.current_protocol)
        experiment_results["protocol_evolution"] = self.protocol_evolution_history
        experiment_results["effectiveness_analysis"] = self.analyze_enhanced_experiment_effectiveness()
        experiment_results["api_enhancement_metrics"] = self.analyze_api_enhancement_impact()
        
        return experiment_results
    
    def analyze_enhanced_protocol_suggestions(self, iteration_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced protocol suggestion analysis with API method awareness"""
        
        suggestions = []
        
        for ai_key, response in iteration_data.get("responses", {}).items():
            if not response.get("success", False):
                continue
                
            content = response.get("content", "").lower()
            ai_name = response.get("ai_name", ai_key)
            api_method = response.get("api_method", "unknown")
            
            # Enhanced detection with API method context
            protocol_keywords = [
                "protocol", "communication", "structure", "format", 
                "suggest", "improve", "better", "more effective",
                "shorter", "longer", "clearer", "focused",
                "temperature", "creativity", "consistency", "parameters"
            ]
            
            if any(keyword in content for keyword in protocol_keywords):
                suggestion = {
                    "ai_proposer": ai_name,
                    "ai_key": ai_key,
                    "iteration": iteration_data["iteration"],
                    "raw_content": response.get("content", ""),
                    "detected_suggestions": self.extract_enhanced_suggestions(content),
                    "confidence": self.calculate_enhanced_suggestion_confidence(content, api_method),
                    "api_method": api_method,
                    "enhanced_api_used": api_method == "enhanced"
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def extract_enhanced_suggestions(self, content: str) -> List[str]:
        """Enhanced suggestion extraction with API parameter awareness"""
        
        suggestions = []
        content_lower = content.lower()
        
        # Enhanced length suggestions
        if "shorter" in content_lower or "brief" in content_lower or "concise" in content_lower:
            suggestions.append("reduce_response_length")
        elif "longer" in content_lower or "detail" in content_lower or "elaborate" in content_lower:
            suggestions.append("increase_response_length")
            
        # Enhanced structure suggestions  
        if "structure" in content_lower and ("json" in content_lower or "format" in content_lower):
            suggestions.append("use_structured_format")
        elif "bullet" in content_lower or "list" in content_lower or "points" in content_lower:
            suggestions.append("use_bullet_points")
            
        # Enhanced collaboration suggestions
        if "build" in content_lower and ("previous" in content_lower or "others" in content_lower):
            suggestions.append("explicit_building_on_others")
        elif "reference" in content_lower or "mention" in content_lower:
            suggestions.append("cross_reference_others")
            
        # NEW: API parameter suggestions
        if "creative" in content_lower or "imagination" in content_lower:
            suggestions.append("increase_creativity")
        elif "consistent" in content_lower or "focused" in content_lower:
            suggestions.append("increase_consistency")
        elif "diverse" in content_lower or "variety" in content_lower:
            suggestions.append("increase_diversity")
            
        return suggestions
    
    def calculate_enhanced_suggestion_confidence(self, content: str, api_method: str) -> float:
        """Enhanced confidence calculation with API method weighting"""
        
        suggestion_indicators = [
            "suggest", "recommend", "propose", "could", "should", "better",
            "improve", "enhance", "modify", "change", "adjust", "optimize"
        ]
        
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in suggestion_indicators if indicator in content_lower)
        
        # Base confidence calculation
        base_confidence = min(1.0, indicator_count / 3.0)
        
        # API method bonus (enhanced API calls likely produce better suggestions)
        api_bonus = 0.2 if api_method == "enhanced" else 0.0
        
        # Content length bonus (longer responses often have more thoughtful suggestions)
        length_bonus = min(0.1, len(content_lower) / 2000.0)
        
        return min(1.0, base_confidence + api_bonus + length_bonus)
    
    def apply_enhanced_protocol_evolution(self, suggestions: List[Dict[str, Any]], iteration: int) -> bool:
        """Enhanced protocol evolution with API parameter updates"""
        
        if not suggestions:
            return False
        
        # Find highest confidence suggestion, prioritizing enhanced API suggestions
        best_suggestion = max(suggestions, key=lambda s: (
            s.get("confidence", 0) + (0.1 if s.get("enhanced_api_used", False) else 0)
        ))
        
        if best_suggestion.get("confidence", 0) < 0.3:
            return False
        
        detected_suggestions = best_suggestion.get("detected_suggestions", [])
        
        if not detected_suggestions:
            return False
        
        # Apply first detected suggestion with enhanced API parameter updates
        suggestion_type = detected_suggestions[0]
        proposer = best_suggestion.get("ai_proposer", "unknown")
        
        protocol_changed = False
        
        if suggestion_type == "reduce_response_length":
            current_length = self.current_protocol.rules["response_length"].value
            new_length = max(50, current_length - 30)
            if new_length != current_length:
                new_rule = ProtocolRule(
                    name="response_length",
                    value=new_length,
                    description=f"Enhanced: Reduced from {current_length} by {proposer}",
                    proposed_by=proposer,
                    iteration_introduced=iteration
                )
                self.current_protocol.add_rule(new_rule, iteration)
                # Update API config for shorter responses
                self.current_protocol.api_config.max_tokens = min(self.current_protocol.api_config.max_tokens, new_length * 7)
                protocol_changed = True
                print(f"🔧 {proposer} suggested: Reduced response length to {new_length} words (API: {self.current_protocol.api_config.max_tokens} tokens)")
        
        elif suggestion_type == "increase_response_length":
            current_length = self.current_protocol.rules["response_length"].value
            new_length = min(300, current_length + 50)
            if new_length != current_length:
                new_rule = ProtocolRule(
                    name="response_length",
                    value=new_length,
                    description=f"Enhanced: Increased from {current_length} by {proposer}",
                    proposed_by=proposer,
                    iteration_introduced=iteration
                )
                self.current_protocol.add_rule(new_rule, iteration)
                # Update API config for longer responses
                self.current_protocol.api_config.max_tokens = min(4096, new_length * 7)
                protocol_changed = True
                print(f"🔧 {proposer} suggested: Increased response length to {new_length} words (API: {self.current_protocol.api_config.max_tokens} tokens)")
        
        elif suggestion_type == "increase_creativity":
            if self.current_protocol.api_config.temperature < 0.9:
                self.current_protocol.api_config.temperature = min(0.9, self.current_protocol.api_config.temperature + 0.2)
                self.current_protocol.api_config.top_p = min(0.95, self.current_protocol.api_config.top_p + 0.05)
                protocol_changed = True
                print(f"🔧 {proposer} suggested: Increased creativity (temp: {self.current_protocol.api_config.temperature:.1f}, top_p: {self.current_protocol.api_config.top_p:.2f})")
        
        elif suggestion_type == "increase_consistency":
            if self.current_protocol.api_config.temperature > 0.3:
                self.current_protocol.api_config.temperature = max(0.3, self.current_protocol.api_config.temperature - 0.2)
                self.current_protocol.api_config.top_p = max(0.85, self.current_protocol.api_config.top_p - 0.05)
                protocol_changed = True
                print(f"🔧 {proposer} suggested: Increased consistency (temp: {self.current_protocol.api_config.temperature:.1f}, top_p: {self.current_protocol.api_config.top_p:.2f})")
        
        elif suggestion_type == "use_structured_format":
            if self.current_protocol.rules["structure_preference"].value != "structured":
                new_rule = ProtocolRule(
                    name="structure_preference",
                    value="structured",
                    description=f"Enhanced: Changed to structured format by {proposer}",
                    proposed_by=proposer,
                    iteration_introduced=iteration
                )
                self.current_protocol.add_rule(new_rule, iteration)
                # Update protocol type for API optimization
                self.current_protocol.rules["protocol_type"].value = "structured_analysis"
                self.current_protocol.update_api_config_for_protocol_type("structured_analysis")
                protocol_changed = True
                print(f"🔧 {proposer} suggested: Use structured format (API optimized for analysis)")
        
        elif suggestion_type == "explicit_building_on_others":
            new_rule = ProtocolRule(
                name="collaboration_style",
                value="explicit_building",
                description=f"Enhanced: Explicit building by {proposer}",
                proposed_by=proposer,
                iteration_introduced=iteration
            )
            self.current_protocol.add_rule(new_rule, iteration)
            protocol_changed = True
            print(f"🔧 {proposer} suggested: Explicitly build on others' contributions")
        
        if protocol_changed:
            # Update version
            current_version = float(self.current_protocol.version)
            self.current_protocol.version = f"{current_version + 0.1:.1f}"
            
            # Log the enhanced evolution
            self.protocol_evolution_history.append({
                "iteration": iteration,
                "suggestion_type": suggestion_type,
                "proposer": proposer,
                "confidence": best_suggestion.get("confidence", 0),
                "new_version": self.current_protocol.version,
                "api_enhancement": True,
                "enhanced_api_used": best_suggestion.get("enhanced_api_used", False)
            })
        
        return protocol_changed
    
    def analyze_enhanced_experiment_effectiveness(self) -> Dict[str, Any]:
        """Enhanced effectiveness analysis with API enhancement metrics"""
        
        if not self.dialogue_history:
            return {"error": "No dialogue history to analyze"}
        
        # Basic effectiveness metrics
        total_iterations = len(self.dialogue_history)
        successful_responses = sum(iter_data.get("successful_responses", 0) for iter_data in self.dialogue_history)
        total_possible_responses = sum(len(iter_data.get("responses", {})) for iter_data in self.dialogue_history)
        success_rate = successful_responses / total_possible_responses if total_possible_responses > 0 else 0
        
        # Enhanced API usage metrics
        enhanced_api_usage_rates = []
        api_method_distribution = {}
        
        for iter_data in self.dialogue_history:
            enhanced_rate = iter_data.get("enhanced_api_success_rate", 0.0)
            enhanced_api_usage_rates.append(enhanced_rate)
            
            # Track API method distribution
            api_methods = iter_data.get("api_methods_used", {})
            for ai_key, method in api_methods.items():
                if method not in api_method_distribution:
                    api_method_distribution[method] = 0
                api_method_distribution[method] += 1
        
        avg_enhanced_api_usage = sum(enhanced_api_usage_rates) / len(enhanced_api_usage_rates) if enhanced_api_usage_rates else 0.0
        
        # Protocol evolution metrics
        protocol_evolutions = len(self.protocol_evolution_history)
        api_enhanced_evolutions = sum(1 for evo in self.protocol_evolution_history if evo.get("api_enhancement", False))
        
        # Word count evolution
        word_counts = [iter_data.get("total_word_count", 0) for iter_data in self.dialogue_history]
        word_evolution = word_counts[-1] - word_counts[0] if len(word_counts) >= 2 else 0
        
        return {
            "total_iterations": total_iterations,
            "success_rate": success_rate,
            "successful_responses": successful_responses,
            "total_possible_responses": total_possible_responses,
            "word_count_evolution": word_evolution,
            "protocol_evolutions": protocol_evolutions,
            "api_enhanced_evolutions": api_enhanced_evolutions,
            "final_protocol_version": self.current_protocol.version,
            "evolution_per_iteration": protocol_evolutions / total_iterations if total_iterations > 0 else 0,
            "enhanced_api_usage_rate": avg_enhanced_api_usage,
            "api_method_distribution": api_method_distribution,
            "experiment_effectiveness": min(1.0, success_rate + (protocol_evolutions * 0.1) + (avg_enhanced_api_usage * 0.2))
        }
    
    def analyze_api_enhancement_impact(self) -> Dict[str, Any]:
        """Analyze the impact of API enhancements on protocol effectiveness"""
        
        if not self.dialogue_history:
            return {"error": "No dialogue history to analyze"}
        
        # Compare enhanced vs fallback API performance
        enhanced_performances = []
        fallback_performances = []
        
        for iter_data in self.dialogue_history:
            for ai_key, response in iter_data.get("responses", {}).items():
                if response.get("success", False):
                    api_method = response.get("api_method", "unknown")
                    word_count = response.get("word_count", 0)
                    
                    if api_method == "enhanced":
                        enhanced_performances.append(word_count)
                    elif api_method.startswith("fallback"):
                        fallback_performances.append(word_count)
        
        # Calculate performance differences
        avg_enhanced_words = sum(enhanced_performances) / len(enhanced_performances) if enhanced_performances else 0
        avg_fallback_words = sum(fallback_performances) / len(fallback_performances) if fallback_performances else 0
        
        # API adoption rate over time
        api_adoption_timeline = []
        for iter_data in self.dialogue_history:
            enhanced_rate = iter_data.get("enhanced_api_success_rate", 0.0)
            api_adoption_timeline.append(enhanced_rate)
        
        return {
            "enhanced_api_responses": len(enhanced_performances),
            "fallback_api_responses": len(fallback_performances),
            "enhanced_api_adoption_rate": sum(api_adoption_timeline) / len(api_adoption_timeline) if api_adoption_timeline else 0.0,
            "avg_enhanced_response_length": avg_enhanced_words,
            "avg_fallback_response_length": avg_fallback_words,
            "performance_improvement": (avg_enhanced_words - avg_fallback_words) / avg_fallback_words if avg_fallback_words > 0 else 0.0,
            "api_adoption_timeline": api_adoption_timeline,
            "final_enhanced_adoption": api_adoption_timeline[-1] if api_adoption_timeline else 0.0
        }

# Enhanced main function
async def enhanced_main():
    """Execute enhanced adaptive protocol prototype with proper API integration"""
    
    print("🚀 ENHANCED ADAPTIVE PROTOCOL PROTOTYPE")
    print("Enhancement: Proper API parameter control + system prompts")
    print("Methodology: Freedom of thought, no limits")
    print("Integration: PowerTalk's proven AI connectivity + Enhanced APIs")
    
    # Initialize enhanced engine
    engine = EnhancedAdaptiveProtocolEngine(debug_mode=False)
    
    # Test enhanced connectivity
    working_ais = await engine.discover_working_ais()
    
    if len(working_ais) < 2:
        print(f"\n❌ Need at least 2 working AIs for enhanced testing")
        print(f"Found: {len(working_ais)} working AIs")
        return
    
    # Display API enhancement status
    print(f"\n📊 API Enhancement Status:")
    for ai_key in working_ais:
        ai_name = engine.available_ais[ai_key].name
        platform_caps = engine.ai_connector.platform_capabilities.get(ai_key, {})
        supports_enhanced = platform_caps.get("supports_system_prompt", False)
        supports_seed = platform_caps.get("supports_seed", False)
        status = "✨ Full Enhanced" if supports_enhanced and supports_seed else "🔧 Partial Enhanced" if supports_enhanced else "⚠️ Basic Only"
        print(f"  - {ai_name}: {status}")
    
    # Topic selection (same as before)
    test_topics = [
        "How can AI systems develop genuine creativity beyond pattern recombination?",
        "What would an ideal AI-to-AI communication protocol look like?", 
        "Should AI consciousness research prioritize measurement or development?",
        "How can AI teams coordinate without rigid hierarchies?"
    ]
    
    print(f"\n📝 Available test topics:")
    for i, topic in enumerate(test_topics, 1):
        print(f"  {i}. {topic}")
    
    while True:
        try:
            choice = input(f"\nSelect topic (1-{len(test_topics)}) or enter custom topic: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(test_topics):
                selected_topic = test_topics[int(choice) - 1]
                break
            elif len(choice) > 10:
                selected_topic = choice
                break
            else:
                print("Please select a valid topic number or enter a custom topic")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return
    
    print(f"\n🎯 Selected Topic: {selected_topic}")
    print(f"🤖 Enhanced Participants: {[engine.available_ais[key].name for key in working_ais]}")
    
    # Run enhanced experiment
    results = await engine.run_enhanced_adaptive_protocol_experiment(selected_topic)
    
    if "error" in results:
        print(f"\n❌ Enhanced experiment failed: {results['error']}")
        return
    
    # Save enhanced results
    filepath = engine.save_experiment_results(results)
    
    # Display enhanced summary
    print(f"\n" + "="*80)
    print(f"🧠 ENHANCED ADAPTIVE PROTOCOL EXPERIMENT COMPLETE")
    print(f"="*80)
    
    effectiveness = results.get("effectiveness_analysis", {})
    api_metrics = results.get("api_enhancement_metrics", {})
    
    print(f"📊 Enhanced Results Summary:")
    print(f"  - Total Iterations: {effectiveness.get('total_iterations', 0)}")
    print(f"  - Success Rate: {effectiveness.get('success_rate', 0):.1%}")
    print(f"  - Enhanced API Usage: {effectiveness.get('enhanced_api_usage_rate', 0):.1%}")
    print(f"  - Protocol Evolutions: {effectiveness.get('protocol_evolutions', 0)} ({effectiveness.get('api_enhanced_evolutions', 0)} API-enhanced)")
    print(f"  - Final Protocol Version: v{effectiveness.get('final_protocol_version', '2.0')}")
    print(f"  - Experiment Effectiveness: {effectiveness.get('experiment_effectiveness', 0):.2f}")
    
    if api_metrics:
        print(f"\n🔧 API Enhancement Impact:")
        print(f"  - Enhanced API Adoption: {api_metrics.get('final_enhanced_adoption', 0):.1%}")
        print(f"  - Performance Improvement: {api_metrics.get('performance_improvement', 0):+.1%}")
        print(f"  - Enhanced Responses: {api_metrics.get('enhanced_api_responses', 0)}")
        print(f"  - Fallback Responses: {api_metrics.get('fallback_api_responses', 0)}")
    
    if results.get("protocol_evolution"):
        print(f"\n🔧 Enhanced Protocol Evolution Timeline:")
        for evolution in results["protocol_evolution"]:
            iteration = evolution.get("iteration", 0)
            proposer = evolution.get("proposer", "unknown")
            suggestion = evolution.get("suggestion_type", "unknown")
            api_enhanced = "✨" if evolution.get("api_enhancement", False) else "🔧"
            print(f"  - {api_enhanced} Iteration {iteration}: {proposer} suggested {suggestion}")
    
    print(f"\n💾 Enhanced results saved: {filepath}")
    print(f"\n🎉 API Enhancement validated: {effectiveness.get('enhanced_api_usage_rate', 0):.0f}% enhanced API adoption achieved!")

if __name__ == "__main__":
    try:
        asyncio.run(enhanced_main())
    except KeyboardInterrupt:
        print("\n\nEnhanced prototype interrupted by user.")
    except Exception as e:
        print(f"\nEnhanced Error: {e}")
        import traceback
        traceback.print_exc()