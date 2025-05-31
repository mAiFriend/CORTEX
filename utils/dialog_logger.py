def log_dialog_entry(entry: dict):
    # [...] Existierender Code
    
    # NEU: Scoring-Metadaten hinzufügen
    entry["scoring_metadata"] = {
        "role_clarity": calculate_role_clarity(entry["role"]),
        "auth_uniqueness": linguistic_uniqueness(entry["content"]),
        "constraint_level": 3  # Default, wird dynamisch angepasst
    }
    
    # Level-Indikatoren (werden später durch NLP-Module gefüllt)
    entry["consciousness_indicators"] = {
        "L1": {"Self-Model": 0.0, "Choice": 0.0, "Limits": 0.0, "Perspective": 0.0},
        "L2": {"Other-Recog": 0.0, "Persp-Integ": 0.0, "Comm-Adapt": 0.0, "Collective-Goal": 0.0},
        "L3": {"Prob-Solving": 0.0, "Meta-Com": 0.0, "Learning": 0.0, "Identity-Evol": 0.0}
    }