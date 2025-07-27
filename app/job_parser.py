import logging
import re
from typing import Dict, Any, List
from pathlib import Path

class JobParser:
    """Parses job-to-be-done descriptions and extracts intents and goals."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def parse(self, job_file: Path) -> Dict[str, Any]:
        """Parse job-to-be-done file and extract structured information."""
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            parsed = {
                'raw_content': content,
                'main_goal': '',
                'specific_tasks': [],
                'success_criteria': [],
                'context': '',
                'urgency': 'medium',
                'keywords': []
            }
            
            # Extract main goal (usually the first sentence or paragraph)
            sentences = content.split('.')
            if sentences:
                parsed['main_goal'] = sentences[0].strip() + '.'
            
            # Look for specific patterns
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section indicators
                if re.search(r'(task|action|step|need to|want to|should)', line, re.IGNORECASE):
                    if line.startswith('-') or line.startswith('•'):
                        parsed['specific_tasks'].append(line[1:].strip())
                    else:
                        parsed['specific_tasks'].append(line)
                
                elif re.search(r'(success|goal|outcome|result|expect)', line, re.IGNORECASE):
                    if line.startswith('-') or line.startswith('•'):
                        parsed['success_criteria'].append(line[1:].strip())
                    else:
                        parsed['success_criteria'].append(line)
                
                elif re.search(r'(urgent|asap|immediately|quickly)', line, re.IGNORECASE):
                    parsed['urgency'] = 'high'
                elif re.search(r'(whenever|sometime|eventually)', line, re.IGNORECASE):
                    parsed['urgency'] = 'low'
            
            # Extract context (look for background information)
            context_indicators = ['because', 'since', 'given that', 'context', 'background']
            for line in lines:
                for indicator in context_indicators:
                    if indicator in line.lower():
                        parsed['context'] += ' ' + line
            
            parsed['context'] = parsed['context'].strip()
            
            # Extract keywords
            parsed['keywords'] = self._extract_job_keywords(content)
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"Error parsing job file {job_file}: {e}")
            raise
    
    def _extract_job_keywords(self, text: str) -> List[str]:
        """Extract action-oriented keywords from job description."""
        # Look for action verbs and important nouns
        action_verbs = re.findall(r'\b(find|search|analyze|review|understand|learn|identify|create|build|develop|improve|optimize|solve|fix|handle|manage|organize|plan|design|implement|test|evaluate|compare|assess|study|research|document|report|present|communicate|coordinate|collaborate)\b', text.lower())
        
        # Extract important nouns (3+ characters, not common words)
        nouns = re.findall(r'\b[A-Z][a-z]{2,}\b', text)  # Proper nouns
        tech_terms = re.findall(r'\b[a-z]{3,}(?:ing|tion|ment|ness|ity|ance|ence)\b', text.lower())  # Technical terms
        
        # Combine and deduplicate
        keywords = list(set(action_verbs + [n.lower() for n in nouns] + tech_terms))
        
        # Filter out very common words
        common_words = {'the', 'and', 'for', 'with', 'this', 'that', 'they', 'have', 'will', 'from', 'been', 'some', 'what', 'were', 'said', 'each', 'which', 'their', 'time', 'than', 'first', 'water', 'long', 'very', 'after', 'work', 'right', 'move', 'thing', 'place', 'year', 'come', 'back', 'way', 'much', 'where', 'most', 'take', 'good', 'just', 'see', 'him', 'two', 'how', 'its', 'our', 'out', 'day', 'get', 'use', 'man', 'new', 'now', 'way', 'may', 'say'}
        
        keywords = [k for k in keywords if k not in common_words and len(k) > 2]
        
        return keywords