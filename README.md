# Jester Ingestion Service

A service for ingesting and processing men's clothing size data, providing a unified size guide across brands.

## Project Structure

```
jester/
├── app/                    # Main application code
│   ├── api/               # API endpoints and routes
│   ├── core/              # Core application logic
│   ├── db/                # Database models and migrations
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions
├── data/                  # Data files
│   ├── raw/              # Raw input data
│   ├── processed/        # Processed data files
│   └── backups/          # Database backups
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   └── architecture/     # Architecture documentation
├── scripts/              # Utility scripts
├── tests/                # Test files
├── ui/                   # User interface components
├── .env                  # Environment variables
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore file
├── config.py            # Configuration settings
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

## Development

- Run the API server:
```bash
python main.py
```

- Run the UI:
```bash
streamlit run ui/streamlit_app.py
```

- Run tests:
```bash
pytest tests/
```

## Data Processing

The service processes men's clothing size data from various brands and creates a unified size guide. The data processing pipeline includes:

1. Data ingestion from multiple sources
2. Text chunking and embedding
3. Vector database storage
4. Size recommendation generation

## API Documentation

See [API Documentation](docs/api/README.md) for detailed API endpoints and usage.

## Architecture

See [Architecture Documentation](docs/architecture/README.md) for system design and components.

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 