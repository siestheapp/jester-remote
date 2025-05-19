# Jester: AI-Powered Size Guide Standardization

Jester is an intelligent system that processes, standardizes, and provides insights about apparel size guides. It combines computer vision, natural language processing, and vector search to create a powerful size guide knowledge base.

# Quick Setup Guide

1. Clone the repo and cd into the project directory:
   ```bash
   git clone <repo-url>
   cd jester
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install the project in editable mode:
   ```bash
   pip install -e .
   ```
5. Copy .env.example to .env and fill in your API keys and database URL.
6. (First time only) Initialize the vector search:
   ```bash
   python scripts/initialize_vector_search.py
   ```
7. Start the app:
   ```bash
   streamlit run ui/streamlit_app.py
   ```

---

## 🏗️ Architecture

Jester follows a modular architecture:

```
app/
├── api/          # FastAPI routes and endpoints
├── core/         # Core business logic
│   ├── jester_chat.py     # Chat functionality
│   └── vector_search.py   # Vector search operations
├── models/       # Pydantic data models
├── schemas/      # API request/response schemas
├── services/     # Business services
└── ui/           # Streamlit interface
```

## 🧠 Core Components

1. **Size Guide Processing**
   - Vision AI for image analysis
   - Measurement extraction and standardization
   - Automatic category detection

2. **Knowledge Base**
   - Vector search for semantic matching
   - Contextual information retrieval
   - Continuous learning from new guides

3. **Chat Interface**
   - Context-aware responses
   - Size guide-specific knowledge
   - Natural language understanding

## 📚 Key Concepts

1. **Size Guide Model**
   - Structured representation of measurements
   - Brand and category metadata
   - Standardized units and formats

2. **Vector Search**
   - Semantic similarity matching
   - Knowledge base chunks
   - Contextual relevance

3. **Chat System**
   - Session management
   - Context preservation
   - Knowledge integration

## 🛠️ Development

### Setting Up for Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Run tests:
   ```bash
   pytest tests/
   ```

3. Check code style:
   ```bash
   flake8 app/
   black app/
   ```

### Development Guidelines

1. Follow [CURSORRULES.md](CURSORRULES.md) for best practices
2. Use type hints and docstrings
3. Write tests for new features
4. Update documentation

## 📖 Documentation

- [API Documentation](docs/api/README.md)
- [Architecture Guide](docs/architecture/README.md)
- [Development Guide](docs/development/README.md)
- [Knowledge Base](docs/knowledge/README.md)

## 🔄 Workflow

1. **Size Guide Upload**
   ```python
   from app.models.size_guide import SizeGuide
   from app.services.size_service import process_size_guide
   
   # Example usage
   guide = process_size_guide(image_data, metadata)
   ```

2. **Chat Interaction**
   ```python
   from app.core.jester_chat import JesterChat
   
   # Example usage
   chat = JesterChat()
   response = chat.get_response("How should I measure chest width?")
   ```

3. **Vector Search**
   ```python
   from app.core.vector_search import JesterVectorSearch
   
   # Example usage
   search = JesterVectorSearch()
   results = search.search("chest measurement technique")
   ```

## 🤝 Contributing

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Follow code style guidelines
3. Write clear commit messages
4. Include tests with new features

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

## 🔗 Links

- [Project Documentation](docs/)
- [Issue Tracker](https://github.com/siestheapp/jester/issues)
- [Change Log](CHANGELOG.md) 