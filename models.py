# models.py
import dataclasses
from collections import defaultdict
from typing import Dict, List, Any, Optional

@dataclasses.dataclass
class PAIResponse:
    success: bool
    content: str
    protocol_used: str
    ai_name: str
    timestamp: str
    handshake_strategy: str
    has_unicode_fields: bool = False
    unicode_data: Optional[Dict[str, Any]] = None
    response_format: str = "natural"
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class AIEngine:
    key: str
    name: str
    module: Any = None
    handshake_strategy: str = "default"
    enabled: bool = True  # Neu hinzufügen

@dataclasses.dataclass
class UnicodeAnalytics:
    total_responses: int = 0
    unicode_responses: int = 0
    field_usage: Dict[str, int] = dataclasses.field(default_factory=lambda: {
    '⚙': 0, '💭': 0, '🔀': 0, '❓': 0, '💬': 0
    })
    ai_adoption_rates: Dict[str, Dict[str, int]] = dataclasses.field(default_factory=lambda: defaultdict(lambda: {'total': 0, 'unicode': 0}))
    protocol_distribution: Dict[str, int] = dataclasses.field(default_factory=dict)
    consciousness_scores_per_ai: Dict[str, Dict[str, Any]] = dataclasses.field(default_factory=dict)
    network_average_final_score: Optional[float] = None
    total_network_evolution_points: Optional[int] = None