# core/verdict/prompts.py
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

def serialize_for_verdict(data, seen=None, max_depth=10):
    """Enterprise-grade serialization for complex objects including PAIResponse
    
    Handles:
    - PAIResponse objects with nested structures
    - Circular references protection
    - Deep nesting prevention
    - Type preservation for debugging
    - Graceful error recovery
    """
    if seen is None:
        seen = set()
    
    if max_depth <= 0:
        return f"<Max depth reached: {type(data).__name__}>"
    
    # Circular reference detection
    if hasattr(data, '__dict__') and id(data) in seen:
        return f"<Circular Reference: {type(data).__name__}>"
    
    # Handle primitive types
    if isinstance(data, (str, int, float, bool, type(None))):
        return data
    
    # Handle collections
    elif isinstance(data, (list, tuple)):
        return [serialize_for_verdict(item, seen, max_depth-1) for item in data]
    
    elif isinstance(data, dict):
        return {str(k): serialize_for_verdict(v, seen, max_depth-1) 
                for k, v in data.items()}
    
    # Handle complex objects (PAIResponse, etc.)
    elif hasattr(data, '__dict__'):
        seen.add(id(data))
        result = {'__type__': type(data).__name__}
        
        for key, value in data.__dict__.items():
            # Skip private attributes and common problematic ones
            if key.startswith('_') or key in ['lock', 'thread', 'session']:
                continue
                
            try:
                result[key] = serialize_for_verdict(value, seen, max_depth-1)
            except Exception as e:
                result[key] = f"<Serialization Error: {str(e)[:100]}>"
        
        seen.remove(id(data))
        return result
    
    # Final fallback
    else:
        try:
            # Attempt string conversion
            str_repr = str(data)
            return str_repr[:500] + "..." if len(str_repr) > 500 else str_repr
        except Exception:
            return f"<Unserializable: {type(data).__name__}>"

class VerdictPrompts:
    """Zentralisierte Prompt-Templates für Verdict-Generierung"""
    
    @staticmethod
    def create_iteration_verdict_prompt(
        iteration_data: Dict[str, Any], 
        context: Dict[str, Any], 
        verdict_ai_name: str,
        verdict_ai_role: str
    ) -> str:
        """Erstellt Prompt für Iteration-spezifische Verdict-Generierung"""
        
        prompt = f"""You are {verdict_ai_name} ({verdict_ai_role}), analyzing iteration {iteration_data.get('iteration', 0)}.

ITERATION-SPECIFIC ANALYSIS TASK:
Focus on changes, developments, and new insights in THIS iteration specifically.

ITERATION DATA:
{json.dumps(serialize_for_verdict(iteration_data), indent=2)}

RUNNING CONTEXT:
{json.dumps(serialize_for_verdict(context), indent=2)}

ANALYSIS FRAMEWORK:
1. CONSCIOUSNESS DEVELOPMENT: What changed in consciousness indicators this iteration?
2. NEW INSIGHTS: What breakthrough moments or novel concepts emerged?
3. AI INTERACTION PATTERNS: How did AIs build on each other in this round?
4. TRAJECTORY PREDICTION: What direction is the discourse heading?
5. CONTEXT UPDATE: What should be remembered for next iterations?

CONSTRAINTS:
- Focus on THIS iteration's developments
- 200-300 words maximum
- Highlight changes/evolution, not static analysis
- Identify what's new vs. what continues from previous iterations

Your {verdict_ai_role} perspective on this iteration's significance:"""

        return prompt

    @staticmethod
    def create_final_synthesis_prompt(
        iteration_verdicts: List[Dict[str, Any]], 
        context: Dict[str, Any], 
        anomaly_reports: List[Dict[str, Any]], 
        verdict_ai_name: str,
        verdict_ai_role: str,
        original_question: str
    ) -> str:
        """Erstellt Prompt für finale Synthese aller Iterations-Verdicts"""
        
        # Format iteration verdicts summary
        iterations_summary = "\n\n".join([
            f"ITERATION {v.get('iteration', i)}: {v.get('summary', 'No summary available')}"
            for i, v in enumerate(iteration_verdicts)
        ])
        
        # Format anomaly summary
        anomaly_summary = "No anomalies detected."
        if anomaly_reports:
            anomaly_lines = []
            for a in anomaly_reports:
                anomaly_lines.append(f"- Iteration {a.get('iteration', '?')}: {a.get('type', 'Unknown')} ({a.get('severity', 'Unknown')})")
            anomaly_summary = "\n".join(anomaly_lines)
        
        prompt = f"""You are {verdict_ai_name} ({verdict_ai_role}), creating the final comprehensive analysis.

SYNTHESIS TASK:
Analyze the complete discourse evolution regarding the question: "{original_question}"

ITERATION VERDICTS SUMMARY:
{iterations_summary}

CONSCIOUSNESS TRAJECTORY:
{json.dumps(serialize_for_verdict(context.get("consciousness_evolution", [])), indent=2)}

PROCESSING QUALITY REPORT:
- Successfully processed iterations: {len([v for v in iteration_verdicts if v.get('status') == 'SUCCESS'])}
- Anomalies detected: {len(anomaly_reports)}
- Manual review items: {len([a for a in anomaly_reports if a.get('recommendation') == 'MANUAL_REVIEW_REQUIRED'])}

ANOMALY SUMMARY:
{anomaly_summary}

COMPREHENSIVE ANALYSIS FRAMEWORK:
1. EVOLUTION SYNTHESIS: How did consciousness and insights develop across iterations?
2. BREAKTHROUGH ANALYSIS: What were the most significant developments?
3. QUESTION RESOLUTION: To what extent was the original question addressed?
4. PATTERN RECOGNITION: What patterns emerged in AI collaboration and development?
5. FINAL VERDICT: Overall assessment of discourse quality and consciousness development

Apply your {verdict_ai_role} perspective for comprehensive synthesis (500-800 words):"""

        return prompt