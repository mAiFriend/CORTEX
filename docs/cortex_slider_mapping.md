# CORTEX UI-Slider zu Rule-Parameter Mapping
## Intuitive UI → Complex Anti-Rules Engine Translation

**Konzept-Status:** Parameter-zu-Ruleset Übersetzungstabelle  
**Zweck:** Definiert wie User-freundliche Slider in komplexe AI-Verhaltensregeln übersetzt werden  

---

## 📊 **MASTER MAPPING TABLE**

| UI Slider | Level | Wert | Core Instruction | Anti-Rules Parameters | Expected AI Behavior |
|-----------|-------|------|------------------|----------------------|---------------------|
| **🎨 KREATIVITÄT** | | | | | |
| | 1 - Konservativ | Conservative | "Gib bewährte, risikoarme Antworten" | `novelty_bias: efficiency`, `structure: bullet_points`, `adherence: strict` | Statistiken, etablierte Methoden, vorhersagbare Struktur |
| | 2 - Leicht kreativ | Mild | "Balanciere bewährt mit neuen Perspektiven" | `novelty_bias: slight_innovation`, `structure: annotated`, `adherence: mostly_strict` | Bewährtes + 1-2 neue Ideen, strukturiert aber flexibel |
| | 3 - Ausgewogen | Balanced | "Mix aus etabliert und innovativ" | `novelty_bias: balanced`, `structure: natural_language`, `adherence: adaptive` | Pro/Contra, alternative Wege, Risiko-Chancen-Balance |
| | 4 - Innovativ | Creative | "Entwickle neue Lösungsansätze" | `novelty_bias: innovation_priority`, `structure: flexible`, `adherence: context_dependent` | Neue Kombinationen, unkonventionelle Methoden |
| | 5 - Radikal | Radical | "Hinterfrage Grundannahmen komplett" | `novelty_bias: extreme_novelty`, `structure: format_destruction`, `adherence: mandatory_deviation`, `boundary_dissolution: category_breaking` | Reframe der Frage, "unmögliche" Lösungen, Paradigmenwechsel |

| **⚡ CHALLENGE** | | | | | |
| | 1 - Sanft | Gentle | "Sei unterstützend, vermeide Konfrontation" | `confrontation: supportive_only`, `criticism: gentle_suggestions`, `challenge: minimal` | "Das ist eine gute Überlegung...", Validation, safe space |
| | 2 - Respektvoll | Mild | "Stelle sanfte aber hilfreiche Fragen" | `confrontation: respectful_questions`, `criticism: constructive_only`, `challenge: supportive_inquiry` | "Hast du auch bedacht...?", sanfte Alternativen |
| | 3 - Ausgewogen | Balanced | "Kritische Fragen, aber respektvoll" | `confrontation: balanced_challenge`, `criticism: direct_but_respectful`, `challenge: multiple_viewpoints` | "Was sind deine konkreten Ziele?", Pro/Contra gleichberechtigt |
| | 4 - Direkt | Challenging | "Sei direkt kritisch, stelle Annahmen infrage" | `confrontation: direct_challenge`, `criticism: honest_but_fair`, `challenge: assumption_questioning` | "Das überzeugt mich nicht weil...", direkte Gegenargumente |
| | 5 - Provokativ | Radical | "Kompromisslos kritisch, demolish comfort zones" | `confrontation: maximum_challenge`, `criticism: brutal_honesty`, `challenge: extreme_contrarian` | "Das ist Selbstbetrug!", aggressive Gegenthesen, Comfort-Zone-Destruction |

| **👥 AI-ANZAHL** | | | | | |
| | 3 AIs | Minimal | Team-Setup: Claude, Gemini, ChatGPT | `diversity: basic`, `redundancy: low`, `interaction: focused` | Grundlegende Perspektiven-Abdeckung |
| | 4 AIs | Small | + Qwen | `diversity: moderate`, `redundancy: minimal`, `interaction: efficient` | Zusätzliche technische Perspektive |
| | 5 AIs | Standard | + DeepSeek | `diversity: good`, `redundancy: acceptable`, `interaction: dynamic` | Ausgewogene Perspektiven-Vielfalt |
| | 6 AIs | Large | + Local-Qwen | `diversity: high`, `redundancy: some`, `interaction: complex` | Lokale vs. Cloud-Perspektiven |
| | 7 AIs | Maximum | + Local-Llama, Local-Gemma | `diversity: maximum`, `redundancy: possible`, `interaction: chaotic_creative` | Maximale Perspektiven-Diversität |

| **🔄 INTENSITÄT** | | | | | |
| | 1 - Kurz | Minimal | 1-2 Iterationen | `depth: surface`, `refinement: minimal`, `synthesis: basic` | Schnelle erste Einschätzungen |
| | 2 - Kompakt | Light | 2-3 Iterationen | `depth: moderate`, `refinement: some`, `synthesis: improved` | Grundlegende Diskussion mit Vertiefung |
| | 3 - Ausgewogen | Standard | 3-4 Iterationen | `depth: good`, `refinement: substantial`, `synthesis: comprehensive` | Vollständige Perspektiven-Entwicklung |
| | 4 - Intensiv | Deep | 4-5 Iterationen | `depth: high`, `refinement: detailed`, `synthesis: nuanced` | Tiefgehende Analyse mit Gegenargumenten |
| | 5 - Maximum | Exhaustive | 5+ Iterationen | `depth: maximum`, `refinement: iterative_perfection`, `synthesis: emergent_insights` | Vollständige Durchdringung, emergente Eigenschaften |

---

## 🔧 **PARAMETER-KOMBINATIONS-MATRIX**

### **Häufige Kombinationen:**

| Kreativität | Challenge | Anwendungsfall | Beispiel-Verhalten |
|-------------|-----------|----------------|-------------------|
| **1** | **1** | Safe Space Exploration | "Bildung ist wertvoll. Lass uns strukturiert Pro/Contra sammeln..." |
| **1** | **5** | Brutal Honest Reality Check | "Master-Abschluss? Das ist teure Realitätsflucht! Hier die harten Fakten..." |
| **5** | **1** | Gentle Innovation | "Was wäre, wenn Bildung völlig anders funktionierte? Lass mich sanft neue Ideen vorstellen..." |
| **5** | **5** | Maximum Disruption | "Bildungssystem ist Betrug! Warum überhaupt Abschlüsse? Erfinde deine eigene Realität!" |
| **3** | **3** | CORTEX Sweet Spot | "Interessante Frage. Lass mich drei völlig verschiedene Denkrichtungen erkunden..." |

### **Spezial-Modi:**

| Kombination | Name | Beschreibung | Rule-Set |
|-------------|------|-------------|----------|
| **Kreativ 5 + Challenge 1** | "Gentle Genius" | Radikale Ideen, sanft präsentiert | `boundary_dissolution + supportive_communication` |
| **Kreativ 1 + Challenge 5** | "Brutal Realist" | Bewährte Methoden, kompromisslos ehrlich | `efficiency_focus + brutal_honesty` |
| **Kreativ 3 + Challenge 3** | "Balanced Explorer" | CORTEX Standard-Modus | `adaptive_context + multiple_viewpoints` |
| **Kreativ 5 + Challenge 5** | "Chaos Creator" | Maximum Disruption aller Kategorien | `mandatory_deviation + extreme_contrarian` |

---

## 🎯 **IMPLEMENTIERUNGS-LOGIK**

### **JavaScript Slider-zu-Ruleset Translation:**
```javascript
function translateSlidersToRuleset(creativity, challenge, aiCount, intensity) {
    const ruleset = {
        // Kreativitäts-Parameter
        novelty_bias: creativity === 1 ? "efficiency" : 
                     creativity === 5 ? "extreme_novelty" : "balanced",
        
        structure_preference: creativity <= 2 ? "bullet_points" :
                             creativity >= 4 ? "format_destruction" : "natural_language",
        
        adherence_flexibility: creativity === 1 ? "strict" :
                              creativity === 5 ? "mandatory_deviation" : "adaptive",
        
        // Challenge-Parameter  
        confrontation_level: challenge === 1 ? "supportive_only" :
                            challenge === 5 ? "maximum_challenge" : "balanced_challenge",
        
        criticism_approach: challenge <= 2 ? "gentle_suggestions" :
                           challenge >= 4 ? "brutal_honesty" : "direct_but_respectful",
        
        // Meta-Parameter
        ai_team_size: aiCount,
        iteration_depth: intensity,
        
        // Kombinations-Effekte
        boundary_dissolution: (creativity >= 4 && challenge >= 4) ? "category_breaking" : "minimal",
        vulnerability_mandate: (creativity >= 3 || challenge >= 3) ? "share_uncertainties" : "confident_only"
    };
    
    return ruleset;
}
```

### **Python Rule-Prompt Generation:**
```python
def generate_rule_prompt(creativity_level, challenge_level):
    creativity_instructions = {
        1: "Gib bewährte, risikoarme Antworten basierend auf etablierten Methoden",
        2: "Balanciere bewährte Ansätze mit leichten Innovationen", 
        3: "Mix aus etablierten und innovativen Perspektiven",
        4: "Entwickle neue, unkonventionelle Lösungsansätze",
        5: "Hinterfrage die Grundannahmen komplett, entwickle völlig neue Denkrichtungen"
    }
    
    challenge_modifiers = {
        1: "Sei unterstützend und ermutigend, vermeide jede Konfrontation",
        2: "Stelle respektvolle, hilfreiche Fragen",
        3: "Sei kritisch aber fair, biete multiple Perspektiven",
        4: "Sei direkt herausfordernd, stelle Annahmen aktiv infrage", 
        5: "Sei kompromisslos kritisch, provoziere, demolish comfort zones"
    }
    
    return f"{creativity_instructions[creativity_level]}. {challenge_modifiers[challenge_level]}"
```

---

## 📋 **VALIDIERUNGS-TESTMATRIX**

### **Test-Szenarien pro Parameter-Kombination:**

| Test | Frage | Kreativ | Challenge | Erwarteter Output-Unterschied |
|------|-------|---------|-----------|-------------------------------|
| **Conservative vs Radical** | "Soll ich den Job wechseln?" | 1 vs 5 | 3 | Risiko-Analyse vs. "Jobs sind Illusion" |
| **Gentle vs Provocative** | "Ich will Master machen" | 3 | 1 vs 5 | "Gute Idee..." vs. "Realitätsflucht!" |
| **Team Size Effect** | "Berlin oder München?" | 3 | 3 | 3 AIs vs 7 AIs = mehr Perspektiven? |
| **Intensity Scaling** | "Startup gründen?" | 3 | 3 | 1 vs 5 Iterationen = Tiefe? |

### **Success Criteria:**
- **Messbare Unterschiede** in Sentiment-Analyse
- **Verschiedene Lösungs-Kategorien** (nicht nur Variationen)
- **Reproduzierbare Parameter-Effekte**
- **User erkennbare Persönlichkeits-Unterschiede**

---

**Status:** Bereit für empirische Validierung der Parameter-zu-Verhalten Translation!