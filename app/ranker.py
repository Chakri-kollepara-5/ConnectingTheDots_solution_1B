import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from .embedder import EmbeddingGenerator

class DocumentRanker:
    """Ranks document sections based on persona and job relevance."""
    
    def __init__(self, embedding_generator: EmbeddingGenerator):
        self.logger = logging.getLogger(__name__)
        self.embedder = embedding_generator
        
    def rank_sections(self, sections: List[Dict[str, Any]], 
                     persona_data: Dict[str, Any], 
                     job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank sections based on relevance to persona and job."""
        
        if not sections:
            return []
        
        self.logger.info("Generating embeddings...")
        
        # Generate embeddings
        persona_embedding = self.embedder.generate_persona_embedding(persona_data)
        job_embedding = self.embedder.generate_job_embedding(job_data)
        section_embeddings = self.embedder.generate_section_embeddings(sections)
        
        self.logger.info("Computing relevance scores...")
        
        # Compute scores and generate explanations
        scored_sections = []
        for i, section in enumerate(sections):
            section_embedding = section_embeddings[i]
            
            # Compute individual similarities
            persona_sim = self.embedder.compute_similarity(section_embedding, persona_embedding)
            job_sim = self.embedder.compute_similarity(section_embedding, job_embedding)
            
            # Compute combined score
            relevance_score = self.embedder.compute_combined_similarity(
                section_embedding, persona_embedding, job_embedding
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                section, persona_data, job_data, persona_sim, job_sim, relevance_score
            )
            
            # Create scored section
            scored_section = {
                'document_name': section['document_name'],
                'page_number': section['page_number'],
                'section_text': section['section_text'][:1000] + '...' if len(section['section_text']) > 1000 else section['section_text'],
                'relevance_score': float(relevance_score),
                'reasoning': reasoning,
                'section_title': section.get('section_title', ''),
                'context_summary': section.get('context_summary', '')
            }
            
            scored_sections.append(scored_section)
        
        # Sort by relevance score (descending)
        scored_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        self.logger.info(f"Ranked {len(scored_sections)} sections")
        
        return scored_sections
    
    def _generate_reasoning(self, section: Dict[str, Any], 
                          persona_data: Dict[str, Any], 
                          job_data: Dict[str, Any],
                          persona_sim: float, 
                          job_sim: float, 
                          combined_score: float) -> str:
        """Generate explanation for why a section received its score."""
        
        reasoning_parts = []
        
        # Overall score assessment
        if combined_score > 0.7:
            reasoning_parts.append("High relevance match.")
        elif combined_score > 0.5:
            reasoning_parts.append("Moderate relevance match.")
        else:
            reasoning_parts.append("Lower relevance match.")
        
        # Persona alignment
        if persona_sim > 0.6:
            reasoning_parts.append("Strong persona alignment")
            # Check for specific persona keyword matches
            persona_keywords = persona_data.get('keywords', [])
            section_text_lower = section['section_text'].lower()
            matched_keywords = [kw for kw in persona_keywords if kw.lower() in section_text_lower]
            if matched_keywords:
                reasoning_parts.append(f"(matches persona keywords: {', '.join(matched_keywords[:3])})")
        elif persona_sim > 0.4:
            reasoning_parts.append("Some persona alignment")
        
        # Job alignment
        if job_sim > 0.6:
            reasoning_parts.append("Strong job relevance")
            # Check for job keyword matches
            job_keywords = job_data.get('keywords', [])
            section_text_lower = section['section_text'].lower()
            matched_job_keywords = [kw for kw in job_keywords if kw.lower() in section_text_lower]
            if matched_job_keywords:
                reasoning_parts.append(f"(addresses job needs: {', '.join(matched_job_keywords[:3])})")
        elif job_sim > 0.4:
            reasoning_parts.append("Some job relevance")
        
        # Content type assessment
        section_text = section['section_text']
        if len(section_text) > 500:
            reasoning_parts.append("Detailed content")
        elif len(section_text) < 100:
            reasoning_parts.append("Brief content")
        
        # Check for specific content indicators
        if any(word in section_text.lower() for word in ['example', 'case study', 'implementation']):
            reasoning_parts.append("Contains practical examples")
        
        if any(word in section_text.lower() for word in ['process', 'step', 'procedure', 'method']):
            reasoning_parts.append("Contains process information")
        
        if any(word in section_text.lower() for word in ['analysis', 'data', 'research', 'study']):
            reasoning_parts.append("Contains analytical content")
        
        return ". ".join(reasoning_parts) + "."