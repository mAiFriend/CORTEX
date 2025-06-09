#!/usr/bin/env python3
"""
CORTEX AI Orchestrator - Multi-Provider AI Integration (STABILIZED)
Handles parallel AI queries with graceful degradation and proper error handling
"""

import asyncio
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Will use environment variables directly

# AI Provider imports with error handling
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  Anthropic not available: pip install anthropic")

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️  Google AI not available: pip install google-generativeai")

from cortex_types import AIResponse, CortexSessionError, TOKEN_COSTS


class AIOrchestrator:
    """Manages multiple AI providers with parallel execution and robust error handling"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize AI clients based on available API keys"""
        self.config = config
        self.execution_config = config.get('execution', {})
        
        # Execution settings
        self.timeout = self.execution_config.get('timeout_seconds', 120)
        self.min_ais_required = self.execution_config.get('min_ais_required', 1)
        self.graceful_mode = self.execution_config.get('graceful_mode', True)
        
        # Initialize AI clients
        self.ai_clients = self._initialize_ai_clients()
        
        # Token cost tracking
        self.token_costs = TOKEN_COSTS
        
        print(f"✅ Initialized {len(self.ai_clients)} AI providers")
        
        if not self.ai_clients:
            raise CortexSessionError("No AI providers could be initialized. Check API keys.")
    
    def _initialize_ai_clients(self) -> Dict[str, Any]:
        """Initialize available AI clients based on API keys with proper error handling"""
        clients = {}
        
        # Claude (Anthropic)
        if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
            try:
                client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                # Test connection with a simple validation
                clients['claude'] = client
                print("  ✓ Claude (Anthropic) initialized")
            except Exception as e:
                print(f"  ✗ Claude initialization failed: {e}")
        
        # ChatGPT (OpenAI)
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                # Use new OpenAI client initialization
                client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                clients['chatgpt'] = client
                print("  ✓ ChatGPT (OpenAI) initialized")
            except Exception as e:
                print(f"  ✗ ChatGPT initialization failed: {e}")
        
        # Gemini (Google)
        if GOOGLE_AVAILABLE and os.getenv('GOOGLE_API_KEY'):
            try:
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                model = genai.GenerativeModel('gemini-1.5-pro')
                clients['gemini'] = model
                print("  ✓ Gemini (Google) initialized")
            except Exception as e:
                print(f"  ✗ Gemini initialization failed: {e}")
        
        # Qwen (via OpenRouter)
        if os.getenv('OPENROUTER_API_KEY'):
            try:
                # OpenRouter uses OpenAI-compatible interface
                client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv('OPENROUTER_API_KEY')
                )
                clients['qwen'] = client
                print("  ✓ Qwen (OpenRouter) initialized")
            except Exception as e:
                print(f"  ✗ Qwen initialization failed: {e}")
        
        # DeepSeek
        if os.getenv('DEEPSEEK_API_KEY'):
            try:
                client = openai.OpenAI(
                    base_url="https://api.deepseek.com",
                    api_key=os.getenv('DEEPSEEK_API_KEY')
                )
                clients['deepseek'] = client
                print("  ✓ DeepSeek initialized")
            except Exception as e:
                print(f"  ✗ DeepSeek initialization failed: {e}")
        
        return clients
    
    def calculate_real_cost(self, ai_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate real cost based on provider-specific rates"""
        if ai_name not in self.token_costs:
            print(f"⚠️  Unknown AI for cost calculation: {ai_name}")
            return 0.0
        
        rates = self.token_costs[ai_name]
        input_cost = (input_tokens / 1_000_000) * rates['input']
        output_cost = (output_tokens / 1_000_000) * rates['output']
        
        return input_cost + output_cost
    
    async def validate_ai_team(self, requested_team: List[str]) -> List[str]:
        """Validate and filter AI team based on available clients"""
        valid_team = []
        
        for ai_name in requested_team:
            if ai_name in self.ai_clients:
                valid_team.append(ai_name)
            else:
                print(f"  ⚠️  {ai_name} not available (missing API key or client error)")
        
        # Check minimum AIs requirement
        if len(valid_team) < self.min_ais_required:
            if self.graceful_mode:
                print(f"  ⚠️  Only {len(valid_team)} AIs available, continuing anyway...")
            else:
                raise CortexSessionError(
                    f"Insufficient AIs: {len(valid_team)} available, "
                    f"{self.min_ais_required} required"
                )
        
        return valid_team
    
    async def query_all_ais(self, ai_team: List[str], topic: str, 
                           iteration: int, previous_context: Dict[str, str],
                           ruleset: Dict[str, Any]) -> List[AIResponse]:
        """Query all AIs in parallel with timeout protection and proper error handling"""
        # Build prompts for each AI
        tasks = []
        for ai_name in ai_team:
            if ai_name in self.ai_clients:
                prompt = self._build_iteration_prompt(
                    ai_name, iteration, topic, previous_context, ruleset
                )
                
                task = asyncio.create_task(
                    self._query_ai_with_timeout(ai_name, prompt, iteration),
                    name=f"query_{ai_name}_{iteration}"
                )
                tasks.append(task)
        
        # Execute all queries in parallel
        print(f"\n🚀 Querying {len(tasks)} AIs in parallel...")
        start_time = time.time()
        
        try:
            # Use gather with return_exceptions to handle partial failures gracefully
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_time = time.time() - start_time
            print(f"⏱️  All queries completed in {total_time:.2f}s")
            
            # Process results and separate successful responses from errors
            valid_responses = []
            for i, result in enumerate(results):
                if isinstance(result, AIResponse):
                    valid_responses.append(result)
                elif isinstance(result, Exception):
                    ai_name = ai_team[i] if i < len(ai_team) else f"AI_{i}"
                    print(f"  ❌ Error in {ai_name} query: {result}")
                else:
                    print(f"  ⚠️  Unexpected result type from AI query: {type(result)}")
            
            return valid_responses
            
        except Exception as e:
            # Clean up any remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for cancellation to complete
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception:
                pass  # Ignore cancellation errors
            
            raise CortexSessionError(f"Parallel AI query execution failed: {e}") from e
    
    async def query_single_ai(self, ai_name: str, prompt: str, 
                             max_tokens: int = 1500) -> Optional[AIResponse]:
        """Query a single AI with timeout protection"""
        if ai_name not in self.ai_clients:
            raise CortexSessionError(f"AI client not available: {ai_name}")
        
        try:
            return await self._query_ai_with_timeout(ai_name, prompt, 0, max_tokens)
        except Exception as e:
            print(f"❌ Single AI query failed for {ai_name}: {e}")
            return None
    
    async def _query_ai_with_timeout(self, ai_name: str, prompt: str, 
                                   iteration: int, max_tokens: int = 1500) -> AIResponse:
        """Query single AI with timeout protection and comprehensive error handling"""
        try:
            # Apply timeout using asyncio.wait_for
            response = await asyncio.wait_for(
                self._query_single_ai_impl(ai_name, prompt, iteration, max_tokens),
                timeout=self.timeout
            )
            return response
            
        except asyncio.TimeoutError:
            print(f"  ⏱️  {ai_name} timed out after {self.timeout}s")
            return AIResponse(
                ai_name=ai_name,
                response="",
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                real_cost=0.0,
                response_time=self.timeout,
                iteration=iteration,
                timestamp=datetime.now(),
                success=False,
                error_message=f"Timeout after {self.timeout}s"
            )
        except Exception as e:
            print(f"  ❌ {ai_name} error: {e}")
            return AIResponse(
                ai_name=ai_name,
                response="",
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                real_cost=0.0,
                response_time=0.0,
                iteration=iteration,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    async def _query_single_ai_impl(self, ai_name: str, prompt: str, 
                                   iteration: int, max_tokens: int) -> AIResponse:
        """Implementation of single AI query with provider-specific handling"""
        start_time = time.time()
        
        try:
            if ai_name == 'claude':
                response_data = await self._query_claude(prompt, max_tokens)
            elif ai_name == 'chatgpt':
                response_data = await self._query_chatgpt(prompt, max_tokens)
            elif ai_name == 'gemini':
                response_data = await self._query_gemini(prompt, max_tokens)
            elif ai_name == 'qwen':
                response_data = await self._query_qwen(prompt, max_tokens)
            elif ai_name == 'deepseek':
                response_data = await self._query_deepseek(prompt, max_tokens)
            else:
                raise ValueError(f"Unknown AI provider: {ai_name}")
            
            response_time = time.time() - start_time
            
            # Calculate real cost
            real_cost = self.calculate_real_cost(
                ai_name,
                response_data['input_tokens'],
                response_data['output_tokens']
            )
            
            print(f"  ✓ {ai_name}: {response_data['output_tokens']} tokens "
                  f"in {response_time:.2f}s (${real_cost:.4f})")
            
            return AIResponse(
                ai_name=ai_name,
                response=response_data['response'],
                input_tokens=response_data['input_tokens'],
                output_tokens=response_data['output_tokens'],
                total_tokens=response_data['total_tokens'],
                real_cost=real_cost,
                response_time=response_time,
                iteration=iteration,
                timestamp=datetime.now(),
                success=True
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            raise CortexSessionError(f"{ai_name} query failed after {response_time:.2f}s: {e}") from e
    
    async def _query_claude(self, prompt: str, max_tokens: int = 1500) -> Dict[str, Any]:
        """Query Claude API with modern async handling"""
        client = self.ai_clients['claude']
        
        # Use asyncio.to_thread for proper async handling in Python 3.9+
        try:
            response = await asyncio.to_thread(
                client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
        except AttributeError:
            # Fallback for older Python versions
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
            )
        
        return {
            'response': response.content[0].text,
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens,
            'total_tokens': response.usage.input_tokens + response.usage.output_tokens
        }
    
    async def _query_chatgpt(self, prompt: str, max_tokens: int = 1500) -> Dict[str, Any]:
        """Query ChatGPT API with modern async handling"""
        client = self.ai_clients['chatgpt']
        
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
        except AttributeError:
            # Fallback for older Python versions
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
            )
        
        return {
            'response': response.choices[0].message.content,
            'input_tokens': response.usage.prompt_tokens if response.usage else len(prompt.split()) * 1.3,
            'output_tokens': response.usage.completion_tokens if response.usage else len(response.choices[0].message.content.split()) * 1.3,
            'total_tokens': response.usage.total_tokens if response.usage else (len(prompt.split()) + len(response.choices[0].message.content.split())) * 1.3
        }
    
    async def _query_gemini(self, prompt: str, max_tokens: int = 1500) -> Dict[str, Any]:
        """Query Gemini API with proper async handling"""
        model = self.ai_clients['gemini']
        
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens)
            )
        except AttributeError:
            # Fallback for older Python versions
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens)
                )
            )
        
        # Token counting for Gemini (approximation)
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(response.text.split()) * 1.3 if response.text else 0
        
        return {
            'response': response.text if response.text else "",
            'input_tokens': int(input_tokens),
            'output_tokens': int(output_tokens),
            'total_tokens': int(input_tokens + output_tokens)
        }
    
    async def _query_qwen(self, prompt: str, max_tokens: int = 1500) -> Dict[str, Any]:
        """Query Qwen via OpenRouter with proper async handling"""
        client = self.ai_clients['qwen']
        
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="qwen/qwen-2.5-72b-instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
        except AttributeError:
            # Fallback for older Python versions
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="qwen/qwen-2.5-72b-instruct",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
            )
        
        return {
            'response': response.choices[0].message.content,
            'input_tokens': response.usage.prompt_tokens if response.usage else len(prompt.split()) * 1.3,
            'output_tokens': response.usage.completion_tokens if response.usage else len(response.choices[0].message.content.split()) * 1.3,
            'total_tokens': response.usage.total_tokens if response.usage else (len(prompt.split()) + len(response.choices[0].message.content.split())) * 1.3
        }
    
    async def _query_deepseek(self, prompt: str, max_tokens: int = 1500) -> Dict[str, Any]:
        """Query DeepSeek API with proper async handling"""
        client = self.ai_clients['deepseek']
        
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
        except AttributeError:
            # Fallback for older Python versions
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
            )
        
        return {
            'response': response.choices[0].message.content,
            'input_tokens': response.usage.prompt_tokens if response.usage else len(prompt.split()) * 1.3,
            'output_tokens': response.usage.completion_tokens if response.usage else len(response.choices[0].message.content.split()) * 1.3,
            'total_tokens': response.usage.total_tokens if response.usage else (len(prompt.split()) + len(response.choices[0].message.content.split())) * 1.3
        }
    
    def _build_iteration_prompt(self, ai_name: str, iteration: int, topic: str,
                               previous_context: Dict[str, str], ruleset: Dict[str, Any]) -> str:
        """Build iteration prompt with context and ruleset parameters"""
        # AI archetypes for better collaboration
        ai_archetypes = {
            "claude": "Claude (Analytical Philosopher)",
            "chatgpt": "ChatGPT (Versatile Collaborator)", 
            "gemini": "Gemini (Creative Synthesizer)",
            "qwen": "Qwen (Efficient Processor)",
            "deepseek": "DeepSeek (Deep Reasoner)"
        }
        
        archetype = ai_archetypes.get(ai_name, f"{ai_name} (AI Collaborator)")
        
        # Build context section from previous responses
        context_section = ""
        if previous_context:
            context_section = "\nPREVIOUS AI RESPONSES:\n"
            for ai, response in previous_context.items():
                if ai != ai_name:  # Don't include own previous response
                    context_section += f"\n{ai}: {response}\n"
        
        # Build ruleset parameters
        ruleset_params = ""
        if ruleset:
            ruleset_params = "\nACTIVE COMMUNICATION RULES:\n"
            for param, value in ruleset.items():
                ruleset_params += f"- {param}: {value}\n"
        
        # Construct complete prompt
        prompt = f"""Du bist {archetype} im CORTEX Framework.

TOPIC: {topic}

{context_section}

{ruleset_params}

Iteration {iteration}: Diskutiere das Thema aus deiner Perspektive. Beziehe dich auf andere AIs wenn relevant, bringe neue Einsichten ein, und sei authentisch in deiner Antwort.

Antworte in 200-400 Wörtern."""
        
        return prompt.strip()