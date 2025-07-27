# Persona-Driven Document Intelligence System

A modular, Dockerized Python backend system that analyzes PDF documents based on persona descriptions and job-to-be-done statements, providing ranked relevance scores with explanations.

## Features

- **PDF Content Extraction**: Intelligent extraction of structured content from PDF documents
- **Persona Analysis**: Parses persona descriptions from JSON or text files
- **Job-to-be-Done Processing**: Extracts goals, tasks, and success criteria from job descriptions
- **Semantic Matching**: Uses sentence transformers for semantic similarity matching
- **Explainable Ranking**: Provides detailed reasoning for relevance scores
- **Dockerized**: Fully containerized for consistent deployment

## Quick Start

### Using Docker (Recommended)

1. **Build the container:**
   ```bash
   docker build -t persona-doc-intel .
   ```

2. **Prepare your input files:**
   - Add 3-10 PDF documents to `input/documents/`
   - Create `input/persona.json` or `input/persona.txt` with persona description
   - Create `input/job_to_be_done.txt` with job description

3. **Run the analysis:**
   ```bash
   docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output persona-doc-intel
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download required models:**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

3. **Run the system:**
   ```bash
   python main.py
   ```

## Input Format

### Directory Structure
```
input/
├── documents/          # 3-10 PDF files
│   ├── document1.pdf
│   ├── document2.pdf
│   └── ...
├── persona.json        # OR persona.txt
└── job_to_be_done.txt
```

### Persona File Format

**JSON Format (persona.json):**
```json
{
  "name": "Dr. Sarah Chen",
  "role": "Senior Data Scientist",
  "needs": ["Technical documentation", "Best practices"],
  "interests": ["Machine learning", "Data analysis"],
  "tone": "Professional, analytical",
  "keywords": ["python", "algorithms", "optimization"]
}
```

**Text Format (persona.txt):**
```
Name: Dr. Sarah Chen
Role: Senior Data Scientist

Needs:
- Technical documentation
- Best practices

Interests:
- Machine learning
- Data analysis

Tone: Professional, analytical, detail-oriented
```

### Job-to-be-Done Format

```
Goal: Implement a machine learning pipeline for fraud detection

Specific Tasks:
- Research fraud detection algorithms
- Learn about real-time model serving
- Study feature engineering approaches

Success Criteria:
- Process 10,000+ transactions per second
- Achieve 95%+ accuracy
- Minimize false positives

Context: Current rule-based system needs ML upgrade
Urgency: High priority - 3 month deadline
```

## Output Format

The system generates `output/result.json` with ranked sections:

```json
[
  {
    "document_name": "ml_fraud_detection.pdf",
    "page_number": 15,
    "section_text": "Real-time fraud detection requires...",
    "relevance_score": 0.89,
    "reasoning": "High relevance match. Strong job relevance (addresses job needs: fraud, detection, real-time). Contains process information.",
    "section_title": "Real-time Processing Architecture",
    "context_summary": "This section discusses architectural patterns..."
  }
]
```

## System Architecture

### Core Components

1. **PDFExtractor** (`app/extractor.py`)
   - Extracts text from PDFs using pdfplumber
   - Segments content by headings and structure
   - Cleans and normalizes text

2. **PersonaParser** (`app/persona_parser.py`)
   - Supports JSON and text persona formats
   - Extracts attributes, needs, interests, and keywords
   - Normalizes persona data for embedding

3. **JobParser** (`app/job_parser.py`)
   - Parses job descriptions for goals and tasks
   - Identifies success criteria and context
   - Extracts action-oriented keywords

4. **EmbeddingGenerator** (`app/embedder.py`)
   - Uses sentence-transformers for semantic embeddings
   - Computes cosine similarity between texts
   - Combines persona and job relevance scores

5. **DocumentRanker** (`app/ranker.py`)
   - Ranks sections by relevance score
   - Generates explanatory reasoning
   - Provides detailed scoring breakdown

### Performance Characteristics

- **Processing Time**: < 60 seconds for 10 PDFs
- **Accuracy**: Semantic matching with explainable results
- **Scalability**: Handles 3-10 PDFs efficiently
- **Stability**: Robust error handling for malformed files

## Configuration

### Model Settings

The system uses `sentence-transformers/all-MiniLM-L6-v2` by default. To use a different model:

```python
embedder = EmbeddingGenerator(model_name='your-preferred-model')
```

### Scoring Weights

Adjust persona vs. job relevance weighting:

```python
combined_score = embedder.compute_combined_similarity(
    section_embedding, 
    persona_embedding, 
    job_embedding,
    persona_weight=0.4,  # Adjust these weights
    job_weight=0.6
)
```

## Troubleshooting

### Common Issues

1. **No sections extracted**: Check PDF text quality and format
2. **Low relevance scores**: Verify persona and job descriptions are detailed
3. **Processing timeout**: Reduce number of PDFs or optimize section splitting
4. **Memory issues**: Use smaller embedding models for resource-constrained environments

### Logging

The system provides detailed logging. Check console output for:
- PDF processing status
- Embedding generation progress
- Section ranking details
- Error messages and warnings

## Development

### Adding New Features

1. **Custom PDF Extractors**: Extend `PDFExtractor` for domain-specific formats
2. **Additional Embedding Models**: Modify `EmbeddingGenerator` model loading
3. **Enhanced Reasoning**: Expand `DocumentRanker._generate_reasoning()`
4. **New Input Formats**: Add parsers in `app/` directory

### Testing

Create test cases with sample documents in `tests/` directory:

```python
def test_pdf_extraction():
    extractor = PDFExtractor()
    sections = extractor.extract_sections("test.pdf")
    assert len(sections) > 0
```

## License

This project is designed for hackathon use and educational purposes."# ConnectingTheDots_solution_1B" 
