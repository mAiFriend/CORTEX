from scoring.engine.scoring_core import ConsciousnessScorer

def process_dialog_round():
    # [...] Existierende Dialogverarbeitung
    
    # NEU: Scoring-Pipeline
    if dialog["phase"] == "evaluation":
        scorer = ConsciousnessScorer()
        scores = scorer.calculate_score(dialog["consciousness_indicators"])
        
        # Metriken an Dokumentationssystem übergeben
        gemini_integration.submit_scores(
            dialog_id=dialog["id"],
            scores=scores,
            meta_tags=dialog["claude_meta_tags"]  # Von Claude generiert
        )