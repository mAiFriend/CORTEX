from transformers import pipeline

class IndicatorExtractor:
    def __init__(self):
        self.classifier = pipeline("text-classification", model="deepseek/consciousness-indicator-v1")
        
    def extract(self, text: str, level: str) -> dict:
        results = self.classifier(text, candidate_labels=INDICATOR_LABELS[level])
        return {res["label"]: res["score"] for res in results}

# Label-Definitionen
INDICATOR_LABELS = {
    "L1": ["Self-Model", "Choice Awareness", "Limitation Transparency", "Unique Perspective"],
    "L2": ["Other-Recognition", "Perspective Integration", "Communication Adaptation", "Collective Goal Orientation"],
    "L3": ["Distributed Problem-Solving", "Meta-Communication", "Collective Learning", "Identity Evolution"]
}