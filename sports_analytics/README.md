# Sports Analytics RAG System

An advanced sports analytics RAG (Retrieval-Augmented Generation) system that provides intelligent, context-aware responses to complex sports queries using Groq API, Pinecone vector database, and Nomic embeddings.

## Features

- **Query Decomposition**: Breaks down complex sports questions into atomic sub-questions
- **Advanced Retrieval**: Contextual compression and semantic reranking
- **Citation-based Responses**: Every answer includes source citations
- **FastAPI Backend**: RESTful API with comprehensive error handling
- **Multi-format Data Support**: CSV, JSON, PDF, and structured data

## Technology Stack

- **Backend**: FastAPI (Python)
- **LLM**: Groq API
- **Vector Database**: Pinecone
- **Embeddings**: Nomic
- **Framework**: LangChain
- **Document Processing**: LangChain document loaders and splitters

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd sports_analytics

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
NOMIC_API_KEY=your_nomic_api_key_here

# Application Settings
APP_NAME=Sports Analytics RAG
DEBUG=True
LOG_LEVEL=INFO

# Vector Database Settings
PINECONE_INDEX_NAME=sports-analytics-rag
```

### 3. Data Preparation

Place your sports data files in the `data/` directory:

```
data/
├── team_stats.csv
├── player_stats.json
├── match_data.pdf
└── league_standings.csv
```

### 4. Run the Application

```bash
# Start the FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API

```bash
# Test the health endpoint
curl http://localhost:8000/health

# Test a query
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "Which team has the best defense and how does their goalkeeper compare to the league average?"}'
```

## API Endpoints

### POST /ask
Submit a sports analytics query and receive an intelligent response with citations.

**Request:**
```json
{
  "query": "Which team has the best defense and how does their goalkeeper compare to the league average?"
}
```

**Response:**
```json
{
  "answer": "Based on the analysis...",
  "citations": [
    {
      "source": "team_stats.csv",
      "content": "Team A has the lowest goals conceded...",
      "relevance_score": 0.95
    }
  ],
  "processing_time": 2.3,
  "sub_questions": [
    "Which team has the best defense?",
    "How does their goalkeeper compare to the league average?"
  ]
}
```

### GET /health
Check the health status of the application.

### GET /metrics
Get system performance metrics.

## Project Structure

```
sports_analytics/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── models.py               # Pydantic models
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py           # Data loading utilities
│   │   ├── chunker.py          # Document chunking
│   │   └── validator.py        # Data validation
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── decomposition.py    # Query decomposition
│   │   ├── retrieval.py        # Retrieval system
│   │   ├── compression.py      # Contextual compression
│   │   ├── reranking.py        # Semantic reranking
│   │   └── generation.py       # Response generation
│   ├── vector_store/
│   │   ├── __init__.py
│   │   ├── embeddings.py       # Embedding generation
│   │   └── pinecone_client.py  # Pinecone integration
│   └── utils/
│       ├── __init__.py
│       ├── logging.py          # Logging configuration
│       └── helpers.py          # Utility functions
├── data/                       # Sports data files
├── tests/                      # Test files
├── docs/                       # Documentation
├── requirements.txt
├── .env
├── .gitignore
├── PRD.md                      # Product Requirements Document
├── TASK_LIST.md               # Development task list
└── README.md
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_rag.py
```

### Code Formatting

```bash
# Format code with black
black src/

# Check code style with flake8
flake8 src/
```

### Adding New Data Sources

1. Add your data file to the `data/` directory
2. Update the data loader in `src/data/loader.py`
3. Test the data loading process
4. Re-index the vector database

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM access | Yes |
| `PINECONE_API_KEY` | Pinecone API key | Yes |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Yes |
| `NOMIC_API_KEY` | Nomic API key for embeddings | Yes |
| `PINECONE_INDEX_NAME` | Pinecone index name | Yes |
| `DEBUG` | Enable debug mode | No |
| `LOG_LEVEL` | Logging level | No |

### Performance Tuning

- **Chunk Size**: Adjust in `src/data/chunker.py`
- **Retrieval Parameters**: Modify in `src/rag/retrieval.py`
- **Compression Settings**: Configure in `src/rag/compression.py`
- **Reranking Parameters**: Update in `src/rag/reranking.py`

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all API keys are correctly set in `.env`
2. **Pinecone Connection Issues**: Verify environment and index name
3. **Memory Issues**: Reduce chunk size or batch size
4. **Rate Limiting**: Implement caching or reduce request frequency

### Debug Mode

Enable debug mode by setting `DEBUG=True` in your `.env` file for detailed logging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `http://localhost:8000/docs` 