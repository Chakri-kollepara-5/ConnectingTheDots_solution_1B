import os
import json
import time
import logging
from pathlib import Path
from app.extractor import PDFExtractor
from app.persona_parser import PersonaParser
from app.job_parser import JobParser
from app.embedder import EmbeddingGenerator
from app.ranker import DocumentRanker
from app.utils import setup_logging, validate_inputs

def main():
    """Main entry point for the persona-driven document intelligence system."""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    start_time = time.time()
    logger.info("Starting Persona-Driven Document Intelligence System")
    
    try:
        # Define paths
        input_dir = Path("input")
        output_dir = Path("output")
        documents_dir = input_dir / "documents"
        
        # Validate inputs
        if not validate_inputs(input_dir, documents_dir):
            logger.error("Input validation failed")
            return
        
        # Initialize components
        logger.info("Initializing system components...")
        pdf_extractor = PDFExtractor()
        persona_parser = PersonaParser()
        job_parser = JobParser()
        embedding_generator = EmbeddingGenerator()
        ranker = DocumentRanker(embedding_generator)
        
        # Parse persona
        logger.info("Parsing persona...")
        persona_file = None
        for ext in ['.json', '.txt']:
            persona_path = input_dir / f"persona{ext}"
            if persona_path.exists():
                persona_file = persona_path
                break
        
        if not persona_file:
            logger.error("No persona file found")
            return
            
        persona_data = persona_parser.parse(persona_file)
        
        # Parse job to be done
        logger.info("Parsing job to be done...")
        job_file = input_dir / "job_to_be_done.txt"
        job_data = job_parser.parse(job_file)
        
        # Extract content from PDFs
        logger.info("Extracting content from PDFs...")
        all_sections = []
        pdf_files = list(documents_dir.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}...")
            try:
                sections = pdf_extractor.extract_sections(pdf_file)
                all_sections.extend(sections)
            except Exception as e:
                logger.warning(f"Failed to process {pdf_file.name}: {e}")
                continue
        
        if not all_sections:
            logger.error("No sections extracted from PDFs")
            return
        
        logger.info(f"Extracted {len(all_sections)} sections from {len(pdf_files)} PDFs")
        
        # Rank sections
        logger.info("Ranking sections based on persona and job relevance...")
        ranked_sections = ranker.rank_sections(all_sections, persona_data, job_data)
        
        # Generate output
        logger.info("Generating output...")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "result.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ranked_sections, f, indent=2, ensure_ascii=False)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        logger.info(f"Generated {len(ranked_sections)} ranked sections")
        logger.info(f"Results saved to {output_file}")
        
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()