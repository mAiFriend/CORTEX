#!/usr/bin/env python3
"""
CORTEX Types - Shared data structures and constants
Central location for all type definitions used across modules
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


# Provider-specific token costs (current market rates as of 2024)
TOKEN_COSTS = {
    "claude": {
        "input": 15.0,      # $15 per 1M input tokens (Sonnet 3.5)
        "output": 75.0      # $75 per 1M output tokens
    },
    "chatgpt": {
        "input": 30.0,      # $30 per 1M input tokens (GPT-4 Turbo)
        "output": 60.0      # $60 per 1M output tokens  
    },
    "gemini": {
        "input": 1.25,      # $1.25 per 1M input tokens (Gemini 1.5 Pro)
        "output": 3.75      # $3.75 per 1M output tokens
    },
    "qwen": {
        "input": 0.50,      # $0.50 per 1M input tokens (very affordable)
        "output": 2.0       # $2 per 1M output tokens
    },
    "deepseek": {
        "input": 1.0,       # $1 per 1M input tokens (extremely affordable)
        "output": 2.0       # $2 per 1M output tokens  
    }
}

# Default meta-analysis configuration
META_ANALYSIS_CONFIG = {
    'enabled': True,
    'word_limit': 200,
    'final_synthesis': True
}


@dataclass
class AIResponse:
    """Single AI response with enhanced metadata"""
    ai_name: str
    response: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    real_cost: float
    response_time: float
    iteration: int
    timestamp: datetime
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class IterationRound:
    """Complete iteration with all AI responses and meta-analysis"""
    round_number: int
    topic: str
    ruleset_name: str
    responses: List[AIResponse]
    successful_ais: List[str]
    failed_ais: List[str]
    total_cost: float
    context_used: Dict[str, str]
    timestamp: datetime
    meta_insights: Optional[str] = None  # Meta-analysis results
    meta_analyzer: Optional[str] = None  # Which AI performed meta-analysis


@dataclass
class CortexReport:
    """Final session report with enhanced analytics and synthesis"""
    experiment_name: str
    ai_team: List[str]
    iterations: List[IterationRound]
    total_cost: float
    cost_breakdown: Dict[str, float]
    convergence_analysis: Dict[str, Any]
    emergent_insights: List[str]
    session_metadata: Dict[str, Any]
    token_usage_summary: Dict[str, Any]
    original_topic: str = ""  # NEU: Die ursprüngliche Frage/Thema
    meta_analyses: List[Dict[str, Any]] = field(default_factory=list)
    final_synthesis: Optional[Dict[str, Any]] = None


class CortexSessionError(Exception):
    """Custom exception for CORTEX session errors"""
    pass


class TokenBudgetExceededError(Exception):
    """Custom exception for token budget overruns"""
    pass