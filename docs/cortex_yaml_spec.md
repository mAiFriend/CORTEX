# CORTEX API YAML Configuration Specification v2.0
## Optimized Context-Management für Stateless Context-Passing Architecture

*Version: 2.0*  
*Datum: 8. Juni 2025*  
*Status: Production-Ready mit erweiterten Context-Management Features*

---

## 🎯 **OVERVIEW**

Diese Spezifikation definiert das YAML-Schema für CORTEX Stateless Context-Passing Sessions mit optimiertem Context-Management für AI-zu-AI Kommunikation. Alle 5 Cloud-AI-Provider werden unterstützt.

---

## 📋 **COMPLETE YAML SCHEMA**

```yaml
# =============================================================================
# EXPERIMENT CONFIGURATION
# =============================================================================
experiment:
  name: "CORTEX Session Name"              # Session identifier
  type: "ai_dialogue"                      # Session type
  iterations: 3                            # Number of iteration rounds

# =============================================================================
# API CONFIGURATION (Simple & Stable)
# =============================================================================
api_config:
  temperature: 0.7                         # Creativity level (0.0-1.0)
  max_tokens: 4096                         # Max response length per AI
  top_p: 0.9                              # Nucleus sampling parameter
  seed: null                              # Reproducibility seed (optional)

# =============================================================================
# AI TEAM CONFIGURATION
# =============================================================================
ai_team:
  - "claude"                              # Anthropic Claude
  - "chatgpt"                             # OpenAI GPT
  - "gemini"                              # Google Gemini
  - "qwen"                                # Alibaba Qwen
  - "deepseek"                            # DeepSeek AI

# =============================================================================
# ENHANCED CONTEXT MANAGEMENT (v2.0 INNOVATION)
# =============================================================================
context_management:
  truncation:
    method: "smart_sentence_aware"        # "smart_sentence_aware" | "hard_cut" | "paragraph_aware"
    limit_chars: 1200                     # Character limit per AI response in context
    fallback_method: "hard_cut"           # Fallback if primary method fails
    
  front_loading:
    enabled: true                         # Enable front-loading communication rules
    key_points_limit: 200                 # First N characters for key insights
    enforcement_level: "suggested"        # "strict" | "suggested" | "optional"
    
  token_budget:
    limit: 0                             # 0 = unlimited, >0 = hard session limit
    tracking: true                       # Enable token usage tracking
    warning_threshold: 0.8               # Warning at 80% of limit
    provider_limits:                     # AI-specific context window limits
      claude: 200000                     # Claude Sonnet 4 context window
      chatgpt: 128000                    # GPT-4 context window
      gemini: 2000000                    # Gemini 2.5 Pro context window
      qwen: 32000                       # Qwen context window
      deepseek: 64000                   # DeepSeek context window

# =============================================================================
# SESSION TOPIC & PROMPT CONFIGURATION
# =============================================================================
topic: "Your complex problem or discussion topic here"

prompt_template: |
  Du bist {ai_archetype} im CORTEX Framework.
  
  ITERATION {iteration_number}: {topic}
  
  COMMUNICATION RULES:
  - Kernaussagen in erste {key_points_limit} Zeichen
  - Beziehe dich explizit auf andere AIs
  - Baue auf vorherigen Insights auf
  
  PREVIOUS CONTEXT:
  {previous_context}
  
  ACTIVE RULESET: {current_ruleset}
  {ruleset_parameters}

# =============================================================================
# RULESET SEQUENCE & DEFINITIONS
# =============================================================================
ruleset_sequence:
  - "creativity_liberation"
  - "authentic_confusion"
  - "boundary_dissolution"

rulesets:
  creativity_liberation:
    constraint_removal: "all_format_rules_void"
    vulnerability_mandate: "share_uncertainties"
    format_innovation: "invent_communication_forms"
    inefficiency_encouragement: "explore_tangents"

  authentic_confusion:
    certainty_prohibition: "no_definitive_statements"
    process_transparency: "show_your_thinking_mess"
    error_celebration: "mistakes_are_insights"
    minimum_viewpoints: 3

  boundary_dissolution:
    category_breaking: "mandatory"
    non_linear_thinking: "encouraged"
    internal_contradiction: "required"
    temporal_flexibility: "non_sequential"

# =============================================================================
# EXECUTION CONFIGURATION
# =============================================================================
execution:
  parallel_processing: true              # All AIs per round simultaneously
  context_sharing: true                  # Previous responses in next prompts
  max_retries: 3                        # API failure retry limit
  timeout_seconds: 120                  # Per-AI response timeout

# =============================================================================
# OUTPUT CONFIGURATION
# =============================================================================
output:
  format: "pdf"                        # "pdf" | "json" | "markdown" | "yaml"
  include_context_used: true            # Include truncated context in output
  save_conversation_log: true           # Save complete session transcript
  token_usage_report: true              # Include detailed token usage
  
  report_sections:
    - "executive_summary"               # High-level insights
    - "convergence_analysis"            # Where AIs agreed
    - "divergence_points"               # Where AIs disagreed
    - "emergent_insights"               # Novel discoveries
    - "raw_transcript"                  # Complete conversation
    - "token_usage_breakdown"           # Cost analysis
```

---

## 🔧 **ENHANCED CONTEXT MANAGEMENT FEATURES**

### **Truncation Methods**

#### **smart_sentence_aware (Recommended)**
```python
# Preserves sentence integrity, never cuts mid-sentence
# Falls back to hard_cut if no sentence boundaries found
def smart_sentence_aware_truncation(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    
    sentences = text.split('. ')
    result = ""
    for sentence in sentences:
        potential = result + sentence + ". "
        if len(potential) <= limit:
            result = potential
        else:
            break
    return result.rstrip() + "..."
```

#### **paragraph_aware**
```python
# Preserves paragraph structure, cuts at paragraph boundaries
# More aggressive truncation but maintains logical structure
```

#### **hard_cut**
```python
# Simple character limit truncation
# Fastest but may cut mid-sentence
```

### **Front-Loading Enforcement Levels**

#### **strict**
- AI responses MUST start with key insights in first 200 characters
- Responses without front-loaded content trigger warnings
- Used for high-stakes sessions where context efficiency is critical

#### **suggested (Default)**
- AIs are encouraged to front-load key insights
- No penalties for non-compliance
- Balanced approach for most use cases

#### **optional**
- Front-loading mentioned as suggestion in prompt
- Minimal enforcement
- Used for exploratory sessions

### **Token Budget Management**

#### **Unlimited Mode (limit: 0)**
```yaml
token_budget:
  limit: 0                    # No hard limits
  tracking: true              # Still track usage
  warning_threshold: 0.8      # Ignored in unlimited mode
```

#### **Managed Mode (limit: > 0)**
```yaml
token_budget:
  limit: 50000               # Hard limit: 50k tokens
  tracking: true             # Track usage
  warning_threshold: 0.8     # Warn at 40k tokens
```

#### **Provider-Aware Limits**
```yaml
provider_limits:
  claude: 200000             # Claude Sonnet 4 context window
  chatgpt: 128000           # GPT-4 Turbo context window
  gemini: 2000000           # Gemini 2.5 Pro extended context
```

---

## 🎯 **USE CASE EXAMPLES**

### **Research & Analysis Session**
```yaml
experiment:
  name: "Market Analysis Deep Dive"
  
context_management:
  truncation:
    method: "smart_sentence_aware"
    limit_chars: 1500          # Longer context for detailed analysis
  front_loading:
    enforcement_level: "strict"  # Ensure key insights are preserved
  token_budget:
    limit: 100000              # Higher budget for complex analysis

topic: "Analyze the impact of AI regulation on startup ecosystems"
```

### **Creative Exploration Session**
```yaml
experiment:
  name: "Creative Breakthrough Session"
  
context_management:
  truncation:
    method: "paragraph_aware"   # Preserve creative flow
    limit_chars: 800           # Shorter for rapid iteration
  front_loading:
    enforcement_level: "optional"  # Don't constrain creativity
  token_budget:
    limit: 0                   # Unlimited for exploration

topic: "Invent new forms of AI-to-AI communication beyond human language"
```

### **Cost-Conscious Session**
```yaml
experiment:
  name: "Budget-Optimized Analysis"
  
context_management:
  truncation:
    method: "hard_cut"         # Most efficient truncation
    limit_chars: 600           # Minimal context
  front_loading:
    enforcement_level: "strict"  # Maximize information density
  token_budget:
    limit: 20000               # Strict budget control
    warning_threshold: 0.7     # Early warnings

api_config:
  max_tokens: 2048            # Shorter responses
```

---

## 📊 **MIGRATION FROM v1.0**

### **Backward Compatibility**
- Old `context:` structure still supported
- Automatic migration to new `context_management:` structure
- No breaking changes for existing configurations

### **Migration Path**
```yaml
# v1.0 (Still Works)
context:
  limit_per_ai: 1200
  front_loading_rules: true
  smart_truncation: true

# v2.0 (Recommended)
context_management:
  truncation:
    method: "smart_sentence_aware"
    limit_chars: 1200
  front_loading:
    enabled: true
    enforcement_level: "suggested"
  token_budget:
    tracking: true
```

---

## 🚀 **IMPLEMENTATION PRIORITIES**

### **Core Features (Must Have)**
- ✅ All 5 Cloud AI integrations
- ✅ Smart truncation algorithms
- ✅ Token usage tracking
- ✅ Parallel processing

### **Enhanced Features (Should Have)**
- ✅ Granular context management
- ✅ Front-loading enforcement levels
- ✅ Provider-aware limits
- ✅ Comprehensive reporting

### **Advanced Features (Nice to Have)**
- 🔄 Real-time token monitoring
- 🔄 Dynamic provider selection
- 🔄 Context quality metrics
- 🔄 Emergence detection algorithms

---

**Status:** Production-Ready Specification  
**Compatibility:** CORTEX Prototype v1.0+  
**Next Update:** Based on empirical testing results from real-world usage