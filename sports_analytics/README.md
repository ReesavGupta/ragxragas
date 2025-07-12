# Sports Analytics RAG System

An advanced sports analytics RAG (Retrieval-Augmented Generation) system that provides intelligent, context-aware responses to complex sports queries using Groq API, Pinecone vector database, and Nomic embeddings.

## 🚀 Features

- **Query Decomposition**: Breaks down complex sports questions into atomic sub-questions
- **Advanced Retrieval**: Contextual compression and semantic reranking
- **Parallel Processing**: Sub-questions processed concurrently for faster responses
- **Citation-based Responses**: Every answer includes source citations
- **Beautiful Web Interface**: Streamlit app with modern UI and real-time processing
- **Multi-format Data Support**: CSV, JSON, PDF, and structured data
- **Performance Optimized**: ~80% faster processing with parallel execution

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python)
- **LLM**: Groq API (Llama3-8b-8192)
- **Vector Database**: Pinecone
- **Embeddings**: Nomic (nomic-embed-text-v1.5)
- **Framework**: LangChain
- **Document Processing**: LangChain document loaders and splitters
- **Parallel Processing**: ThreadPoolExecutor for concurrent sub-question processing

## ⚡ Performance

- **Processing Time**: ~13 seconds for complex queries (down from ~68 seconds)
- **Parallel Processing**: 4 sub-questions processed concurrently
- **Optimized Retrieval**: Reduced document count and improved caching
- **Smart Rate Limiting**: Intelligent delays to avoid API limits

## 🚀 Quick Start

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
# Start the Streamlit web app
streamlit run streamlit_app.py
```

The app will be available at `http://localhost:8501`

## 🎯 Usage

### Web Interface

1. **Open the Streamlit app** at `http://localhost:8501`
2. **Enter your sports query** in the text area
3. **Click "Process Query"** to get intelligent responses
4. **View results** with:
   - Query decomposition into sub-questions
   - Real-time processing progress
   - Confidence metrics
   - Detailed answers with citations
   - Source documents

### Example Queries

- "Which team has the best defense in the Premier League and how does their goalkeeper's save percentage compare to the league average?"
- "What are the key performance metrics for Manchester City?"
- "Which players have the best assist records?"
- "How do goalkeeper statistics compare across teams?"

## 📊 Project Structure

```
sports_analytics/
├── streamlit_app.py           # Main Streamlit web application
├── src/
│   ├── __init__.py
│   ├── main.py                # Core application logic
│   ├── config.py              # Configuration settings
│   ├── models.py              # Data models
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py          # Data loading utilities
│   │   ├── chunker.py         # Document chunking
│   │   └── ingestion.py       # Data ingestion pipeline
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── decomposition.py   # Query decomposition
│   │   ├── retrieval.py       # Retrieval system
│   │   └── generation.py      # Response generation
│   ├── vector_store/
│   │   ├── __init__.py
│   │   └── embeddings_and_vectorstore.py  # Vector store integration
│   └── utils/
│       ├── __init__.py
│       ├── logging.py         # Logging configuration
│       └── helpers.py         # Utility functions
├── data/                      # Sports data files
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Configuration

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

### Performance Settings

- **Chunk Size**: 800 characters (optimized for speed)
- **Retrieval Count**: 3 documents per query (reduced for efficiency)
- **Parallel Workers**: 4 concurrent sub-question processors
- **Rate Limiting**: 0.3 second delays between requests

## 🔧 Advanced Features

### Query Decomposition

The system automatically breaks down complex queries into sub-questions:

```
Original: "Which team has the best defense and how does their goalkeeper compare?"
Sub-questions:
1. Which teams have the best defensive records?
2. What is the average save percentage for goalkeepers?
3. How does the best defensive team's goalkeeper compare?
4. Are there significant differences in performance?
```

### Contextual Compression

- **Document Compression**: Reduces document size while preserving key information
- **Semantic Reranking**: Ranks documents by relevance to query
- **Source Citations**: Every answer includes traceable sources

### Parallel Processing

- **Concurrent Execution**: Sub-questions processed simultaneously
- **ThreadPoolExecutor**: Manages parallel processing with configurable workers
- **Error Handling**: Graceful failure handling for individual sub-questions

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all API keys are correctly set in `.env`
2. **Pinecone Connection Issues**: Verify environment and index name
3. **Rate Limiting**: System automatically handles Groq API rate limits
4. **Memory Issues**: Optimized chunk sizes and retrieval counts

### Performance Tips

- **Reduce Query Complexity**: Simpler queries process faster
- **Monitor API Usage**: Check Groq console for rate limit status
- **Cache Results**: Repeated queries return faster responses

## 📈 Performance Metrics

- **Average Processing Time**: ~13 seconds for complex queries
- **Sub-question Processing**: 4 questions processed in parallel
- **Document Retrieval**: 3 documents per query (optimized)
- **Confidence Scoring**: Automatic relevance assessment
- **Error Recovery**: Graceful handling of API failures

## 🎨 UI Features

- **Real-time Progress**: Live processing indicators
- **Confidence Metrics**: Visual confidence scores
- **Source Citations**: Clickable source references
- **Query Examples**: Pre-built example queries
- **Responsive Design**: Works on desktop and mobile
- **Dark/Light Theme**: Automatic text color adaptation

## 🔮 Future Enhancements

- **Caching Layer**: Redis integration for faster repeated queries
- **Advanced Reranking**: Cross-encoder reranking for better relevance
- **Multi-language Support**: Support for multiple languages
- **Real-time Data**: Live sports data integration
- **Analytics Dashboard**: Advanced analytics and insights

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues and questions, please open an issue on the repository.

---

**Built with ❤️ using Streamlit, LangChain, Groq, and Pinecone** 