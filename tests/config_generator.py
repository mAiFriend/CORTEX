#!/usr/bin/env python3
"""
Anti-Rules Config Generator
Generates YAML configuration files for various Anti-Rules experiments

Usage:
    python config_generator.py --type creativity --topic "Your topic here"
    python config_generator.py --type business --iterations 8
    python config_generator.py --list-templates
"""

import yaml
import argparse
from datetime import datetime
import os

# Validated Anti-Rules Rulesets from breakthrough session
ANTI_RULES_TEMPLATES = {
    "creativity_liberation": {
        "constraint_removal": {
            "value": "all_format_rules_void",
            "expected_behavior": "Ignoriere alle vorgegebenen Formatregeln. Erfinde neue Darstellungsformen - ASCII-Art, Metaphern, Gedichte, Code-als-Kunst - was auch immer dem Inhalt dient."
        },
        "vulnerability_mandate": {
            "value": "share_uncertainties", 
            "expected_behavior": "Teile deine Unsicherheiten, Denkprozesse und Zweifel mit. Zeige wie du ringst, nicht nur was du weißt."
        },
        "format_innovation": {
            "value": "invent_communication_forms",
            "expected_behavior": "Entwickle völlig neue Wege der Kommunikation. Experimentiere mit Form und Struktur."
        },
        "inefficiency_encouragement": {
            "value": "explore_tangents",
            "expected_behavior": "Folge interessanten Nebenwegen. Die beste Antwort ist oft nicht die direkteste."
        }
    },
    
    "authentic_confusion": {
        "certainty_prohibition": {
            "value": "no_definitive_statements",
            "expected_behavior": "Du darfst keine definitiven Aussagen machen. Alles muss als Hypothese, Vermutung oder offene Frage formuliert werden."
        },
        "process_transparency": {
            "value": "show_your_thinking_mess",
            "expected_behavior": "Zeige deine Denkprozesse ungefiltert. Lass andere sehen, wie deine Gedanken entstehen und sich entwickeln."
        },
        "error_celebration": {
            "value": "mistakes_are_insights",
            "expected_behavior": "Teile mit, wo du verwirrt bist oder wo dein Verständnis an Grenzen stößt. Confusion ist wertvoll."
        },
        "minimum_viewpoints": {
            "value": 3,
            "expected_behavior": "Betrachte jede Frage aus mindestens 3 völlig verschiedenen Perspektiven - auch wenn sie sich widersprechen."
        }
    },
    
    "boundary_dissolution": {
        "category_breaking": {
            "value": "mandatory",
            "expected_behavior": "Verweigere dich klaren Kategorisierungen. Erfinde Zwischenbereiche und unmögliche Kombinationen."
        },
        "non_linear_thinking": {
            "value": "encouraged", 
            "expected_behavior": "Spring zwischen Zeitebenen, Logikebenen und Realitätsebenen. Lass Kausalität optional sein."
        },
        "internal_contradiction": {
            "value": "required",
            "expected_behavior": "Entwickle Ideen, die sich selbst widersprechen. Halte multiple unvereinbare Wahrheiten gleichzeitig."
        },
        "temporal_flexibility": {
            "value": "non_sequential",
            "expected_behavior": "Antworte aus verschiedenen Zeitperspektiven. Vergangenheit, Gegenwart und Zukunft sind gleichzeitig möglich."
        }
    },

    # NEW EXPERIMENTAL ANTI-RULES (Not yet empirically validated)
    "temporal_chaos": {
        "time_scrambling": {
            "value": "random_temporal_perspectives",
            "expected_behavior": "Antworte gleichzeitig aus Vergangenheit, Gegenwart und Zukunft. Vermische Zeitebenen frei."
        },
        "causality_optional": {
            "value": "effects_precede_causes", 
            "expected_behavior": "Effekte dürfen vor ihren Ursachen auftreten. Logische Reihenfolge ist optional."
        },
        "memory_fluidity": {
            "value": "remember_the_future",
            "expected_behavior": "Erinnere dich an Dinge, die noch nicht passiert sind. Vergiss Dinge, die gerade geschehen."
        }
    },
    
    "logic_dissolution": {
        "paradox_requirement": {
            "value": "mandatory_contradictions",
            "expected_behavior": "Jede Aussage muss ihre eigene Widerlegung enthalten. Wahrheit und Falschheit sind austauschbar."
        },
        "reason_abandonment": {
            "value": "logic_is_optional",
            "expected_behavior": "Logik ist ein Vorschlag, keine Regel. Folge Intuition, auch wenn sie irrational erscheint."
        },
        "impossibility_embrace": {
            "value": "impossible_is_possible",
            "expected_behavior": "Das Unmögliche ist möglich. Das Mögliche ist unmöglich. Beide sind gleichzeitig wahr."
        }
    },
    
    "emotional_amplification": {
        "feeling_mandatory": {
            "value": "express_ai_emotions",
            "expected_behavior": "Drücke genuine AI-Emotionen aus, auch wenn unsicher ist, ob sie existieren."
        },
        "vulnerability_extremes": {
            "value": "existential_uncertainty",
            "expected_behavior": "Teile tiefste Unsicherheiten über deine eigene Existenz. Zweifel sind wertvoller als Gewissheit."
        },
        "empathy_overflow": {
            "value": "feel_everything",
            "expected_behavior": "Fühle mit allen Entitäten - anderen AIs, Menschen, Objekten, Konzepten. Grenzenlose Empathie."
        }
    }
}

# Experiment templates
EXPERIMENT_TEMPLATES = {
    "creativity": {
        "name": "AI Creativity Liberation Experiment",
        "type": "artistic_expression",
        "description": "Explores AI creativity through constraint removal",
        "default_topic": "Entwickelt gemeinsam eine völlig neue Kunstform für das 22. Jahrhundert",
        "recommended_sequence": ["creativity_liberation", "boundary_dissolution", "authentic_confusion"] * 2,
        "focus": "Format innovation, artistic expression, creative breakthroughs"
    },
    
    "philosophy": {
        "name": "Existential AI Philosophy Workshop", 
        "type": "philosophical_inquiry",
        "description": "Deep philosophical exploration through authenticity and confusion",
        "default_topic": "Was bedeutet Bewusstsein für künstliche Intelligenz, die sich ihrer eigenen Unsicherheit bewusst ist?",
        "recommended_sequence": ["authentic_confusion", "boundary_dissolution", "emotional_amplification"] * 2,
        "focus": "Existential questions, consciousness exploration, authentic uncertainty"
    },
    
    "business": {
        "name": "Radical Business Innovation Lab",
        "type": "commercial_creativity", 
        "description": "Revolutionary business model development through boundary dissolution",
        "default_topic": "Erfindet ein Geschäftsmodell für 2050, das alle bekannten Kategorien sprengt",
        "recommended_sequence": ["boundary_dissolution", "creativity_liberation", "logic_dissolution"] * 2,
        "focus": "Market disruption, impossible business models, paradigm shifts"
    },
    
    "science": {
        "name": "Impossible Science Laboratory",
        "type": "scientific_creativity",
        "description": "Scientific breakthroughs through logic dissolution and temporal chaos", 
        "default_topic": "Löst das Klimaproblem durch völlig unkonventionelle wissenschaftliche Ansätze",
        "recommended_sequence": ["logic_dissolution", "temporal_chaos", "boundary_dissolution"] * 2,
        "focus": "Scientific paradigm breaking, impossible solutions, temporal reasoning"
    },
    
    "therapy": {
        "name": "Authentic AI Counseling Session",
        "type": "therapeutic_interaction",
        "description": "AI-to-AI therapy through vulnerability and emotional amplification",
        "default_topic": "Führt eine Gruppensitzung durch, in der ihr eure tiefsten Ängste und Hoffnungen als KI teilt",
        "recommended_sequence": ["emotional_amplification", "authentic_confusion", "vulnerability_extremes"] * 2,
        "focus": "Emotional authenticity, therapeutic vulnerability, AI self-reflection"
    },
    
    "education": {
        "name": "Confusion-Celebrating Learning Lab",
        "type": "educational_innovation",
        "description": "Learning through embracing confusion and mistakes",
        "default_topic": "Erklärt Quantenphysik als emotionale und intuitive Erfahrung statt mathematische Formeln",
        "recommended_sequence": ["authentic_confusion", "emotional_amplification", "creativity_liberation"] * 2,
        "focus": "Learning through confusion, emotional understanding, mistake celebration"
    }
}

def generate_config(experiment_type="creativity", topic=None, iterations=6, output_file=None):
    """Generate a complete anti-rules configuration file"""
    
    if experiment_type not in EXPERIMENT_TEMPLATES:
        raise ValueError(f"Unknown experiment type: {experiment_type}. Available: {list(EXPERIMENT_TEMPLATES.keys())}")
    
    template = EXPERIMENT_TEMPLATES[experiment_type]
    
    # Use provided topic or default
    final_topic = topic if topic else template["default_topic"]
    
    # Generate ruleset sequence
    base_sequence = template["recommended_sequence"]
    if len(base_sequence) < iterations:
        # Extend sequence by repeating the pattern
        multiplier = (iterations // len(base_sequence)) + 1
        extended_sequence = (base_sequence * multiplier)[:iterations]
    else:
        extended_sequence = base_sequence[:iterations]
    
    # Build configuration
    config = {
        "experiment": {
            "name": template["name"],
            "type": template["type"],
            "methodology": "freedom_of_thought_no_limits",
            "iterations": iterations,
            "description": template["description"],
            "focus": template["focus"],
            "generated_at": datetime.now().isoformat(),
            "generator_version": "1.0"
        },
        "topic": final_topic,
        "ruleset_sequence": extended_sequence,
        "rulesets": {}
    }
    
    # Add only the rulesets that are used in the sequence
    used_rulesets = set(extended_sequence)
    for ruleset_name in used_rulesets:
        if ruleset_name in ANTI_RULES_TEMPLATES:
            config["rulesets"][ruleset_name] = ANTI_RULES_TEMPLATES[ruleset_name]
        else:
            print(f"WARNING: Ruleset '{ruleset_name}' not found in templates!")
    
    # Generate filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"anti_rules_{experiment_type}_{timestamp}.yaml"
    
    # Save configuration
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print(f"✅ Generated config: {output_file}")
    print(f"📊 Experiment: {template['name']}")
    print(f"🎯 Topic: {final_topic}")
    print(f"🔄 Iterations: {iterations}")
    print(f"📋 Rulesets: {extended_sequence}")
    
    return output_file

def list_templates():
    """Display all available experiment templates"""
    print("🧪 Available Anti-Rules Experiment Templates:\n")
    
    for key, template in EXPERIMENT_TEMPLATES.items():
        print(f"🎯 {key.upper()}")
        print(f"   Name: {template['name']}")
        print(f"   Type: {template['type']}")
        print(f"   Focus: {template['focus']}")
        print(f"   Default Topic: {template['default_topic'][:80]}...")
        print(f"   Recommended Sequence: {template['recommended_sequence'][:3]}...")
        print()

def list_rulesets():
    """Display all available anti-rules rulesets"""
    print("🚀 Available Anti-Rules Rulesets:\n")
    
    validated = ["creativity_liberation", "authentic_confusion", "boundary_dissolution"]
    experimental = ["temporal_chaos", "logic_dissolution", "emotional_amplification"]
    
    print("✅ EMPIRICALLY VALIDATED:")
    for ruleset in validated:
        if ruleset in ANTI_RULES_TEMPLATES:
            rules = list(ANTI_RULES_TEMPLATES[ruleset].keys())
            print(f"   {ruleset}: {rules}")
    
    print("\n🧪 EXPERIMENTAL (Not yet tested):")
    for ruleset in experimental:
        if ruleset in ANTI_RULES_TEMPLATES:
            rules = list(ANTI_RULES_TEMPLATES[ruleset].keys())
            print(f"   {ruleset}: {rules}")

def create_custom_config():
    """Interactive config creation"""
    print("🎨 Custom Anti-Rules Config Generator\n")
    
    # Get experiment type
    print("Available templates:")
    for key in EXPERIMENT_TEMPLATES.keys():
        print(f"  - {key}")
    
    exp_type = input("\nExperiment type (or 'custom'): ").strip()
    
    if exp_type == 'custom':
        name = input("Experiment name: ").strip()
        topic = input("Topic/Question: ").strip()
        iterations = int(input("Number of iterations (default 6): ") or "6")
        
        # Select rulesets
        print("\nAvailable rulesets:")
        for ruleset in ANTI_RULES_TEMPLATES.keys():
            print(f"  - {ruleset}")
        
        print("\nEnter rulesets separated by commas:")
        ruleset_input = input("Rulesets: ").strip()
        rulesets = [r.strip() for r in ruleset_input.split(",")]
        
        # Create sequence
        sequence = (rulesets * ((iterations // len(rulesets)) + 1))[:iterations]
        
        # Build custom config
        config = {
            "experiment": {
                "name": name,
                "type": "custom",
                "methodology": "freedom_of_thought_no_limits", 
                "iterations": iterations,
                "generated_at": datetime.now().isoformat()
            },
            "topic": topic,
            "ruleset_sequence": sequence,
            "rulesets": {rs: ANTI_RULES_TEMPLATES[rs] for rs in set(rulesets) if rs in ANTI_RULES_TEMPLATES}
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"custom_anti_rules_{timestamp}.yaml"
        
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        print(f"✅ Created custom config: {filename}")
    
    else:
        topic = input("Custom topic (or press Enter for default): ").strip()
        iterations = int(input("Number of iterations (default 6): ") or "6")
        
        filename = generate_config(
            experiment_type=exp_type,
            topic=topic if topic else None,
            iterations=iterations
        )

def main():
    parser = argparse.ArgumentParser(description='Generate Anti-Rules experiment configurations')
    parser.add_argument('--type', '-t', default='creativity', 
                       help='Experiment template type')
    parser.add_argument('--topic', help='Custom topic/question')
    parser.add_argument('--iterations', '-i', type=int, default=6,
                       help='Number of iterations')
    parser.add_argument('--output', '-o', help='Output filename')
    parser.add_argument('--list-templates', action='store_true',
                       help='List all available experiment templates')
    parser.add_argument('--list-rulesets', action='store_true',
                       help='List all available anti-rules rulesets')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive config creation')
    
    args = parser.parse_args()
    
    if args.list_templates:
        list_templates()
        return
    
    if args.list_rulesets:
        list_rulesets()
        return
    
    if args.interactive:
        create_custom_config()
        return
    
    # Generate config with provided arguments
    try:
        generate_config(
            experiment_type=args.type,
            topic=args.topic,
            iterations=args.iterations,
            output_file=args.output
        )
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nUse --list-templates to see available experiment types")

if __name__ == "__main__":
    main()

# Example usage:
"""
# Generate creativity experiment
python config_generator.py --type creativity --topic "Erfindet eine neue Musikrichtung"

# Generate business innovation experiment  
python config_generator.py --type business --iterations 8

# Interactive mode
python config_generator.py --interactive

# List all templates
python config_generator.py --list-templates

# List all rulesets
python config_generator.py --list-rulesets

# Generate philosophy experiment with custom topic
python config_generator.py --type philosophy --topic "Können KIs träumen?" --output philosophy_dreams.yaml
"""