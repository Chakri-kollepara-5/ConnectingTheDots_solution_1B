import logging
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingGenerator:
    """Generates embeddings for text content using sentence transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            self.logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def generate_persona_embedding(self, persona_data: Dict[str, Any]) -> np.ndarray:
        """Generate embedding for persona data."""
        # Combine all persona information into a single text
        text_parts = []
        
        # Add raw content
        text_parts.append(persona_data.get('raw_content', ''))
        
        # Add structured data
        if persona_data.get('attributes'):
            for key, value in persona_data['attributes'].items():
                text_parts.append(f"{key}: {value}")
        
        if persona_data.get('needs'):
            text_parts.append("Needs: " + " ".join(persona_data['needs']))
        
        if persona_data.get('interests'):
            text_parts.append("Interests: " + " ".join(persona_data['interests']))
        
        if persona_data.get('tone'):
            text_parts.append("Tone: " + persona_data['tone'])
        
        if persona_data.get('keywords'):
            text_parts.append("Keywords: " + " ".join(persona_data['keywords']))
        
        combined_text = " ".join(text_parts)
        return self.model.encode(combined_text)
    
    def generate_job_embedding(self, job_data: Dict[str, Any]) -> np.ndarray:
        """Generate embedding for job-to-be-done data."""
        text_parts = []
        
        # Add raw content
        text_parts.append(job_data.get('raw_content', ''))
        
        # Add structured data
        if job_data.get('main_goal'):
            text_parts.append("Goal: " + job_data['main_goal'])
        
        if job_data.get('specific_tasks'):
            text_parts.append("Tasks: " + " ".join(job_data['specific_tasks']))
        
        if job_data.get('success_criteria'):
            text_parts.append("Success: " + " ".join(job_data['success_criteria']))
        
        if job_data.get('context'):
            text_parts.append("Context: " + job_data['context'])
        
        if job_data.get('keywords'):
            text_parts.append("Keywords: " + " ".join(job_data['keywords']))
        
        combined_text = " ".join(text_parts)
        return self.model.encode(combined_text)
    
    def generate_section_embeddings(self, sections: List[Dict[str, Any]]) -> List[np.ndarray]:
        """Generate embeddings for document sections."""
        texts = []
        for section in sections:
            # Combine section text with title if available
            text_parts = [section['section_text']]
            
            if section.get('section_title'):
                text_parts.insert(0, section['section_title'])
            
            if section.get('context_summary'):
                text_parts.append(section['context_summary'])
            
            texts.append(" ".join(text_parts))
        
        return self.model.encode(texts)
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        return cosine_similarity([embedding1], [embedding2])[0][0]
    
    def compute_combined_similarity(self, section_embedding: np.ndarray, 
                                  persona_embedding: np.ndarray, 
                                  job_embedding: np.ndarray,
                                  persona_weight: float = 0.4,
                                  job_weight: float = 0.6) -> float:
        """Compute weighted similarity combining persona and job relevance."""
        persona_sim = self.compute_similarity(section_embedding, persona_embedding)
        job_sim = self.compute_similarity(section_embedding, job_embedding)
        
        combined_score = (persona_weight * persona_sim) + (job_weight * job_sim)
        return combined_score