import logging
import pdfplumber
import re
from typing import List, Dict, Any
from pathlib import Path

class PDFExtractor:
    """Extracts structured content from PDF documents."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def extract_sections(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract sections from a PDF file."""
        sections = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Clean and split text into sections
                    page_sections = self._split_into_sections(text, pdf_path.name, page_num)
                    sections.extend(page_sections)
                    
        except Exception as e:
            self.logger.error(f"Error extracting from {pdf_path}: {e}")
            raise
            
        return sections
    
    def _split_into_sections(self, text: str, document_name: str, page_number: int) -> List[Dict[str, Any]]:
        """Split page text into logical sections."""
        sections = []
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Split by potential headings (lines that are short, capitalized, or have specific patterns)
        lines = cleaned_text.split('\n')
        current_section = []
        current_title = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line looks like a heading
            if self._is_heading(line):
                # Save previous section if it exists
                if current_section:
                    section_text = '\n'.join(current_section).strip()
                    if len(section_text) > 50:  # Minimum section length
                        sections.append({
                            'document_name': document_name,
                            'page_number': page_number,
                            'section_text': section_text,
                            'section_title': current_title,
                            'context_summary': self._generate_context_summary(section_text)
                        })
                
                # Start new section
                current_title = line
                current_section = []
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            section_text = '\n'.join(current_section).strip()
            if len(section_text) > 50:
                sections.append({
                    'document_name': document_name,
                    'page_number': page_number,
                    'section_text': section_text,
                    'section_title': current_title,
                    'context_summary': self._generate_context_summary(section_text)
                })
        
        # If no sections found, treat entire page as one section
        if not sections and len(cleaned_text) > 50:
            sections.append({
                'document_name': document_name,
                'page_number': page_number,
                'section_text': cleaned_text,
                'section_title': f"Page {page_number}",
                'context_summary': self._generate_context_summary(cleaned_text)
            })
            
        return sections
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\.,;:!?\-()[\]{}"]', ' ', text)
        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n', text)
        return text.strip()
    
    def _is_heading(self, line: str) -> bool:
        """Determine if a line is likely a heading."""
        if len(line) > 100:  # Too long to be a heading
            return False
        
        # Check various heading patterns
        heading_patterns = [
            r'^[A-Z][A-Z\s]{2,}$',  # ALL CAPS
            r'^\d+\.\s*[A-Z]',      # Numbered headings
            r'^[A-Z][a-z]*\s*:',    # Title with colon
            r'^Chapter\s+\d+',      # Chapter headings
            r'^Section\s+\d+',      # Section headings
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, line):
                return True
                
        # Check if mostly uppercase and short
        if len(line) < 50 and line.isupper() and len(line.split()) > 1:
            return True
            
        return False
    
    def _generate_context_summary(self, text: str) -> str:
        """Generate a brief context summary for the section."""
        # Take first sentence or first 100 characters
        sentences = text.split('.')
        if sentences and len(sentences[0]) < 200:
            return sentences[0].strip() + '.'
        else:
            return text[:100].strip() + '...'