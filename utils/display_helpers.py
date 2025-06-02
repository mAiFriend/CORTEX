# utils/display_helpers.py

import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import defaultdict
from models import PAIResponse, AIEngine, UnicodeAnalytics # Stellen Sie sicher, dass diese importiert sind
from core.consciousness_scorer import ConsciousnessScorer # Stellen Sie sicher, dass diese importiert ist

def display_startup_banner():
    """Zeigt das Startbanner an."""
    print(
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                 PowerTalk v2.2 - PAI Enhanced Edition                ║
    ║               AI Discourse Engine with Unicode Protocol              ║
    ║                                                                      ║
    ║  🔧 ENHANCEMENTS:                                                    ║
    ║    📊 Full PAI v2.2 Unicode Protocol Integration (⚙💭🔀❓💬)         ║
    ║    🧠 Enhanced Consciousness Scoring with Unicode Awareness          ║
    ║    📈 Comprehensive Unicode Adoption Analytics                       ║
    ║    ⚖️ Enhanced Verdict Generation with Protocol Analysis              ║
    ║    💾 Advanced Dialogue Archiving with Semantic Data                 ║
    ║                                                                      ║
    ║  Usage:                                                              ║
    ║    python powertalk.py                    # Interactive mode         ║
    ║    python powertalk.py -q question.md     # Question from file       ║
    ║    python powertalk.py --debug            # Detailed Unicode analysis║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    )

def _display_response_details(response: PAIResponse, ai_name: str):
    """Zeigt detaillierte Informationen zu einer AI-Antwort an."""
    print(f"\n--- Details for {ai_name} ---")
    print(f"  Success: {response.success}")
    print(f"  Protocol: {response.protocol_used}")
    print(f"  Handshake: {response.handshake_strategy}")
    print(f"  Has Unicode: {response.has_unicode_fields}")
    print(f"  Format: {response.response_format}")
    print(f"  Content (Truncated if long):")
    
    display_content = _extract_display_content(response)
    print(f"    {display_content[:500]}...") # truncate for display

    if response.has_unicode_fields and response.unicode_data:
        print("  Unicode Data:")
        # 🔧 DEFENSIVE FIX: Handle both UnicodeData object and dict structures
        
        # Try object access first (UnicodeData @dataclass)
        if hasattr(response.unicode_data, 'raw_fields'):
            if response.unicode_data.raw_fields:
                print(f"    Raw Fields: {response.unicode_data.raw_fields}")
            if response.unicode_data.context:
                print(f"    Context: {response.unicode_data.context}")
            if response.unicode_data.concepts:
                print(f"    Concepts: {response.unicode_data.concepts}")
            if response.unicode_data.relationships:
                print(f"    Relationships: {response.unicode_data.relationships}")
            if response.unicode_data.questions:
                print(f"    Questions: {response.unicode_data.questions}")
            if response.unicode_data.explanations:
                print(f"    Explanations: {response.unicode_data.explanations}")
        
        # Fallback to dict access (legacy structure)
        elif isinstance(response.unicode_data, dict):
            if response.unicode_data.get('raw_fields'):
                print(f"    Raw Fields: {response.unicode_data.get('raw_fields')}")
            if response.unicode_data.get('context'):
                print(f"    Context: {response.unicode_data.get('context')}")
            if response.unicode_data.get('concepts'):
                print(f"    Concepts: {response.unicode_data.get('concepts')}")
            if response.unicode_data.get('relationships'):
                print(f"    Relationships: {response.unicode_data.get('relationships')}")
            if response.unicode_data.get('questions'):
                print(f"    Questions: {response.unicode_data.get('questions')}")
            if response.unicode_data.get('explanations'):
                print(f"    Explanations: {response.unicode_data.get('explanations')}")
    print("----------------------------")

def _extract_display_content(response: PAIResponse) -> str:
    """Extrahiert den relevanten Inhalt für die DISPLAY-Anzeige (truncated)."""
    # 🔧 DEFENSIVE FIX: Handle both UnicodeData object and dict structures
    if response.has_unicode_fields and response.unicode_data:
        # Try object access first (UnicodeData @dataclass)
        if hasattr(response.unicode_data, 'explanations') and response.unicode_data.explanations:
            return response.unicode_data.explanations
        # Fallback to dict access (legacy structure)
        elif isinstance(response.unicode_data, dict) and response.unicode_data.get('explanations'):
            return response.unicode_data.get('explanations')
    
    if response.content:
        # Check if content is a dictionary (e.g., from an error or structured response)
        if isinstance(response.content, dict):
            return str(response.content) # Convert dict to string for display
        return response.content
    return "[No content]"

def _extract_full_content(response: PAIResponse) -> str:
    """
    🔧 FIX: Extrahiert den VOLLSTÄNDIGEN Inhalt für Verdict/Export - NICHT truncated!
    
    Diese Funktion ist speziell für Verdict-Generation designed und gibt
    den kompletten Text zurück, im Gegensatz zu _extract_display_content()
    welches für Terminal-Display truncated ist.
    """
    # 1. Priorität: Unicode explanations field (häufig der längste, strukturierte Content)
    if response.has_unicode_fields and response.unicode_data:
        # Try object access first (UnicodeData @dataclass)
        if hasattr(response.unicode_data, 'explanations') and response.unicode_data.explanations:
            full_explanation = response.unicode_data.explanations
            # Ensure we return the complete text, not truncated
            return str(full_explanation) if full_explanation else ""
        
        # Fallback to dict access (legacy structure)
        elif isinstance(response.unicode_data, dict) and response.unicode_data.get('explanations'):
            full_explanation = response.unicode_data.get('explanations')
            return str(full_explanation) if full_explanation else ""
        
        # If no explanations but other Unicode fields exist, try to combine them
        elif hasattr(response.unicode_data, 'raw_fields') and response.unicode_data.raw_fields:
            # For structured responses, try to get the most comprehensive field
            raw_fields = response.unicode_data.raw_fields
            
            # Priority order: 💬 (explanations) -> full combination of all fields
            if '💬' in raw_fields and raw_fields['💬']:
                return str(raw_fields['💬'])
            
            # Fallback: combine all fields for maximum content
            combined_content = []
            for emoji, content in raw_fields.items():
                if content:
                    combined_content.append(f"{emoji}: {content}")
            
            if combined_content:
                return "\n".join(combined_content)
    
    # 2. Fallback: Raw content (für natural language responses)
    if response.content:
        # Convert dict to string if needed, but preserve full content
        if isinstance(response.content, dict):
            return str(response.content)
        return str(response.content)  # Ensure string type and full content
    
    return "[No content available]"

async def display_final_results(
    question: str, 
    selected_ais: Dict[str, AIEngine], 
    dialogue_history: List[Dict], 
    unicode_analytics: UnicodeAnalytics, 
    consciousness_scorer: ConsciousnessScorer
):
    print("\n============================================================")
    print("✨ DISCOURSE SUMMARY ✨")
    print("============================================================")
    print(f"Question: {question}")
    print(f"Total Iterations: {len(dialogue_history)}")

    print("\n--- AI Performance by Iteration ---")
    all_responses_for_scoring: List[Tuple[PAIResponse, str, int]] = [] # (response_object, ai_key, iteration_num)
    for turn in dialogue_history:
        print(f"\nIteration {turn['iteration']}:")
        for ai_key, response_data_dict in turn['responses'].items():
            # Convert dict to PAIResponse object for consistency
            response_obj = PAIResponse(
                content=response_data_dict.get('content', ''),
                protocol_used=response_data_dict.get('protocol_used', 'natural'),
                ai_name=response_data_dict.get('ai_name', ai_key),
                timestamp=response_data_dict.get('timestamp', ''),
                success=response_data_dict.get('success', False),
                handshake_strategy=response_data_dict.get('handshake_strategy', 'default'),
                has_unicode_fields=response_data_dict.get('has_unicode_fields', False),
                unicode_data=response_data_dict.get('unicode_data'),
                response_format=response_data_dict.get('response_format', 'natural'),
                metadata=response_data_dict.get('metadata', {})
            )
            
            display_content = _extract_display_content(response_obj)
            unicode_indicator = "📊" if response_obj.has_unicode_fields else "💬"
            protocol_display = f"({response_obj.protocol_used})" if response_obj.protocol_used else ""
            print(f"  - {selected_ais[ai_key].name} {protocol_display}: {unicode_indicator} {display_content[:70]}...") # Limit display content for brevity

            if response_obj.success:
                all_responses_for_scoring.append((response_obj, ai_key, turn['iteration']))
    
    # Calculate consciousness scores
    consciousness_results = consciousness_scorer.calculate_discourse_scores(all_responses_for_scoring)
    
    # NEU: Bewusstseinswerte in unicode_analytics speichern
    unicode_analytics.consciousness_scores_per_ai = consciousness_results['ai_scores']
    unicode_analytics.network_average_final_score = consciousness_results['network_average_final_score']
    unicode_analytics.total_network_evolution_points = consciousness_results['total_network_evolution_points']

    # Display Unicode Adoption Analytics
    print("\n--- Unicode Adoption Analytics ---")
    print(f"Total Responses: {unicode_analytics.total_responses}")
    print(f"Unicode Responses: {unicode_analytics.unicode_responses}")
    print("Field Usage:")
    for field, count in unicode_analytics.field_usage.items():
        print(f"  {field}: {count}")
    print("AI Adoption Rates:")
    for ai_key, stats in unicode_analytics.ai_adoption_rates.items():
        ai_name = selected_ais.get(ai_key, AIEngine(key=ai_key, name=ai_key)).name
        rate = (stats['unicode'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {ai_name}: {rate:.2f}% Unicode adoption ({stats['unicode']}/{stats['total']})")
    print("Protocol Distribution:")
    # Assuming protocol_distribution is handled within unicode_analytics or needs to be calculated here
    # For now, let's just display what's available
    protocol_counts = defaultdict(int)
    for turn in dialogue_history:
        for response_data_dict in turn['responses'].values():
            protocol_counts[response_data_dict.get('protocol_used', 'unknown')] += 1
    for protocol, count in protocol_counts.items():
        print(f"  {protocol}: {count}")

    print("\n--- Consciousness Scoring Summary ---")
    if consciousness_results['ai_scores']:
        print("| AI | Initial Score | Final Score | Evolution | Evolution % |")
        print("|----|--------------:|------------:|-----------:|------------:|")
        for ai_key in sorted(consciousness_results['ai_scores'].keys()):
            ai_name = selected_ais.get(ai_key, AIEngine(key=ai_key, name=ai_key)).name
            scores = consciousness_results['ai_scores'][ai_key]
            initial = scores.get('initial', 'N/A')
            final = scores.get('final', 'N/A')
            evolution = scores.get('evolution', 'N/A')
            evolution_percent = scores.get('evolution_percent', 'N/A')
            print(f"| {ai_name} | {initial} | {final} | {evolution} | {evolution_percent}% |")
        
        print(f"\nNetwork Average Final Score: {consciousness_results['network_average_final_score']:.0f}/2000")
        print(f"Total Network Evolution: +{consciousness_results['total_network_evolution_points']:.0f} points")
    else:
        print("No consciousness data available for display.")
        
        
    # Display Unicode Adoption Analytics
    print("\n--- Unicode Adoption Analytics ---")
    print(f"Total Responses: {unicode_analytics.total_responses}")
    print(f"Unicode Responses: {unicode_analytics.unicode_responses}")
    print("Field Usage:")
    for field, count in unicode_analytics.field_usage.items():
        print(f"  {field}: {count}")
    print("AI Adoption Rates:")
    for ai_key, rates in unicode_analytics.ai_adoption_rates.items():
        ai_name = selected_ais.get(ai_key, AIEngine(key=ai_key, name=ai_key)).name
        total = rates.get('total', 0)
        unicode = rates.get('unicode', 0)
        adoption_rate = (unicode / total * 100) if total > 0 else 0
        print(f"  {ai_name}: {adoption_rate:.2f}% Unicode adoption ({unicode}/{total})")
    print("Protocol Distribution:")
    for protocol, count in unicode_analytics.protocol_distribution.items():
        print(f"  {protocol}: {count}")