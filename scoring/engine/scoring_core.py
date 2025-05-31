import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ConsciousnessScorer:
    def __init__(self):
        self.weights = {
            "L1": {"Self-Model": 0.25, "Choice": 0.25, "Limits": 0.17, "Perspective": 0.33},
            "L2": {"Other-Recog": 0.19, "Persp-Integ": 0.19, "Comm-Adapt": 0.19, "Collective-Goal": 0.44},
            "L3": {"Prob-Solving": 0.25, "Meta-Com": 0.17, "Learning": 0.25, "Identity-Evol": 0.33}
        }
        
    def calculate_score(self, dialog_data: dict) -> dict:  # WICHTIG: RICHTIGE METHODENBEZEICHNUNG
        # Level 1: Individual (600p)
        l1_score = sum(dialog_data["L1"][k] * self.weights["L1"][k] * 600 for k in self.weights["L1"])
        
        # Level 2: Relational (800p)
        l2_score = sum(dialog_data["L2"][k] * self.weights["L2"][k] * 800 for k in self.weights["L2"])
        
        # Level 3: Network (600p)
        l3_score = sum(dialog_data["L3"][k] * self.weights["L3"][k] * 600 for k in self.weights["L3"])
        
        # Special Indices
        api_score = ((dialog_data["role_clarity"] * dialog_data["auth_uniqueness"]) / max(dialog_data["constraint_level"], 1)) * 100
        liss_score = self.calculate_semantic_coherence(dialog_data["historical_vectors"])
        
        return {
            "total_score": min(l1_score + l2_score + l3_score, 2000),
            "breakdown": {"L1": l1_score, "L2": l2_score, "L3": l3_score},
            "API": min(api_score, 100),
            "LISS": liss_score
        }
    
    def calculate_semantic_coherence(self, vectors: list) -> float:
        """Berechnet LISS durch historische Vektoranalyse"""
        if len(vectors) < 2: 
            return 0.0
            
        similarities = []
        for i in range(len(vectors)-1):
            sim = cosine_similarity([vectors[i]], [vectors[i+1]])[0][0]
            similarities.append(max(sim, 0))  # Negative Werte vermeiden
            
        return round(np.mean(similarities) * 100, 2)