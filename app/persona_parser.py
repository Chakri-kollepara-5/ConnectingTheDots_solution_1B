import json
import logging
import re
from typing import Dict, Any, List
from pathlib import Path

class PersonaParser:
    """Parses persona descriptions from JSON or text files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def parse(self, persona_file: Path) -> Dict[str, Any]:
        """Parse persona file and extract structured information."""
        try:
            if persona_file.suffix == '.json':
                return self._parse_json(persona_file)
            else:
                return self._parse_text(persona_file)
        except Exception as e:
            self.logger.error(f"Error parsing persona file {persona_file}: {e}")
            raise
    
    def _parse_json(self, persona_file: Path) -> Dict[str, Any]:
        """Parse JSON persona file."""
        with open(persona_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Normalize the structure
        parsed = {
            'raw_content': json.dumps(data, indent=2),
            'attributes': {},
            'needs': [],
            'interests': [],
            'tone': '',
            'keywords': []
        }
        
        # Extract common fields
        for key, value in data.items():
            if key.lower() in ['name', 'age', 'role', 'occupation', 'title']:
                parsed['attributes'][key] = value
            elif key.lower() in ['needs', 'requirements', 'goals']:
                if isinstance(value, list):
                    parsed['needs'].extend(value)
                else:
                    parsed['needs'].append(str(value))
            elif key.lower() in ['interests', 'hobbies', 'preferences']:
                if isinstance(value, list):
                    parsed['interests'].extend(value)
                else:
                    parsed['interests'].append(str(value))
            elif key.lower() in ['tone', 'communication_style', 'personality']:
                parsed['tone'] = str(value)
            elif key.lower() in ['keywords', 'tags', 'topics']:
                if isinstance(value, list):
                    parsed['keywords'].extend(value)
                else:
                    parsed['keywords'].append(str(value))
        
        # Extract keywords from all text content
        all_text = json.dumps(data)
        parsed['keywords'].extend(self._extract_keywords(all_text))
        
        return parsed
    
    def _parse_text(self, persona_file: Path) -> Dict[str, Any]:
        """Parse text persona file."""
        with open(persona_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parsed = {
            'raw_content': content,
            'attributes': {},
            'needs': [],
            'interests': [],
            'tone': '',
            'keywords': []
        }
        
        # Extract structured information using patterns
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if re.match(r'^(name|age|role|occupation|title):\s*(.+)', line, re.IGNORECASE):
                match = re.match(r'^(\w+):\s*(.+)', line, re.IGNORECASE)
                parsed['attributes'][match.group(1).lower()] = match.group(2)
            elif re.match(r'^(needs|requirements|goals):', line, re.IGNORECASE):
                current_section = 'needs'
            elif re.match(r'^(interests|hobbies|preferences):', line, re.IGNORECASE):
                current_section = 'interests'
            elif re.match(r'^(tone|communication|personality):', line, re.IGNORECASE):
                current_section = 'tone'
            elif line.startswith('-') or line.startswith('•'):
                # Bullet point
                item = line[1:].strip()
                if current_section == 'needs':
                    parsed['needs'].append(item)
                elif current_section == 'interests':
                    parsed['interests'].append(item)
            elif current_section == 'tone' and not line.endswith(':'):
                parsed['tone'] += ' ' + line
        
        # Clean tone
        parsed['tone'] = parsed['tone'].strip()
        
        # Extract keywords from all content
        parsed['keywords'] = self._extract_keywords(content)
        
        return parsed
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 
            'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'shall', 'from', 'into', 'onto'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return unique keywords
        return list(set(keywords))