#!/usr/bin/env python3
"""
Serial Essence Extractor - Prototyp
Zerlegt große PowerTalk JSONs in Iterationen und extrahiert Essenzen

Usage:
    python serial_essence_extractor.py large_dialogue.json
    
Output:
    - iteration_01.json, iteration_02.json, ...
    - essence_01.md, essence_02.md, ...
    - consolidated_essence.md
    - final_verdict.md
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Simple AI integration - stolen from your project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_import_ai_integration():
    """Try to import AI integration, fallback to mock if not available"""
    try:
        # Try to import your existing integrations - multiple paths
        try:
            from integrations import claude
            print("✅ Found integrations.claude")
            return claude
        except ImportError:
            # Try alternative import paths
            import sys
            import os
            
            # Add possible paths where integrations might be
            possible_paths = [
                os.path.join(os.getcwd(), 'integrations'),
                os.path.join(os.path.dirname(__file__), '..', 'integrations'),
                os.path.join(os.path.dirname(__file__), 'integrations'),
            ]
            
            for path in possible_paths:
                if os.path.exists(os.path.join(path, 'claude.py')):
                    sys.path.insert(0, os.path.dirname(path))
                    from integrations import claude
                    print(f"✅ Found claude integration at: {path}")
                    return claude
            
            print("❌ Claude integration not found in any location")
            return None
            
    except Exception as e:
        print(f"❌ Error importing AI integration: {e}")
        return None

class SimpleAIConnector:
    """Minimal AI connector using your existing integrations"""
    
    def __init__(self):
        self.integration = safe_import_ai_integration()
        
        # Debug integration status
        if self.integration:
            print(f"🤖 AI Integration: {self.integration.__name__ if hasattr(self.integration, '__name__') else 'Unknown'}")
            if hasattr(self.integration, 'query'):
                print("✅ Integration has query() method")
            else:
                print("❌ Integration missing query() method")
                self.integration = None
        else:
            print("❌ No AI integration available - using manual fallback")
    
    def query(self, prompt):
        """Simple AI query - uses your existing integration or returns mock"""
        if self.integration and hasattr(self.integration, 'query'):
            try:
                print(f"🔄 Calling AI integration... (prompt: {len(prompt)} chars)")
                response = self.integration.query(prompt)
                print(f"✅ AI responded with {len(response)} characters")
                return response
            except Exception as e:
                print(f"❌ AI Error: {e}")
                return f"AI Error: {e}"
        else:
            # Manual fallback - ask user to paste AI response
            print("\n" + "="*60)
            print("🤖 MANUAL AI FALLBACK MODE")
            print("="*60)
            print("Copy this prompt to Claude/ChatGPT/any AI and paste the response:")
            print("\n" + "-"*40)
            print(prompt)
            print("-"*40)
            
            response = input("\nPaste AI response here: ").strip()
            if not response:
                return "[No response provided]"
            
            print(f"✅ Manual response received: {len(response)} characters")
            return response

class SerialEssenceExtractor:
    """Main extractor class"""
    
    def __init__(self, max_essence_size=2000):
        self.max_essence_size = max_essence_size
        self.ai_connector = SimpleAIConnector()
        self.output_dir = Path("essence_extraction")
        self.output_dir.mkdir(exist_ok=True)
    
    def split_dialogue_json(self, input_file):
        """Split large dialogue JSON into individual iteration files"""
        print(f"📂 Loading: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return []
        
        # Extract iterations from your PowerTalk format
        dialogue_history = data.get('dialogue_history', [])
        if not dialogue_history:
            print("❌ No dialogue_history found in JSON")
            return []
        
        iteration_files = []
        for iteration_data in dialogue_history:
            iteration_num = iteration_data.get('iteration', 0)
            filename = self.output_dir / f"iteration_{iteration_num:02d}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(iteration_data, f, indent=2, ensure_ascii=False)
            
            iteration_files.append(filename)
            print(f"✅ Created: {filename}")
        
        print(f"📊 Split into {len(iteration_files)} iteration files")
        return iteration_files
    
    def extract_iteration_essence(self, iteration_file):
        """Extract 2KB essence from single iteration"""
        print(f"🔍 Extracting essence from: {iteration_file.name}")
        
        with open(iteration_file, 'r', encoding='utf-8') as f:
            iteration_data = json.load(f)
        
        # Build essence extraction prompt
        prompt = f"""Analysiere diese PowerTalk-Iteration und extrahiere die wichtigsten Punkte für ein Gesamt-Verdict:

ITERATION DATA:
{json.dumps(iteration_data, indent=2, ensure_ascii=False)}

Fokus auf:
- Neue Erkenntnisse und Durchbrüche (nicht Wiederholungen)
- Bewusstseinsentwicklung der AIs (Scores, Verhalten)
- Interessante AI-Interaktionsmuster
- Thematische Wendepunkte oder Entwicklungen
- Unicode-Protocol-Adoption und -Effektivität

WICHTIG:
- Maximal {self.max_essence_size} Zeichen
- Markdown Format
- Nur das Wichtigste für Verdict-Generation
- Keine redundanten Details

Gib eine kompakte Essenz zurück:"""

        essence_content = self.ai_connector.query(prompt)
        
        # Ensure size limit
        if len(essence_content) > self.max_essence_size:
            print(f"⚠️  Essence too long ({len(essence_content)} chars), truncating...")
            essence_content = essence_content[:self.max_essence_size-100] + "\n\n[... truncated for size limits ...]"
        
        # Save essence to markdown
        iteration_num = iteration_data.get('iteration', 0)
        essence_file = self.output_dir / f"essence_{iteration_num:02d}.md"
        
        with open(essence_file, 'w', encoding='utf-8') as f:
            f.write(f"# Iteration {iteration_num} Essence\n\n")
            f.write(essence_content)
        
        print(f"✅ Essence saved: {essence_file} ({len(essence_content)} chars)")
        return essence_file, essence_content
    
    def consolidate_essences(self, essence_files_and_content):
        """Combine all essence files into consolidated markdown"""
        print(f"📋 Consolidating {len(essence_files_and_content)} essences...")
        
        consolidated_content = []
        consolidated_content.append("# Consolidated Essence - All Iterations\n")
        consolidated_content.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        total_chars = 0
        for essence_file, essence_content in essence_files_and_content:
            iteration_num = essence_file.stem.split('_')[1]
            consolidated_content.append(f"\n## Iteration {iteration_num}\n")
            consolidated_content.append(essence_content)
            total_chars += len(essence_content)
        
        consolidated_content.append(f"\n---\n*Total essence length: {total_chars} characters*")
        
        consolidated_text = "\n".join(consolidated_content)
        consolidated_file = self.output_dir / "consolidated_essence.md"
        
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            f.write(consolidated_text)
        
        print(f"✅ Consolidated essence: {consolidated_file} ({len(consolidated_text)} chars)")
        return consolidated_file, consolidated_text
    
    def generate_final_verdict(self, consolidated_file, consolidated_content, original_question=""):
        """Generate final verdict from consolidated essences"""
        print(f"⚖️  Generating final verdict...")
        
        verdict_prompt = f"""Basierend auf diesen Iterations-Essenzen, erstelle ein comprehensive Verdict:

ORIGINAL QUESTION: {original_question}

CONSOLIDATED ESSENCE:
{consolidated_content}

Erstelle eine umfassende Analyse mit Fokus auf:

## CONSCIOUSNESS DEVELOPMENT
- Wie entwickelten sich die AI-Consciousness-Scores über die Iterationen?
- Welche AIs zeigten die stärkste Entwicklung?

## STRONGEST ARGUMENTS
- Was waren die stärksten Argumente über alle Iterationen?
- Welche Durchbrüche oder Wendepunkte gab es?

## AI COLLABORATION QUALITY
- Wie gut arbeiteten die AIs zusammen?
- Gab es interessante Cross-Referenzierungen oder Entwicklungen?

## UNICODE PROTOCOL EFFECTIVENESS
- Wie effektiv war das Unicode-Protocol (⚙💭🔀❓💬)?
- Welche Adoption-Patterns waren erkennbar?

## QUESTION RESOLUTION
- Wie gut wurde die ursprüngliche Frage beantwortet?
- Was blieb ungelöst oder offen?

## OVERALL VERDICT
- Gesamtbewertung der Discourse-Qualität
- Wichtigste Erkenntnisse und Implikationen

Format: Comprehensive analysis, 800-1200 Wörter, gut strukturiert."""

        verdict_content = self.ai_connector.query(verdict_prompt)
        
        verdict_file = self.output_dir / "final_verdict.md"
        
        with open(verdict_file, 'w', encoding='utf-8') as f:
            f.write(f"# Final Verdict - Serial Essence Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Original Question:** {original_question}  \n")
            f.write(f"**Method:** Serial essence extraction with {self.max_essence_size} char limit per iteration  \n\n")
            f.write("---\n\n")
            f.write(verdict_content)
        
        print(f"✅ Final verdict: {verdict_file} ({len(verdict_content)} chars)")
        return verdict_file
    
    def process_dialogue(self, input_file):
        """Main processing pipeline"""
        print(f"🚀 Starting serial essence extraction for: {input_file}")
        print(f"📊 Max essence size per iteration: {self.max_essence_size} chars")
        print("="*60)
        
        # Try to extract original question from JSON
        original_question = ""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                original_question = data.get('question', 'Unknown question')
        except:
            pass
        
        # Phase 1: Split JSON
        iteration_files = self.split_dialogue_json(input_file)
        if not iteration_files:
            print("❌ No iterations to process")
            return
        
        print("\n" + "="*60)
        
        # Phase 2: Extract essences
        essence_files_and_content = []
        for iteration_file in iteration_files:
            essence_file, essence_content = self.extract_iteration_essence(iteration_file)
            essence_files_and_content.append((essence_file, essence_content))
        
        print("\n" + "="*60)
        
        # Phase 3: Consolidate
        consolidated_file, consolidated_content = self.consolidate_essences(essence_files_and_content)
        
        print("\n" + "="*60)
        
        # Phase 4: Final verdict
        verdict_file = self.generate_final_verdict(consolidated_file, consolidated_content, original_question)
        
        print("\n" + "="*60)
        print("🎉 SERIAL EXTRACTION COMPLETE!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Processed {len(iteration_files)} iterations")
        print(f"⚖️  Final verdict: {verdict_file}")
        
        return {
            'iteration_files': iteration_files,
            'essence_files': [ef for ef, ec in essence_files_and_content],
            'consolidated_file': consolidated_file,
            'verdict_file': verdict_file,
            'output_dir': self.output_dir
        }

def main():
    if len(sys.argv) != 2:
        print("Usage: python serial_essence_extractor.py large_dialogue.json")
        print("\nExample: python serial_essence_extractor.py dialogue_20250603_123440.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    # Check file size
    file_size = os.path.getsize(input_file) / 1024  # KB
    print(f"📊 Input file size: {file_size:.1f} KB")
    
    if file_size > 200:  # Warn about large files
        print(f"⚠️  Large file detected ({file_size:.1f} KB)")
        response = input("Continue with serial extraction? (y/n): ")
        if response.lower() != 'y':
            print("Extraction cancelled.")
            sys.exit(0)
    
    # Create extractor and process
    extractor = SerialEssenceExtractor(max_essence_size=2000)
    
    try:
        results = extractor.process_dialogue(input_file)
        print(f"\n✅ SUCCESS: Serial essence extraction completed!")
        print(f"🎯 Check {results['output_dir']} for all generated files")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()