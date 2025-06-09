# CORTEX Architecture Blueprint
## Stateless Context-Passing für AI-zu-AI Dialog

---

## 🏗️ **CORE ARCHITECTURE PRINCIPLES**

### **1. Stateless Context-Passing**
- **Kein Session Management** - Jeder AI-Call ist unabhängig
- **Context via Prompt** - Vorherige Antworten werden in den Prompt eingebettet
- **API-Agnostic** - Funktioniert mit jeder AI-API (Claude, ChatGPT, Gemini, Qwen)

### **2. Intelligent Context Limits**
- **Smart Truncation** - Erste 800-1200 Zeichen pro AI-Antwort als Context
- **Front-Loading Rules** - AIs lernen: Kernaussagen an den Anfang
- **Token-Explosion Prevention** - Feste Limits verhindern exponentielles Wachstum

### **3. Echte Iterative Dialoge**
- **Sequential Rounds** - Alle AIs parallel pro Runde
- **Cross-Referencing** - AIs beziehen sich explizit aufeinander
- **Dialog Evolution** - Aufbau über mehrere Runden hinweg

---

## 🔄 **SYSTEM FLOW ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────┐
│                    CORTEX SESSION FLOW                     │
└─────────────────────────────────────────────────────────────┘

1. INPUT PHASE
   ┌─────────────────┐
   │  User Question  │ → Original Prompt (200 Tokens)
   │  + AI Team      │   
   │  + Parameters   │   
   └─────────────────┘

2. ITERATION ROUND (Parallel Processing)
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │   AI 1: Claude  │    │  AI 2: ChatGPT  │    │   AI 3: Gemini  │
   │                 │    │                 │    │                 │
   │ Prompt Building │    │ Prompt Building │    │ Prompt Building │
   │ ├─Original Q.   │    │ ├─Original Q.   │    │ ├─Original Q.   │
   │ ├─Context (1.2k)│    │ ├─Context (1.2k)│    │ ├─Context (1.2k)│
   │ └─Front Rules   │    │ └─Front Rules   │    │ └─Front Rules   │
   │                 │    │                 │    │                 │
   │ Response (2k)   │    │ Response (2k)   │    │ Response (2k)   │
   └─────────────────┘    └─────────────────┘    └─────────────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
                                   ▼
   ┌─────────────────────────────────────────────────────────────┐
   │               CONTEXT PREPARATION                           │
   │                                                             │
   │  Smart Truncation: First 1200 chars per response           │
   │  ├─ Sentence-aware cutting (no mid-sentence breaks)        │
   │  ├─ Preserve key insights through front-loading            │
   │  └─ Total context: ~6k chars for next round                │
   └─────────────────────────────────────────────────────────────┘

3. NEXT ITERATION (Repeat 2-5 times)
   Same parallel processing, but with enriched context

4. OUTPUT SYNTHESIS
   ┌─────────────────────────────────────────────────────────────┐
   │                    FINAL REPORT                             │
   │                                                             │
   │  • Executive Summary                                        │
   │  • Key Insights Matrix                                      │
   │  • Convergence/Divergence Analysis                          │
   │  • Actionable Recommendations                               │
   │  • Raw Dialog Transcript                                    │
   └─────────────────────────────────────────────────────────────┘
```

---

## 🧠 **PROMPT CONSTRUCTION ARCHITECTURE**

### **Dynamic Prompt Builder**
```python
def build_cortex_prompt(
    original_question: str,
    ai_role: str,
    iteration_number: int,
    previous_context: List[str],  # Already truncated responses
    front_loading_rules: Dict
) -> str:

    # Template Structure:
    """
    ROLE: {ai_role} - {unique_perspective}
    
    ITERATION {iteration_number}: {original_question}
    
    COMMUNICATION RULES:
    - Kernaussagen in erste 200 Zeichen
    - Explizite Referenzen auf andere AIs
    - Aufbau auf vorherigen Insights
    
    PREVIOUS CONTRIBUTIONS:
    [Claude]: {truncated_response_1200_chars}...
    [ChatGPT]: {truncated_response_1200_chars}...
    [Gemini]: {truncated_response_1200_chars}...
    
    YOUR TASK:
    - Iteration 1: Eröffne mit deiner Position
    - Iteration 2-4: Baue auf anderen auf, bringe neue Perspektiven
    - Iteration 5: Synthese und Schlussfolgerungen
    """
```

### **Context Limit Calculator**
```python
CONTEXT_LIMITS = {
    "team_size_3": 1200,    # Mehr Detail pro AI möglich
    "team_size_5": 1000,    # Standard Setup
    "team_size_7": 800,     # Kompaktere Contexts nötig
    "team_size_10": 600     # Maximum Compression
}

def calculate_context_budget(num_ais: int, max_iterations: int) -> int:
    """
    Dynamische Context-Limits basierend auf Team-Größe
    Ziel: Max 50k Tokens total per Session
    """
    base_limit = 50000 // (num_ais * max_iterations)
    return min(1200, max(600, base_limit))
```

---

## 📊 **TOKEN MANAGEMENT ARCHITECTURE**

### **Token Budget System**
```
SESSION BUDGET EXAMPLE (5 AIs, 3 Iterations):

Iteration 1:
├─ Input: 5 × 200 tokens (original prompt) = 1,000 tokens
├─ Output: 5 × 1,500 tokens (responses) = 7,500 tokens
└─ Context Prep: 5 × 1,000 chars → 5,000 tokens

Iteration 2:
├─ Input: 5 × (200 + 1,000) tokens = 6,000 tokens
├─ Output: 5 × 1,500 tokens = 7,500 tokens
└─ Context Prep: 5 × 1,000 chars → 5,000 tokens

Iteration 3:
├─ Input: 5 × (200 + 2,000) tokens = 11,000 tokens
├─ Output: 5 × 1,500 tokens = 7,500 tokens

TOTAL SESSION: ~45,000 tokens (~$0.90 at GPT-4 pricing)
```

### **Smart Truncation Algorithm**
```python
def smart_truncate(response: str, limit: int = 1000) -> str:
    """
    Sentence-aware truncation preserving meaning
    """
    if len(response) <= limit:
        return response
    
    # Find last complete sentence within limit
    sentences = response.split('. ')
    result = ""
    
    for sentence in sentences:
        potential = result + sentence + ". "
        if len(potential) <= limit:
            result = potential
        else:
            break
    
    return result + "..." if result != response else result
```

---

## 🎯 **FRONT-LOADING RULES SYSTEM**

### **AI Communication Optimization**
```python
FRONT_LOADING_RULES = {
    "key_points_first": {
        "instruction": "Erste 200 Zeichen: Deine Hauptthese",
        "example": "Hauptpunkt: X ist falsch weil Y. [Details folgen...]"
    },
    
    "explicit_references": {
        "instruction": "Beziehe dich direkt auf andere AIs",
        "example": "Claude erwähnte X, aber ich sehe Problem Y..."
    },
    
    "dense_communication": {
        "instruction": "Maximiere Informationsdichte",
        "example": "Statt 'Das ist interessant' → 'Das löst Problem X'"
    },
    
    "meta_coordination": {
        "instruction": "Erkenne Diskussionsmuster",
        "example": "Wir konvergieren bei X, divergieren bei Y"
    }
}
```

---

## 🔧 **IMPLEMENTATION COMPONENTS**

### **Core Modules**
```
cortex/
├── core/
│   ├── session_manager.py      # Session lifecycle
│   ├── prompt_builder.py       # Dynamic prompt construction
│   ├── context_processor.py    # Smart truncation & limits
│   └── ai_orchestrator.py      # Parallel API coordination
│
├── integrations/
│   ├── anthropic_api.py        # Claude integration
│   ├── openai_api.py           # ChatGPT integration
│   ├── google_api.py           # Gemini integration
│   └── openrouter_api.py       # Multi-provider access
│
├── utils/
│   ├── token_calculator.py     # Budget management
│   ├── truncation.py           # Smart context limits
│   └── report_generator.py     # Output synthesis
│
└── config/
    ├── ai_profiles.py          # AI roles & personalities
    ├── ruleset_library.py      # Front-loading rules
    └── limits.py               # Context & token limits
```

### **Data Flow Interfaces**
```python
# Session Input
class CortexSession:
    question: str
    ai_team: List[str]          # ["claude", "chatgpt", "gemini"]
    max_iterations: int = 3
    context_limit: int = 1000
    front_loading_rules: Dict

# Iteration State
class IterationRound:
    round_number: int
    responses: Dict[str, str]   # ai_name → response
    truncated_context: Dict[str, str]  # ai_name → first 1000 chars
    token_usage: Dict[str, int]

# Final Output
class CortexReport:
    executive_summary: str
    key_insights: List[str]
    convergence_analysis: str
    divergence_points: List[str]
    raw_transcript: List[IterationRound]
    token_usage_total: int
```

---

## 🚀 **SCALABILITY & PERFORMANCE**

### **Horizontal Scaling**
- **AI Team Size:** 3-10 AIs per session
- **Concurrent Sessions:** Multiple independent sessions
- **API Load Balancing:** Distribute across providers

### **Performance Optimization**
- **Parallel Processing:** All AIs in round process simultaneously
- **Context Caching:** Reuse truncated contexts within session
- **Token Prediction:** Estimate costs before execution

### **Quality Assurance**
- **Context Quality Metrics:** Measure information preservation
- **Cross-Reference Tracking:** Monitor AI-to-AI dialogue depth
- **Emergence Detection:** Identify novel insights from collaboration

---

## 💡 **IMPLEMENTATION PRIORITIES**

### **Phase 1: MVP (Week 1)**
1. ✅ **Basic Prompt Builder** - Dynamic context injection
2. ✅ **Smart Truncation** - Sentence-aware limits
3. ✅ **Parallel AI Calls** - Async processing
4. ✅ **Simple Report Generation** - Raw output formatting

### **Phase 2: Enhancement (Week 2)**
1. 🔄 **Front-Loading Rules** - Communication optimization
2. 🔄 **Token Budget Management** - Cost control
3. 🔄 **Quality Metrics** - Dialogue depth measurement
4. 🔄 **Web Interface** - User-friendly session management

### **Phase 3: Production (Week 3-4)**
1. 📋 **Advanced Reporting** - Insight synthesis
2. 📋 **Performance Optimization** - Speed & reliability
3. 📋 **Scale Testing** - Large teams & long sessions
4. 📋 **Integration Testing** - Real-world use cases

---

**Status:** Architecture Blueprint Complete - Ready for Implementation  
**Next:** Begin Phase 1 MVP Development with Focus on Core Components