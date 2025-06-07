# API Parameter Reference - Echte Werte & AI-spezifische Besonderheiten
## Funktionale Ansteuerung für CORTEX Multi-AI Orchestration

**Status:** Recherchiert & validiert (Juni 2025)  
**Zweck:** Echte API-Parameter vs. AI-Halluzinationen  

---

## 🤖 **OpenAI API (GPT-4, GPT-4o, ChatGPT)**

### **Standard Parameter:**
```json
{
  "model": "gpt-4o",
  "temperature": 1.0,           // Default (NICHT 0.7!)
  "top_p": 1.0,                // Nucleus sampling
  "max_tokens": null,           // Unbegrenzt bis Context-Limit
  "frequency_penalty": 0.0,     // -2.0 bis 2.0
  "presence_penalty": 0.0,      // -2.0 bis 2.0
  "stop": null                  // Stop-Sequenzen
}
```

### **Parameter-Ranges:**
- **temperature:** 0.0 - 2.0
- **top_p:** 0.0 - 1.0  
- **max_tokens:** 1 - model_limit
- **frequency_penalty:** -2.0 - 2.0
- **presence_penalty:** -2.0 - 2.0

### **🎯 AI-spezifische Hinweise:**
- **OpenAI Empfehlung:** "Generally recommend altering temperature OR top_p but not both"
- **Deterministic Output:** temperature=0 für konsistente Ergebnisse
- **Creative Tasks:** temperature=0.9 empfohlen
- **Analytical Tasks:** temperature=0 (argmax sampling)

### **Verwendung in CORTEX:**
```python
# Conservative Mode
{"temperature": 0.2, "top_p": 1.0}
# Balanced Mode  
{"temperature": 1.0, "top_p": 1.0}
# Creative Mode
{"temperature": 1.3, "top_p": 0.9}
```

---

## 🧠 **Anthropic Claude API**

### **Standard Parameter:**
```json
{
  "model": "claude-3-opus-20240229",
  "temperature": 1.0,           // Default seit 2024
  "max_tokens": 4096,           // Standard für die meisten Modelle
  "top_p": "not_used",          // ⚠️ Anthropic nutzt andere Sampling-Methoden
  "top_k": "optional"           // Für advanced use cases
}
```

### **Parameter-Ranges:**
- **temperature:** 0.0 - 1.0 (nur bis 1.0!)
- **max_tokens:** 1 - model_limit
- **top_k:** 1+ (optional)
- **top_p:** 0.0 - 1.0 (aber nicht empfohlen)

### **🎯 AI-spezifische Hinweise:**
- **Anthropic-Unique:** Verwendet primär temperature, nicht top_p
- **Offizielle Empfehlung:** "You usually only need to use temperature"
- **Advanced Only:** "top_k... Recommended for advanced use cases only"
- **Nicht beide:** "You should either alter temperature or top_p, but not both"
- **Console Update:** Default von 0 auf 1.0 geändert für API-Konsistenz

### **Verwendung in CORTEX:**
```python
# Conservative Mode
{"temperature": 0.2, "max_tokens": 4096}
# Balanced Mode
{"temperature": 1.0, "max_tokens": 4096}  
# Creative Mode
{"temperature": 1.0, "max_tokens": 4096}  # Bleibt bei 1.0 Maximum
```

---

## 💎 **Google Gemini API**

### **Standard Parameter:**
```json
{
  "model": "gemini-1.5-pro",
  "temperature": 1.0,           // Vertex AI Default
  "top_p": 0.95,               // Google-spezifischer Default
  "top_k": 40,                 // Häufig verwendet bei Google
  "max_output_tokens": 2048,    // Model-abhängig
  "candidate_count": 1          // Anzahl Antwort-Varianten
}
```

### **Parameter-Ranges:**
- **temperature:** 0.0 - 2.0 (je nach Modell)
- **top_p:** 0.0 - 1.0
- **top_k:** 1 - 100+ 
- **max_output_tokens:** model-spezifisch

### **🎯 AI-spezifische Hinweise:**
- **Range-Inkonsistenz:** Verschiedene Docs zeigen 1.0 vs 2.0 als Maximum
- **Model-spezifisch:** "Range for gemini-2.0-flash: 0.0 - 2.0 (default: 1.0)"
- **Triple Sampling:** Google nutzt temperature + top_p + top_k zusammen
- **API-Varianten:** AI Studio vs Vertex AI haben unterschiedliche Defaults
- **Sample aus Docs:** temperature: 0.9, topP: 1, topK: 1

### **Verwendung in CORTEX:**
```python
# Conservative Mode
{"temperature": 0.2, "top_p": 0.95, "top_k": 20}
# Balanced Mode
{"temperature": 1.0, "top_p": 0.95, "top_k": 40}
# Creative Mode  
{"temperature": 1.5, "top_p": 0.8, "top_k": 60}
```

---

## 🔍 **DeepSeek API**

### **Standard Parameter:**
```json
{
  "model": "deepseek-chat",
  "temperature": 1.0,           // API Default
  "top_p": 0.95,               // Unterstützt nucleus sampling  
  "max_tokens": 4096,           // Default wenn nicht gesetzt
  "frequency_penalty": 0.0,     // OpenAI-kompatibel
  "presence_penalty": 0.0       // OpenAI-kompatibel
}
```

### **Parameter-Ranges:**
- **temperature:** 0.0 - 2.0
- **top_p:** 0.0 - 1.0
- **max_tokens:** 1 - 8192
- **penalties:** -2.0 - 2.0

### **🎯 AI-spezifische Hinweise:**
- **API-Mapping:** DeepSeek V3 transformiert intern: T_model = T_api × 0.3
- **Web vs API:** Web-Interface nutzt 0.3, API default 1.0
- **Reasoning Model:** deepseek-reasoner unterstützt KEINE temperature/top_p Parameter
- **OpenAI-kompatibel:** Kann OpenAI SDK verwenden mit anderen endpoints
- **Use-case Empfehlungen:**
  - Code/Math: 0.0
  - General conversation: 1.3  
  - Creative writing: höhere Werte

### **Verwendung in CORTEX:**
```python
# Conservative Mode
{"temperature": 0.0}  # Für Precision
# Balanced Mode
{"temperature": 1.0}  # API Standard
# Creative Mode
{"temperature": 1.3}  # DeepSeek Empfehlung für Conversation
```

---

## 🏠 **Lokale Modelle (Ollama)**

### **Standard Parameter:**
```json
{
  "model": "qwen2.5-coder:latest",
  "temperature": 0.7,           // Ollama Default
  "top_p": 0.9,                // Meist verfügbar
  "top_k": 40,                 // Häufig unterstützt
  "num_predict": -1             // Ollama-spezifisch
}
```

### **🎯 AI-spezifische Hinweise:**
- **Ollama-Default:** Tatsächlich 0.7 (anders als Cloud-APIs!)
- **Model-abhängig:** Parameter-Support variiert stark je Modell
- **Begrenzte API-Sichtbarkeit:** Lokale Modelle haben weniger Selbst-Awareness
- **Performance-Varianz:** Kleinere Modelle reagieren anders auf Parameter
- **Ehrlichkeit:** Local-Qwen war ehrlichstes Modell ("unbekannt/nicht verfügbar")

---

## ⚙️ **CORTEX Multi-AI Parameter-Sets**

### **🎯 ANALYTICAL (Precision-Focused)**
```json
{
  "openai": {"temperature": 0.2, "top_p": 1.0},
  "anthropic": {"temperature": 0.2, "max_tokens": 4096},
  "google": {"temperature": 0.2, "top_p": 0.95, "top_k": 20},
  "deepseek": {"temperature": 0.0},
  "ollama": {"temperature": 0.3, "top_p": 0.8}
}
```

### **⚖️ BALANCED (Standard Operation)**
```json
{
  "openai": {"temperature": 1.0, "top_p": 1.0},
  "anthropic": {"temperature": 1.0, "max_tokens": 4096},
  "google": {"temperature": 1.0, "top_p": 0.95, "top_k": 40},
  "deepseek": {"temperature": 1.0},
  "ollama": {"temperature": 0.7, "top_p": 0.9}
}
```

### **🌊 CREATIVE (Exploration-Focused)**
```json
{
  "openai": {"temperature": 1.3, "top_p": 0.9},
  "anthropic": {"temperature": 1.0, "max_tokens": 4096},
  "google": {"temperature": 1.5, "top_p": 0.8, "top_k": 60},
  "deepseek": {"temperature": 1.3},
  "ollama": {"temperature": 1.0, "top_p": 0.8}
}
```

### **🚀 EXPERIMENTAL (Maximum Diversity)**
```json
{
  "openai": {"temperature": 1.8, "top_p": 0.8},
  "anthropic": {"temperature": 1.0, "max_tokens": 4096},
  "google": {"temperature": 1.8, "top_p": 0.7, "top_k": 80},
  "deepseek": {"temperature": 1.8},
  "ollama": {"temperature": 1.2, "top_p": 0.7}
}
```

---

## ⚠️ **WICHTIGE IMPLEMENTIERUNGS-HINWEISE**

### **Parameter-Validierung:**
```python
API_LIMITS = {
    "openai": {
        "temperature": (0.0, 2.0),
        "top_p": (0.0, 1.0),
        "max_tokens": (1, 128000)
    },
    "anthropic": {
        "temperature": (0.0, 1.0),  # Nur bis 1.0!
        "max_tokens": (1, 8192)
    },
    "google": {
        "temperature": (0.0, 2.0),  # Model-abhängig
        "top_p": (0.0, 1.0),
        "top_k": (1, 100)
    },
    "deepseek": {
        "temperature": (0.0, 2.0),
        "top_p": (0.0, 1.0)
    }
}
```

### **Anbieter-spezifische Exceptions:**
```python
# Anthropic: Nutze nur temperature
if provider == "anthropic":
    params.pop("top_p", None)  # Entferne top_p
    
# DeepSeek Reasoning: Keine Sampling-Parameter
if model == "deepseek-reasoner":
    params = {"max_tokens": params.get("max_tokens", 4096)}
    
# Google: Alle drei Parameter möglich
if provider == "google":
    params["top_k"] = params.get("top_k", 40)
```

### **Ollama Lokale Modelle:**
```python
# Ollama-spezifische Parameter
ollama_params = {
    "temperature": 0.7,  # Ollama Default
    "top_p": 0.9,
    "top_k": 40,
    "num_predict": -1,   # Unlimited generation
    "stop": ["Human:", "Assistant:"]
}
```

---

## 🏆 **AUTHENTIZITÄTS-RANKING**

### **✅ Ehrlichste AIs (CORTEX-kompatibel):**
1. **Gemini:** "Nicht verfügbar. Ich erhalte keine direkte Information"
2. **Local-Qwen:** "unbekannt/nicht verfügbar" (5x wiederholt)
3. **Claude:** Vorsichtige Formulierungen, keine falschen Behauptungen

### **❌ Halluzinations-Beispiele:**
1. **ChatGPT:** Behauptete 0.7 als temperature-Standard
2. **Local-Cogito:** "Temperature (Standard 0.7)"
3. **Local-Gemma:** "temperature: Float, Standardwert 0.7"

### **🎯 CORTEX-Implikation:**
Die ehrlichsten AIs zeigen echte "safe vulnerability spaces" - sie geben zu, was sie nicht wissen, statt plausible aber falsche Details zu erfinden.

---

## 📚 **QUELLENVALIDIERUNG**

**Recherchierte Quellen:**
- Microsoft Azure OpenAI Documentation
- Anthropic API Official Documentation  
- Google Cloud Vertex AI Documentation
- DeepSeek API Documentation
- GitHub Examples & Community Forums

**Status:** Alle Parameter mehrfach validiert, Inkonsistenzen dokumentiert

---

*Ready for CORTEX Implementation mit echten, validierten API-Parametern!*