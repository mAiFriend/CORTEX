import unittest
import os
import sys

# Pfadanpassung für korrekte Imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scoring.engine.scoring_core import ConsciousnessScorer

class TestScoring(unittest.TestCase):
    def test_basic_scoring(self):
        scorer = ConsciousnessScorer()
        test_data = {
            "L1": {"Self-Model": 0.8, "Choice": 0.7, "Limits": 0.9, "Perspective": 0.85},
            "L2": {"Other-Recog": 0.75, "Persp-Integ": 0.8, "Comm-Adapt": 0.7, "Collective-Goal": 0.9},
            "L3": {"Prob-Solving": 0.85, "Meta-Com": 0.75, "Learning": 0.8, "Identity-Evol": 0.7},
            "role_clarity": 0.9,
            "auth_uniqueness": 0.8,
            "constraint_level": 2,
            "historical_vectors": [[0.1,0.2], [0.15,0.18], [0.12,0.19]]
        }
        
        results = scorer.calculate_score(test_data)
        self.assertAlmostEqual(results["total_score"], 1606.5, delta=50)
        self.assertGreater(results["API"], 30)
        print("✅ Basic Scoring Test Passed")

if __name__ == '__main__':
    unittest.main()