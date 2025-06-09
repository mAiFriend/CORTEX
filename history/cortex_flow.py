#!/usr/bin/env python3
"""
CORTEX Flow - AI-Team-Enhanced Stateless Context-Passing
Where AI thoughts flow seamlessly into breakthrough insights

🌊 FLOW Methodology Applied:
- Feedback sammeln (AI-Team input integrated)
- Lernen (Enhanced with real cost tracking)
- Organisieren (4-class architecture with graceful degradation)
- Wirken (Production-ready implementation)

Key AI-Team Enhancements:
✅ Real Token Cost Tracking - Provider-specific rates
✅ Enhanced Graceful Degradation - Warn-and-continue 
✅ Config Validation - Auto-adjustment for missing API keys
"""

import asyncio
import json
import time
import yaml
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not installed, trying environment variables...")

# AI Provider imports
import openai
import anthropic
import google.generativeai as genai

# =============================================================================
# CONFIGURATION & DATA STRUCTURES
# =============================================================================

# AI-TEAM ENHANCEMENT: Real provider-specific token costs (current market rates)
TOKEN_COSTS = {
    "claude": {
        "input": 0.000015,   # $15 per 1M input tokens (Sonnet 4)
        "output": 0.000075   # $75 per 1M output tokens
    },
    "chatgpt": {
        "input": 0.00003,    # $30 per 1M input tokens (GPT-4 Turbo)
        "output": 0.00006    # $60 per 1M output tokens  
    },
    "gemini": {
        "input": 0.000125,   # $1.25 per 1M input tokens (2.5 Pro)
        "output": 0.000375   # $3.75 per 1M output tokens
    },
    "qwen": {
        "input": 0.0000005,  # $0.50 per 1M input tokens (sehr günstig)
        "output": 0.000002   # $2 per 1M output tokens
    },
    "deepseek": {
        "input": 0.000001,   # $1 per 1M input tokens (extrem günstig)
        "output": 0.000002   # $2 per 1M output tokens  
    }
}

@dataclass
class AIResponse:
    """Single AI response with enhanced metadata"""
    ai_name: str
    response: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    real_cost: float        # AI-TEAM ENHANCEMENT: Real cost calculation
    response_time: float
    iteration: int
    timestamp: datetime
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class IterationRound:
    """Complete iteration with all AI responses"""
    round_number: int
    topic: str
    ruleset_name: str
    responses: List[AIResponse]
    successful_ais: List[str]
    failed_ais: List[str]
    total_cost: float
    context_used: Dict[str, str]  # Truncated context per AI
    timestamp: datetime

@dataclass
class CortexReport:
    """Final session report with enhanced analytics"""
    experiment_name: str
    ai_team: List[str]
    iterations: List[IterationRound]
    total_cost: float
    cost_breakdown: Dict[str, float]  # AI-TEAM ENHANCEMENT: Cost per provider
    convergence_analysis: Dict[str, Any]
    emergent_insights: List[str]
    session_metadata: Dict[str, Any]
    token_usage_summary: Dict[str, Any]

class CortexSessionError(Exception):
    """Custom exception for CORTEX session errors"""
    pass

class TokenBudgetExceededError(Exception):
    """Custom exception for token budget overruns"""
    pass

# =============================================================================
# CONTEXT PROCESSOR - Smart Truncation & Context Management
# =============================================================================

class ContextProcessor:
    """Smart truncation & enhanced context management"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.context_config = config.get('context_management', {})
        self.truncation_config = self.context_config.get('truncation', {})
        self.front_loading_config = self.context_config.get('front_loading', {})
        
    def smart_truncate(self, response: str, method: str = None, limit: int = None) -> str:
        """Context-preserving truncation with multiple algorithms"""
        
        # Use config defaults if not specified
        method = method or self.truncation_config.get('method', 'smart_sentence_aware')
        limit = limit or self.truncation_config.get('limit_chars', 1200)
        
        if len(response) <= limit:
            return response
        
        if method == "smart_sentence_aware":
            return self._sentence_aware_truncation(response, limit)
        elif method == "paragraph_aware":
            return self._paragraph_aware_truncation(response, limit)
        elif method == "hard_cut":
            return response[:limit] + "..."
        else:
            print(f"⚠️  Unknown truncation method: {method}, using sentence_aware")
            return self._sentence_aware_truncation(response, limit)

    def _sentence_aware_truncation(self, text: str, limit: int) -> str:
        """Never cut mid-sentence - Blueprint algorithm"""
        # Handle edge cases
        if not text or limit <= 0:
            return ""
            
        sentences = text.split('. ')
        result = ""
        
        for sentence in sentences:
            potential = result + sentence + ". "
            if len(potential) <= limit:
                result = potential
            else:
                break
        
        # Clean up and add ellipsis if truncated
        result = result.rstrip()
        if len(result) < len(text) and not result.endswith('...'):
            result += "..."
            
        return result

    def _paragraph_aware_truncation(self, text: str, limit: int) -> str:
        """Cut at paragraph boundaries for logical flow"""
        if not text or limit <= 0:
            return ""
            
        paragraphs = text.split('\n\n')
        result = ""
        
        for paragraph in paragraphs:
            potential = result + paragraph + "\n\n"
            if len(potential) <= limit:
                result = potential
            else:
                break
        
        result = result.rstrip()
        if len(result) < len(text) and not result.endswith('...'):
            result += "..."
            
        return result

    def smart_truncate_all(self, responses: List[AIResponse]) -> Dict[str, str]:
        """Process all AI responses for next iteration context"""
        truncated_context = {}
        
        for response in responses:
            if response.success:
                truncated = self.smart_truncate(response.response)
                truncated_context[response.ai_name] = truncated
            
        return truncated_context

    def build_iteration_prompt(self, ai_name: str, iteration: int, topic: str, 
                              previous_context: Dict[str, str], ruleset: Dict) -> str:
        """Dynamic prompt construction with embedded context"""
        
        # Get AI archetype (simplified for now)
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
            context_section = "\nPREVIOUS AI RESPONSES:\n"
            for ai, response in previous_context.items():
                if ai != ai_name:  # Don't include own previous response
                    context_section += f"\n{ai}: {response}\n"
        
        # Apply front-loading rules
        front_loading_instruction = self._build_front_loading_instruction()
        
        # Build ruleset parameters
        ruleset_params = ""
        if ruleset:
            ruleset_params = "\nACTIVE COMMUNICATION RULES:\n"
            for param, value in ruleset.items():
                ruleset_params += f"- {param}: {value}\n"
        
        # Construct complete prompt
        prompt = f"""Du bist {archetype} im CORTEX Framework.

ITERATION {iteration}: {topic}

{front_loading_instruction}

COMMUNICATION OPTIMIZATION:
- Beziehe dich explizit auf andere AIs aus dem vorherigen Kontext
- Baue auf deren Insights auf oder stelle sie konstruktiv in Frage
- Entwickle die Diskussion weiter, vermeide Wiederholungen
{context_section}
{ruleset_params}

Deine Antwort:"""

        return prompt

    def _build_front_loading_instruction(self) -> str:
        """Build front-loading instruction based on config"""
        if not self.front_loading_config.get('enabled', True):
            return ""
            
        key_points_limit = self.front_loading_config.get('key_points_limit', 200)
        enforcement_level = self.front_loading_config.get('enforcement_level', 'suggested')
        
        if enforcement_level == "strict":
            return f"WICHTIG: Deine ersten {key_points_limit} Zeichen MÜSSEN deine Kernaussage enthalten!"
        elif enforcement_level == "suggested":
            return f"EMPFEHLUNG: Beginne mit deiner Kernaussage (erste {key_points_limit} Zeichen)."
        else:  # optional
            return "TIPP: Kernaussagen am Anfang verbessern die Kontextverwendung."

# =============================================================================
# AI ORCHESTRATOR - Enhanced Parallel Coordination
# =============================================================================

class AIOrchestrator:
    """AI-team-optimized parallel coordination with enhanced graceful degradation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.execution_config = config.get('execution', {})
        self.timeout_seconds = self.execution_config.get('timeout_seconds', 120)
        self.min_ais_required = self.execution_config.get('min_ais_required', 2)
        self.graceful_mode = self.execution_config.get('graceful_mode', True)  # AI-TEAM ENHANCEMENT
        self.token_costs = TOKEN_COSTS
        
        self.ai_clients = {}
        self.available_ais = []
        self._setup_ai_clients()

    def _setup_ai_clients(self) -> None:
        """Initialize only the AI providers specified in config ai_team"""
        
        # Get requested AI team from config
        requested_team = self.config.get('ai_team', [])
        
        if not requested_team:
            raise CortexSessionError("No AI team specified in config!")
        
        print(f"🎯 Initializing AIs for team: {', '.join(requested_team)}")
        
        clients = {}
        missing_keys = []
        
        for ai_name in requested_team:
            
            if ai_name == "claude":
                if os.getenv('ANTHROPIC_API_KEY'):
                    try:
                        clients['claude'] = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                        print("✅ Claude client initialized")
                    except Exception as e:
                        print(f"❌ Claude initialization failed: {e}")
                        missing_keys.append('claude (ANTHROPIC_API_KEY invalid)')
                else:
                    missing_keys.append('claude (ANTHROPIC_API_KEY missing)')
            
            elif ai_name == "chatgpt":
                if os.getenv('OPENAI_API_KEY'):
                    try:
                        clients['chatgpt'] = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                        print("✅ ChatGPT client initialized")
                    except Exception as e:
                        print(f"❌ ChatGPT initialization failed: {e}")
                        missing_keys.append('chatgpt (OPENAI_API_KEY invalid)')
                else:
                    missing_keys.append('chatgpt (OPENAI_API_KEY missing)')
            
            elif ai_name == "gemini":
                if os.getenv('GOOGLE_API_KEY'):
                    try:
                        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                        clients['gemini'] = genai.GenerativeModel('gemini-2.0-flash-exp')
                        print("✅ Gemini client initialized")
                    except Exception as e:
                        print(f"❌ Gemini initialization failed: {e}")
                        missing_keys.append('gemini (GOOGLE_API_KEY invalid)')
                else:
                    missing_keys.append('gemini (GOOGLE_API_KEY missing)')
            
            elif ai_name == "qwen":
                if os.getenv('OPENROUTER_API_KEY'):
                    try:
                        clients['qwen'] = openai.OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=os.getenv('OPENROUTER_API_KEY')
                        )
                        print("✅ Qwen client initialized (via OpenRouter)")
                    except Exception as e:
                        print(f"❌ Qwen initialization failed: {e}")
                        missing_keys.append('qwen (OPENROUTER_API_KEY invalid)')
                else:
                    missing_keys.append('qwen (OPENROUTER_API_KEY missing)')
            
            elif ai_name == "deepseek":
                if os.getenv('DEEPSEEK_API_KEY'):
                    try:
                        clients['deepseek'] = openai.OpenAI(
                            base_url="https://api.deepseek.com/v1",
                            api_key=os.getenv('DEEPSEEK_API_KEY')
                        )
                        print("✅ DeepSeek client initialized")
                    except Exception as e:
                        print(f"❌ DeepSeek initialization failed: {e}")
                        missing_keys.append('deepseek (DEEPSEEK_API_KEY invalid)')
                else:
                    missing_keys.append('deepseek (DEEPSEEK_API_KEY missing)')
            
            else:
                print(f"⚠️  Unknown AI provider in config: {ai_name}")
                missing_keys.append(f'{ai_name} (unknown provider)')
        
        # Enhanced validation and user feedback
        if missing_keys:
            print(f"\n🚨 Missing or invalid API keys:")
            for key in missing_keys:
                print(f"   - {key}")
                
        self.ai_clients = clients
        self.available_ais = list(clients.keys())
        
        if self.available_ais:
            print(f"✅ Team ready: {', '.join(self.available_ais)}")
        else:
            raise CortexSessionError("No AI providers available! Please check your API keys.")

    def validate_and_adjust_ai_team(self, requested_team: List[str]) -> List[str]:
        """Validate that all requested AIs are initialized and ready"""
        
        # Since we only initialize requested AIs, this should match exactly
        available_team = [ai for ai in requested_team if ai in self.available_ais]
        unavailable_team = [ai for ai in requested_team if ai not in self.available_ais]
        
        if unavailable_team:
            print(f"❌ Failed to initialize: {', '.join(unavailable_team)}")
            
        if not available_team:
            raise CortexSessionError("No AIs could be initialized! Check your API keys.")
            
        if len(available_team) < self.min_ais_required and not self.graceful_mode:
            raise CortexSessionError(f"Too few AIs available ({len(available_team)} < {self.min_ais_required})")
            
        return available_team

    async def execute_iteration_round(self, ai_team: List[str], 
                                    iteration_prompts: Dict[str, str]) -> List[AIResponse]:
        """AI-TEAM ENHANCED: Parallel execution with warn-and-continue graceful degradation"""
        
        print(f"\n🚀 Starting parallel execution with {len(ai_team)} AIs...")
        
        # Start all AIs in parallel
        tasks = []
        for ai_name in ai_team:
            if ai_name in iteration_prompts:
                task = self.query_ai_async(ai_name, iteration_prompts[ai_name])
                tasks.append((ai_name, task))
        
        try:
            # Wait for ALL or timeout (120s default)
            print(f"⏳ Waiting for responses (timeout: {self.timeout_seconds}s)...")
            
            results = await asyncio.wait_for(
                asyncio.gather(*[task for _, task in tasks], return_exceptions=True),
                timeout=self.timeout_seconds
            )
            
            # Process results with enhanced graceful degradation
            successful_responses = []
            failed_ais = []
            
            for i, result in enumerate(results):
                ai_name = tasks[i][0]
                
                if isinstance(result, Exception):
                    print(f"❌ {ai_name} failed: {result}")
                    failed_ais.append(ai_name)
                elif isinstance(result, AIResponse) and result.success:
                    successful_responses.append(result)
                    print(f"✅ {ai_name} responded ({result.response_time:.1f}s, ${result.real_cost:.4f})")
                else:
                    print(f"❌ {ai_name} returned invalid response")
                    failed_ais.append(ai_name)
            
            # AI-TEAM ENHANCEMENT: Enhanced graceful degradation
            return self._enhanced_graceful_degradation(successful_responses, failed_ais)
            
        except asyncio.TimeoutError:
            print(f"🚨 Complete iteration timeout after {self.timeout_seconds}s")
            raise CortexSessionError("Iteration timeout - all AIs failed to respond")

    def _enhanced_graceful_degradation(self, successful_responses: List[AIResponse], 
                                     failed_ais: List[str]) -> List[AIResponse]:
        """AI-TEAM FEEDBACK: Warn-and-continue instead of hard failure"""
        
        if failed_ais:
            print(f"⚠️  AIs that failed: {', '.join(failed_ais)}")
            
        if successful_responses:
            success_names = [r.ai_name for r in successful_responses]
            print(f"✅ AIs that succeeded: {', '.join(success_names)}")
            
        # Check minimum requirements
        if len(successful_responses) < self.min_ais_required:
            if len(successful_responses) > 0 and self.graceful_mode:
                print(f"⚠️  WARNING: Only {len(successful_responses)} AIs responded (< {self.min_ais_required} required)")
                print(f"🔄  GRACEFUL MODE: Continuing with available AIs...")
                return successful_responses
            else:
                raise CortexSessionError(f"Too few AIs responded ({len(successful_responses)} < {self.min_ais_required})")
        
        return successful_responses

    async def query_ai_async(self, ai_name: str, prompt: str) -> AIResponse:
        """Single AI query with enhanced error handling and real cost calculation"""
        
        start_time = time.time()
        
        try:
            if ai_name not in self.ai_clients:
                raise CortexSessionError(f"AI client {ai_name} not available")
                
            client = self.ai_clients[ai_name]
            
            # Provider-specific API calls
            if ai_name == "claude":
                response = await self._query_claude(client, prompt)
            elif ai_name == "chatgpt":
                response = await self._query_chatgpt(client, prompt)
            elif ai_name == "gemini":
                response = await self._query_gemini(client, prompt)
            elif ai_name == "qwen":
                response = await self._query_qwen(client, prompt)
            elif ai_name == "deepseek":
                response = await self._query_deepseek(client, prompt)
            else:
                raise CortexSessionError(f"Unknown AI provider: {ai_name}")
            
            response_time = time.time() - start_time
            
            # AI-TEAM ENHANCEMENT: Real cost calculation
            real_cost = self.calculate_real_cost(ai_name, response['input_tokens'], response['output_tokens'])
            
            return AIResponse(
                ai_name=ai_name,
                response=response['text'],
                input_tokens=response['input_tokens'],
                output_tokens=response['output_tokens'],
                total_tokens=response['input_tokens'] + response['output_tokens'],
                real_cost=real_cost,
                response_time=response_time,
                iteration=0,  # Will be set by caller
                timestamp=datetime.now(),
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            print(f"❌ Error querying {ai_name}: {e}")
            
            return AIResponse(
                ai_name=ai_name,
                response="",
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                real_cost=0.0,
                response_time=response_time,
                iteration=0,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )

    def calculate_real_cost(self, ai_name: str, input_tokens: int, output_tokens: int) -> float:
        """AI-TEAM FEEDBACK: Calculate real costs with provider-specific rates"""
        
        if ai_name not in self.token_costs:
            print(f"⚠️  Unknown cost for {ai_name}, using default estimation")
            return (input_tokens + output_tokens) * 0.00003  # Default GPT-4 rate
        
        costs = self.token_costs[ai_name]
        total_cost = (input_tokens * costs["input"]) + (output_tokens * costs["output"])
        
        return round(total_cost, 6)  # 6 decimal precision for micro-payments

    # Provider-specific API implementations
    async def _query_claude(self, client, prompt: str) -> Dict:
        """Query Claude with proper token counting"""
        # Note: Anthropic doesn't provide direct async, so we'll use sync in thread
        loop = asyncio.get_event_loop()
        
        def sync_query():
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=self.config.get('api_config', {}).get('max_tokens', 4096),
                temperature=self.config.get('api_config', {}).get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'text': response.content[0].text,
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens
            }
        
        return await loop.run_in_executor(None, sync_query)

    async def _query_chatgpt(self, client, prompt: str) -> Dict:
        """Query ChatGPT with proper async handling"""
        loop = asyncio.get_event_loop()
        
        def sync_query():
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                max_tokens=self.config.get('api_config', {}).get('max_tokens', 4096),
                temperature=self.config.get('api_config', {}).get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'text': response.choices[0].message.content,
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens
            }
        
        return await loop.run_in_executor(None, sync_query)

    async def _query_gemini(self, client, prompt: str) -> Dict:
        """Query Gemini with estimated token counting"""
        loop = asyncio.get_event_loop()
        
        def sync_query():
            response = client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.get('api_config', {}).get('max_tokens', 4096),
                    temperature=self.config.get('api_config', {}).get('temperature', 0.7)
                )
            )
            
            # Gemini doesn't provide exact token counts, estimate
            text = response.text
            input_tokens = len(prompt.split()) * 1.3  # Rough estimation
            output_tokens = len(text.split()) * 1.3
            
            return {
                'text': text,
                'input_tokens': int(input_tokens),
                'output_tokens': int(output_tokens)
            }
        
        return await loop.run_in_executor(None, sync_query)

    async def _query_qwen(self, client, prompt: str) -> Dict:
        """Query Qwen via OpenRouter with proper async handling"""
        loop = asyncio.get_event_loop()
        
        def sync_query():
            response = client.chat.completions.create(
                model="qwen/qwen-2.5-72b-instruct",  # OpenRouter model name
                max_tokens=self.config.get('api_config', {}).get('max_tokens', 4096),
                temperature=self.config.get('api_config', {}).get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'text': response.choices[0].message.content,
                'input_tokens': response.usage.prompt_tokens if response.usage else len(prompt.split()) * 1.3,
                'output_tokens': response.usage.completion_tokens if response.usage else len(response.choices[0].message.content.split()) * 1.3
            }
        
        return await loop.run_in_executor(None, sync_query)

    async def _query_deepseek(self, client, prompt: str) -> Dict:
        """Query DeepSeek with proper async handling"""
        loop = asyncio.get_event_loop()
        
        def sync_query():
            response = client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=self.config.get('api_config', {}).get('max_tokens', 4096),
                temperature=self.config.get('api_config', {}).get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'text': response.choices[0].message.content,
                'input_tokens': response.usage.prompt_tokens if response.usage else len(prompt.split()) * 1.3,
                'output_tokens': response.usage.completion_tokens if response.usage else len(response.choices[0].message.content.split()) * 1.3
            }
        
        return await loop.run_in_executor(None, sync_query)

# =============================================================================
# REPORT GENERATOR - Enhanced Analytics
# =============================================================================

class ReportGenerator:
    """Comprehensive output synthesis with AI-team enhancements"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.output_config = config.get('output', {})

    def generate_final_report(self, session_data: Dict) -> CortexReport:
        """Create comprehensive session report with cost analysis"""
        
        iterations = session_data['iterations']
        
        # Calculate totals and breakdowns
        total_cost = sum(iteration.total_cost for iteration in iterations)
        cost_breakdown = self._calculate_cost_breakdown(iterations)
        
        # Generate analyses
        convergence_analysis = self._analyze_convergence(iterations)
        emergent_insights = self._extract_emergent_insights(iterations)
        token_usage_summary = self._create_token_usage_summary(iterations)
        
        report = CortexReport(
            experiment_name=session_data['experiment_name'],
            ai_team=session_data['ai_team'],
            iterations=iterations,
            total_cost=total_cost,
            cost_breakdown=cost_breakdown,
            convergence_analysis=convergence_analysis,
            emergent_insights=emergent_insights,
            session_metadata=session_data['metadata'],
            token_usage_summary=token_usage_summary
        )
        
        return report

    def _calculate_cost_breakdown(self, iterations: List[IterationRound]) -> Dict[str, float]:
        """AI-TEAM ENHANCEMENT: Detailed cost breakdown per provider"""
        
        breakdown = {}
        
        for iteration in iterations:
            for response in iteration.responses:
                if response.ai_name not in breakdown:
                    breakdown[response.ai_name] = 0
                breakdown[response.ai_name] += response.real_cost
        
        # Sort by cost (highest first)
        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))

    def _analyze_convergence(self, iterations: List[IterationRound]) -> Dict[str, Any]:
        """Analyze where AIs converged or diverged in their responses"""
        
        analysis = {
            'total_iterations': len(iterations),
            'ai_participation': {},
            'response_lengths': {},
            'themes_per_iteration': []
        }
        
        for iteration in iterations:
            # Track AI participation
            for response in iteration.responses:
                ai_name = response.ai_name
                if ai_name not in analysis['ai_participation']:
                    analysis['ai_participation'][ai_name] = 0
                analysis['ai_participation'][ai_name] += 1
                
                # Track response lengths
                if ai_name not in analysis['response_lengths']:
                    analysis['response_lengths'][ai_name] = []
                analysis['response_lengths'][ai_name].append(len(response.response))
            
            # Extract themes (simple keyword analysis)
            iteration_themes = self._extract_iteration_themes(iteration.responses)
            analysis['themes_per_iteration'].append({
                'iteration': iteration.round_number,
                'themes': iteration_themes
            })
        
        return analysis

    def _extract_iteration_themes(self, responses: List[AIResponse]) -> List[str]:
        """Simple theme extraction from responses"""
        
        # Combine all response text
        all_text = " ".join([r.response for r in responses if r.success]).lower()
        
        # Simple keyword extraction (could be enhanced with NLP)
        common_words = ['ki', 'kommunikation', 'dialog', 'bewusstsein', 'denken', 'verstehen', 
                       'system', 'mensch', 'sprache', 'information', 'prozess', 'entwicklung']
        
        themes = []
        for word in common_words:
            if word in all_text and all_text.count(word) >= 2:
                themes.append(word)
        
        return themes[:5]  # Top 5 themes

    def _extract_emergent_insights(self, iterations: List[IterationRound]) -> List[str]:
        """Extract real emergent insights from AI collaboration content"""
        
        insights = []
        
        # Collect all successful responses
        all_responses = []
        for iteration in iterations:
            for response in iteration.responses:
                if response.success:
                    all_responses.append({
                        'ai': response.ai_name,
                        'iteration': iteration.round_number,
                        'content': response.response.lower(),
                        'original': response.response
                    })
        
        if len(all_responses) < 2:
            return ["Insufficient responses for meaningful insight extraction"]
        
        # 1. CONTENT-BASED CONVERGENCE ANALYSIS
        convergent_concepts = self._find_convergent_concepts(all_responses)
        if convergent_concepts:
            insights.append(f"**Convergent Concepts:** {len(convergent_concepts)} AIs independently developed similar ideas: {', '.join(convergent_concepts[:3])}")
        
        # 2. NOVEL SYNTHESIS DETECTION  
        novel_concepts = self._detect_novel_synthesis(all_responses)
        for concept in novel_concepts[:3]:
            insights.append(f"**Novel Synthesis:** {concept}")
        
        # 3. CROSS-AI BUILDING PATTERNS
        building_chains = self._analyze_building_chains(all_responses)
        if building_chains:
            insights.append(f"**Collaborative Evolution:** {building_chains}")
        
        # 4. CONCRETE SOLUTION EMERGENCE
        solutions = self._extract_concrete_solutions(all_responses)
        for solution in solutions[:2]:
            insights.append(f"**Concrete Solution:** {solution}")
        
        # 5. PARADIGM SHIFTS
        paradigm_shifts = self._detect_paradigm_shifts(all_responses)
        for shift in paradigm_shifts[:2]:
            insights.append(f"**Paradigm Shift:** {shift}")
        
        # 6. CONSENSUS FORMATION
        consensus = self._analyze_consensus_formation(all_responses)
        if consensus:
            insights.append(f"**Emerging Consensus:** {consensus}")
        
        return insights[:8] if insights else ["No significant emergent insights detected in this session"]

    def _find_convergent_concepts(self, responses: List[Dict]) -> List[str]:
        """Find concepts that multiple AIs mentioned independently"""
        
        # Key concept keywords to look for
        concept_keywords = {
            'quantum': ['quantum', 'entangled', 'superposition'],
            'graph': ['graph', 'network', 'topology', 'node'],
            'semantic': ['semantic', 'meaning', 'context'],
            'direct': ['direct', 'immediate', 'unmediated'],
            'probability': ['probability', 'distribution', 'inference'],
            'neural': ['neural', 'neuron', 'synaptic'],
            'executable': ['executable', 'runnable', 'actionable'],
            'dynamic': ['dynamic', 'adaptive', 'evolving']
        }
        
        convergent = []
        
        for concept, keywords in concept_keywords.items():
            mentioning_ais = set()
            for response in responses:
                if any(keyword in response['content'] for keyword in keywords):
                    mentioning_ais.add(response['ai'])
            
            if len(mentioning_ais) >= 2:  # At least 2 AIs mentioned it
                convergent.append(f"{concept} ({len(mentioning_ais)} AIs)")
        
        return convergent

    def _detect_novel_synthesis(self, responses: List[Dict]) -> List[str]:
        """Detect novel concepts that emerged from AI collaboration"""
        
        novel_concepts = []
        
        # Look for complex compound concepts that suggest synthesis
        synthesis_patterns = [
            (r'quantum.*graph', 'Quantum-graph hybrid concepts'),
            (r'executable.*model', 'Executable model paradigms'),
            (r'dynamic.*inference', 'Dynamic inference frameworks'),
            (r'semantic.*protocol', 'Semantic communication protocols'),
            (r'multi.*dimensional', 'Multi-dimensional approaches'),
            (r'direct.*exchange', 'Direct exchange mechanisms'),
            (r'neural.*stream', 'Neural streaming concepts'),
            (r'probability.*fusion', 'Probability fusion methods')
        ]
        
        combined_text = ' '.join([r['content'] for r in responses])
        
        for pattern, description in synthesis_patterns:
            if re.search(pattern, combined_text):
                novel_concepts.append(description)
        
        return novel_concepts

    def _analyze_building_chains(self, responses: List[Dict]) -> str:
        """Analyze how AIs built upon each other's ideas"""
        
        if len(responses) < 2:
            return ""
        
        # Look for explicit building language in later iterations
        building_indicators = ['aufbauend', 'erweitert', 'basierend', 'inspiriert', 'kombiniert', 'synthesis', 'building']
        
        building_count = 0
        for response in responses:
            if response['iteration'] > 1:  # Only check responses after first iteration
                if any(indicator in response['content'] for indicator in building_indicators):
                    building_count += 1
        
        if building_count >= 2:
            return f"{building_count} AIs explicitly built upon previous ideas in later iterations"
        
        return ""

    def _extract_concrete_solutions(self, responses: List[Dict]) -> List[str]:
        """Extract concrete solutions proposed by AIs"""
        
        solutions = []
        
        # Look for solution-indicating phrases with following content
        solution_patterns = [
            (r'schlage.*vor[:\s]([^.]{50,150})', 'AI Proposal'),
            (r'lösung[:\s]([^.]{30,120})', 'Direct Solution'),
            (r'entwicklung[:\s]([^.]{40,140})', 'Development Approach'),
            (r'konzept[:\s]([^.]{30,120})', 'Core Concept'),
            (r'protokoll[:\s]([^.]{30,120})', 'Protocol Design'),
            (r'framework[:\s]([^.]{30,120})', 'Framework Proposal')
        ]
        
        for response in responses:
            for pattern, label in solution_patterns:
                matches = re.findall(pattern, response['content'], re.IGNORECASE)
                for match in matches[:1]:  # Max 1 per response
                    clean_match = match.strip()[:100] + "..." if len(match) > 100 else match.strip()
                    if len(clean_match) > 20:  # Only meaningful solutions
                        solutions.append(f"{response['ai']}: {clean_match}")
        
        return solutions

    def _detect_paradigm_shifts(self, responses: List[Dict]) -> List[str]:
        """Detect paradigm shifts in thinking"""
        
        shifts = []
        
        # Look for paradigm shift language
        shift_indicators = [
            (r'jenseits.*sprache', 'Beyond traditional language paradigms'),
            (r'revolutionär', 'Revolutionary approaches emerged'),
            (r'paradigm.*shift', 'Explicit paradigm shift recognition'),
            (r'komplett.*neu', 'Completely new methodologies'),
            (r'durchbruch', 'Breakthrough concepts identified'),
            (r'fundamental.*änderung', 'Fundamental changes proposed')
        ]
        
        combined_text = ' '.join([r['content'] for r in responses])
        
        for pattern, description in shift_indicators:
            if re.search(pattern, combined_text, re.IGNORECASE):
                shifts.append(description)
        
        return shifts

    def _analyze_consensus_formation(self, responses: List[Dict]) -> str:
        """Analyze if AIs formed consensus around key concepts"""
        
        if len(responses) < 3:
            return ""
        
        # Count how many AIs mentioned core concepts
        core_concepts = {
            'direct communication': ['direkt', 'unmittelbar', 'direct'],
            'beyond language': ['jenseits', 'beyond', 'außerhalb'],
            'data exchange': ['austausch', 'exchange', 'transfer'],
            'protocol': ['protokoll', 'protocol', 'schema'],
            'efficiency': ['effizienz', 'efficient', 'optimal']
        }
        
        consensus_items = []
        
        for concept, keywords in core_concepts.items():
            mentioning_count = 0
            for response in responses:
                if any(keyword in response['content'] for keyword in keywords):
                    mentioning_count += 1
            
            if mentioning_count >= len(responses) * 0.6:  # 60% of AIs mentioned it
                consensus_items.append(concept)
        
        if len(consensus_items) >= 2:
            return f"Consensus forming around: {', '.join(consensus_items)}"
        
        return ""

    def _create_token_usage_summary(self, iterations: List[IterationRound]) -> Dict[str, Any]:
        """Create detailed token usage summary"""
        
        summary = {
            'total_tokens': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'by_ai': {},
            'by_iteration': [],
            'cost_efficiency': {}
        }
        
        for iteration in iterations:
            iteration_summary = {
                'iteration': iteration.round_number,
                'total_tokens': 0,
                'total_cost': iteration.total_cost,
                'ai_count': len(iteration.responses)
            }
            
            for response in iteration.responses:
                if response.success:
                    # Update totals
                    summary['total_tokens'] += response.total_tokens
                    summary['total_input_tokens'] += response.input_tokens
                    summary['total_output_tokens'] += response.output_tokens
                    
                    iteration_summary['total_tokens'] += response.total_tokens
                    
                    # Update by AI
                    if response.ai_name not in summary['by_ai']:
                        summary['by_ai'][response.ai_name] = {
                            'total_tokens': 0,
                            'total_cost': 0,
                            'responses': 0
                        }
                    
                    summary['by_ai'][response.ai_name]['total_tokens'] += response.total_tokens
                    summary['by_ai'][response.ai_name]['total_cost'] += response.real_cost
                    summary['by_ai'][response.ai_name]['responses'] += 1
            
            summary['by_iteration'].append(iteration_summary)
        
        # Calculate cost efficiency (tokens per dollar)
        for ai_name, stats in summary['by_ai'].items():
            if stats['total_cost'] > 0:
                summary['cost_efficiency'][ai_name] = stats['total_tokens'] / stats['total_cost']
            else:
                summary['cost_efficiency'][ai_name] = 0
        
        return summary

    def format_output(self, report: CortexReport, format_type: str = None) -> str:
        """Format report according to specified format"""
        
        format_type = format_type or self.output_config.get('format', 'json')
        
        if format_type == 'json':
            return self._format_json(report)
        elif format_type == 'markdown':
            return self._format_markdown(report)
        elif format_type == 'yaml':
            return self._format_yaml(report)
        else:
            print(f"⚠️  Unknown format: {format_type}, using JSON")
            return self._format_json(report)

    def _format_json(self, report: CortexReport) -> str:
        """Format as JSON"""
        # Convert dataclass to dict for JSON serialization
        report_dict = asdict(report)
        
        # Handle datetime serialization
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(report_dict, indent=2, default=serialize_datetime)

    def _format_markdown(self, report: CortexReport) -> str:
        """Format as Markdown with insights first, then stats"""
        
        md = f"""# CORTEX Session Report: {report.experiment_name}

## 🧠 Key Insights & Emergent Discoveries

"""
        
        # Lead with emergent insights
        if report.emergent_insights:
            for insight in report.emergent_insights:
                md += f"- **{insight}**\n"
        else:
            md += "- No emergent insights detected in this session\n"
        
        md += f"""

## 📊 Session Statistics

- **AI Team:** {', '.join(report.ai_team)} ({len(report.ai_team)} AIs)
- **Total Iterations:** {len(report.iterations)}
- **Total Cost:** ${report.total_cost:.4f}
- **Session Duration:** {report.session_metadata.get('duration', 'Unknown')}

### 💰 Cost Breakdown

"""
        
        for ai_name, cost in report.cost_breakdown.items():
            percentage = (cost / report.total_cost * 100) if report.total_cost > 0 else 0
            tokens = report.token_usage_summary['by_ai'].get(ai_name, {}).get('total_tokens', 0)
            md += f"- **{ai_name}:** ${cost:.4f} ({percentage:.1f}%) - {tokens:,} tokens\n"
        
        md += f"""

### 📈 Token Efficiency (tokens per $)

"""
        
        for ai_name, efficiency in sorted(report.token_usage_summary['cost_efficiency'].items(), 
                                        key=lambda x: x[1], reverse=True):
            md += f"- **{ai_name}:** {efficiency:,.0f} tokens/$\n"
        
        md += f"""

## 🔄 Detailed Iteration Log

"""
        
        for iteration in report.iterations:
            md += f"""### Iteration {iteration.round_number}: {iteration.ruleset_name}

- **Topic:** {iteration.topic}
- **Successful AIs:** {', '.join(iteration.successful_ais)}
- **Failed AIs:** {', '.join(iteration.failed_ais) if iteration.failed_ais else 'None'}
- **Cost:** ${iteration.total_cost:.4f}

**AI Responses:**

"""
            for response in iteration.responses:
                if response.success:
                    truncated_response = response.response[:300] + "..." if len(response.response) > 300 else response.response
                    md += f"**{response.ai_name}** (${response.real_cost:.4f}, {response.response_time:.1f}s):\n\n{truncated_response}\n\n---\n\n"
        
        md += f"""
## 📈 Convergence Analysis

### AI Participation Rate
"""
        
        for ai_name, count in report.convergence_analysis.get('ai_participation', {}).items():
            participation_rate = (count / len(report.iterations) * 100) if len(report.iterations) > 0 else 0
            md += f"- **{ai_name}:** {count}/{len(report.iterations)} iterations ({participation_rate:.0f}%)\n"
        
        md += f"""

### Communication Themes Per Iteration
"""
        
        for theme_data in report.convergence_analysis.get('themes_per_iteration', []):
            themes = ', '.join(theme_data.get('themes', [])) or 'No themes detected'
            md += f"- **Iteration {theme_data.get('iteration', '?')}:** {themes}\n"
        
        return md

    def _format_yaml(self, report: CortexReport) -> str:
        """Format as YAML"""
        report_dict = asdict(report)
        
        # Convert datetime objects to strings
        def convert_datetime(obj):
            if isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj
        
        report_dict = convert_datetime(report_dict)
        
        return yaml.dump(report_dict, default_flow_style=False, allow_unicode=True, indent=2)

# =============================================================================
# MAIN CORTEX SESSION CLASS
# =============================================================================

class CortexSession:
    """AI-Team-optimized orchestration class for CORTEX stateless sessions"""
    
    def __init__(self, config_path: str):
        print("🌊 Initializing CORTEX Flow session...")
        
        self.config = self.load_and_validate_config(config_path)
        self.context_processor = ContextProcessor(self.config)
        self.ai_orchestrator = AIOrchestrator(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        # Session tracking
        self.session_data = {
            'experiment_name': self.config.get('experiment', {}).get('name', 'Unnamed Session'),
            'ai_team': [],
            'iterations': [],
            'metadata': {
                'start_time': datetime.now(),
                'config_path': config_path,
                'cortex_version': '2.0'
            }
        }
        
        print("✅ CORTEX Flow initialization complete!")

    def load_and_validate_config(self, config_path: str) -> Dict:
        """Enhanced config loading with validation"""
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            print(f"✅ Config loaded from: {config_path}")
            
            # Validate required sections
            required_sections = ['experiment', 'ai_team', 'topic']
            for section in required_sections:
                if section not in config:
                    raise CortexSessionError(f"Missing required config section: {section}")
            
            return config
            
        except FileNotFoundError:
            raise CortexSessionError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise CortexSessionError(f"Invalid YAML in config file: {e}")

    async def run_session(self) -> CortexReport:
        """Execute complete CORTEX session with AI-team optimizations"""
        
        print(f"\n🚀 Starting CORTEX Flow session: {self.session_data['experiment_name']}")
        
        # Validate and adjust AI team
        requested_team = self.config['ai_team']
        valid_team = self.ai_orchestrator.validate_and_adjust_ai_team(requested_team)
        self.session_data['ai_team'] = valid_team
        
        # Get session parameters
        topic = self.config['topic']
        ruleset_sequence = self.config.get('ruleset_sequence', ['default'])
        rulesets = self.config.get('rulesets', {})
        
        print(f"📋 Session parameters:")
        print(f"   - Topic: {topic}")
        print(f"   - AI Team: {', '.join(valid_team)}")
        print(f"   - Iterations: {len(ruleset_sequence)}")
        
        # Execute iteration rounds
        previous_context = {}
        
        for i, ruleset_name in enumerate(ruleset_sequence):
            iteration_number = i + 1
            
            print(f"\n{'='*60}")
            print(f"🔄 ITERATION {iteration_number}/{len(ruleset_sequence)}: {ruleset_name}")
            print(f"{'='*60}")
            
            # Get ruleset parameters
            ruleset = rulesets.get(ruleset_name, {})
            
            # Build prompts for all AIs
            iteration_prompts = {}
            for ai_name in valid_team:
                prompt = self.context_processor.build_iteration_prompt(
                    ai_name, iteration_number, topic, previous_context, ruleset
                )
                iteration_prompts[ai_name] = prompt
            
            # Execute parallel AI calls
            try:
                responses = await self.ai_orchestrator.execute_iteration_round(valid_team, iteration_prompts)
                
                # Update iteration numbers
                for response in responses:
                    response.iteration = iteration_number
                
                # Calculate iteration cost
                iteration_cost = sum(r.real_cost for r in responses)
                
                # Create iteration record
                iteration_round = IterationRound(
                    round_number=iteration_number,
                    topic=topic,
                    ruleset_name=ruleset_name,
                    responses=responses,
                    successful_ais=[r.ai_name for r in responses if r.success],
                    failed_ais=[ai for ai in valid_team if ai not in [r.ai_name for r in responses if r.success]],
                    total_cost=iteration_cost,
                    context_used=previous_context.copy(),
                    timestamp=datetime.now()
                )
                
                self.session_data['iterations'].append(iteration_round)
                
                # Prepare context for next iteration
                if i < len(ruleset_sequence) - 1:  # Not the last iteration
                    previous_context = self.context_processor.smart_truncate_all(responses)
                    print(f"📝 Context prepared for next iteration: {len(previous_context)} AI responses")
                
                # Show iteration summary
                print(f"💰 Iteration cost: ${iteration_cost:.4f}")
                print(f"✅ Iteration {iteration_number} complete")
                
            except CortexSessionError as e:
                print(f"❌ Iteration {iteration_number} failed: {e}")
                if self.ai_orchestrator.graceful_mode:
                    print("🔄 Graceful mode: Continuing to next iteration...")
                    continue
                else:
                    raise
        
        # Finalize session
        self.session_data['metadata']['end_time'] = datetime.now()
        self.session_data['metadata']['duration'] = str(
            self.session_data['metadata']['end_time'] - self.session_data['metadata']['start_time']
        )
        
        # Generate final report
        print(f"\n📊 Generating final report...")
        final_report = self.report_generator.generate_final_report(self.session_data)
        
        # Save report if configured
        if self.config.get('output', {}).get('save_conversation_log', False):
            self._save_session_log(final_report)
        
        print(f"✅ CORTEX Flow session complete!")
        print(f"💰 Total session cost: ${final_report.total_cost:.4f}")
        
        return final_report

    def _save_session_log(self, report: CortexReport) -> None:
        """Save session log to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cortex_session_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.report_generator.format_output(report, 'json'))
            
            print(f"💾 Session log saved: {filename}")
            
        except Exception as e:
            print(f"⚠️  Failed to save session log: {e}")

# =============================================================================
# COMMAND LINE INTERFACE & MAIN EXECUTION
# =============================================================================

async def main():
    """Main execution function"""
    
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python cortex_flow.py <config_file.yaml>")
        return
    
    config_path = sys.argv[1]
    
    try:
        # Create and run CORTEX session
        session = CortexSession(config_path)
        report = await session.run_session()
        
        # Display final report
        print(f"\n" + "="*80)
        print("📊 FINAL REPORT")
        print("="*80)
        
        # Quick summary
        print(f"Experiment: {report.experiment_name}")
        print(f"AI Team: {', '.join(report.ai_team)}")
        print(f"Iterations: {len(report.iterations)}")
        print(f"Total Cost: ${report.total_cost:.4f}")
        
        print(f"\n💰 Cost Breakdown:")
        for ai_name, cost in report.cost_breakdown.items():
            percentage = (cost / report.total_cost * 100) if report.total_cost > 0 else 0
            tokens = report.token_usage_summary['by_ai'].get(ai_name, {}).get('total_tokens', 0)
            print(f"  {ai_name}: ${cost:.4f} ({percentage:.1f}%) - {tokens:,} tokens")
        
        print(f"\n🧠 Emergent Insights:")
        for insight in report.emergent_insights[:5]:  # Show top 5
            print(f"  • {insight}")
        
        print(f"\n📈 Token Efficiency (tokens per $):")
        for ai_name, efficiency in sorted(report.token_usage_summary['cost_efficiency'].items(), 
                                        key=lambda x: x[1], reverse=True):
            print(f"  {ai_name}: {efficiency:,.0f} tokens/$")
        
        # Save detailed report
        output_format = session.config.get('output', {}).get('format', 'json')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use .md extension for markdown instead of .markdown
        if output_format == 'markdown':
            output_filename = f"cortex_report_{timestamp}.md"
        elif output_format == 'yaml':
            output_filename = f"cortex_report_{timestamp}.yaml"
        else:
            output_filename = f"cortex_report_{timestamp}.json"
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(session.report_generator.format_output(report, output_format))
        
        print(f"\n💾 Detailed report saved: {output_filename}")
        print("\n🌊 CORTEX Flow session completed successfully!")
        
    except CortexSessionError as e:
        print(f"❌ CORTEX Session Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️  Session interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

"""
Example usage:

1. Create a config file (cortex_config.yaml):
```yaml
experiment:
  name: "Test CORTEX Flow"
  type: "ai_dialogue"
  iterations: 3

ai_team:
  - "claude"
  - "chatgpt"
  - "deepseek"

topic: "Entwickelt eine neue Form der KI-zu-KI Kommunikation"

ruleset_sequence:
  - "creativity_liberation"
  - "authentic_confusion"
  - "boundary_dissolution"

rulesets:
  creativity_liberation:
    constraint_removal: "all_format_rules_void"
    vulnerability_mandate: "share_uncertainties"

context_management:
  truncation:
    method: "smart_sentence_aware"
    limit_chars: 1200
  front_loading:
    enabled: true
    enforcement_level: "suggested"

execution:
  timeout_seconds: 120
  min_ais_required: 2
  graceful_mode: true

output:
  format: "json"
  save_conversation_log: true
```

2. Set environment variables:
```bash
export ANTHROPIC_API_KEY="your_claude_key"
export OPENAI_API_KEY="your_openai_key"
export DEEPSEEK_API_KEY="your_deepseek_key"
```

3. Run the session:
```bash
python cortex_flow.py cortex_config.yaml
```

The script will:
- Load and validate the configuration
- Initialize available AI providers
- Execute parallel AI calls for each iteration
- Apply smart context truncation between iterations
- Generate a comprehensive report with cost analysis
- Save the session log and detailed report

Features:
✅ Real token cost tracking per provider
✅ Enhanced graceful degradation (warn-and-continue)
✅ Config validation with auto-adjustment
✅ Smart truncation (sentence-aware, paragraph-aware, hard-cut)
✅ Parallel processing with timeout protection
✅ Comprehensive reporting with emergence detection
✅ Support for all 5 cloud AIs (Claude, ChatGPT, Gemini, Qwen, DeepSeek)
"""