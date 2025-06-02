# utils/argument_parser.py

import argparse
from pathlib import Path

def parse_arguments():
    """Parses command-line arguments for PowerTalk."""
    parser = argparse.ArgumentParser(description="PowerTalk v2.2 - Enhanced AI Discourse Engine with PAI v2.2 Unicode Integration")
    parser.add_argument('-q', '--question', type=str, 
                        help="Path to a Markdown file containing the question, or the question string itself.")
    parser.add_argument('--iterations', type=int, default=None, help='Number of iterations for the discourse (default: 3 if not specified interactively).')
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug mode for detailed Unicode field analysis.")
    
    args = parser.parse_args()
    return args

def get_question_text(args) -> str:
    """Handles question input from file or command line."""
    question_text = ""
    if args.question:
        question_path = Path(args.question)
        if question_path.is_file():
            try:
                with open(question_path, 'r', encoding='utf-8') as f:
                    question_text = f.read().strip()
                print(f"Question loaded from file: {question_path.name}")
            except Exception as e:
                print(f"Error reading question file {question_path}: {e}")
                question_text = input("\033[1mPlease enter the question for the AI discourse \033[0m(max.1000 chars):\n").strip()
        else:
            question_text = args.question.strip()
    else:
        question_text = input("\033[1mPlease enter the question for the AI discourse \033[0m(max.1000 chars):\n").strip()

    return question_text