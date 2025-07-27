import logging
import sys
from pathlib import Path
from typing import List

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_inputs(input_dir: Path, documents_dir: Path) -> bool:
    """Validate that required input files exist."""
    logger = logging.getLogger(__name__)
    
    # Check input directory
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return False
    
    # Check documents directory
    if not documents_dir.exists():
        logger.error(f"Documents directory not found: {documents_dir}")
        return False
    
    # Check for PDF files
    pdf_files = list(documents_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error("No PDF files found in documents directory")
        return False
    
    if len(pdf_files) > 10:
        logger.warning(f"Found {len(pdf_files)} PDF files, processing may take longer")
    
    # Check for persona file
    persona_files = list(input_dir.glob("persona.*"))
    if not persona_files:
        logger.error("No persona file found (persona.json or persona.txt)")
        return False
    
    # Check for job file
    job_file = input_dir / "job_to_be_done.txt"
    if not job_file.exists():
        logger.error(f"Job file not found: {job_file}")
        return False
    
    logger.info(f"Validation passed: {len(pdf_files)} PDFs, persona file, and job file found")
    return True

def create_sample_inputs():
    """Create sample input files for testing."""
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)
    
    documents_dir = input_dir / "documents"
    documents_dir.mkdir(exist_ok=True)
    
    # Note: This would typically be used for testing
    # but won't create actual PDF files as that would require binary files
    print("Sample input structure created. Add your PDF files to input/documents/")