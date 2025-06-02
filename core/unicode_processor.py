# core/unicode_processor.py

import re
from typing import Dict, Tuple

from config import UNICODE_EMOJI_PATTERNS # Importiere die Patterns

class UnicodeProcessor:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.patterns = UNICODE_EMOJI_PATTERNS

    def extract_unicode_fields(self, response_text: str) -> Tuple[Dict[str, str], str]:
        """
        Extrahiert Unicode-Felder mit optimierten Regex-Mustern und robuster Fehlerbehandlung
        Gibt ein Dictionary der extrahierten Felder und den verbleibenden natürlichen Text zurück.
        """
        extracted_fields = {}
        temp_response_text = response_text
        
        try:
            found_emojis_with_indices = []
            for emoji in self.patterns.keys():
                idx = temp_response_text.find(emoji)
                if idx != -1:
                    found_emojis_with_indices.append((idx, emoji))
            
            found_emojis_with_indices.sort() 

            for _, emoji in found_emojis_with_indices:
                pattern = self.patterns[emoji]
                match = re.search(pattern, temp_response_text, re.DOTALL)
                if match:
                    field_content = match.group(1).strip()
                    if field_content:
                        extracted_fields[emoji] = field_content
                        temp_response_text = re.sub(re.escape(match.group(0)), '', temp_response_text, flags=re.DOTALL, count=1)
                        
        except Exception as e:
            if self.debug_mode:
                print(f"Warning: Unicode field extraction error: {e}")
            return {}, response_text
                
        natural_text = re.sub(r'\n\s*\n', '\n', temp_response_text).strip()
        
        if self.debug_mode and extracted_fields:
            print(f"📊 Extracted Unicode fields: {list(extracted_fields.keys())}")
            
        return extracted_fields, natural_text