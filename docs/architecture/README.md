# Architecture Documentation

## Overview

The Jester Ingestion Service is a comprehensive system for processing and standardizing men's clothing size data across different brands. The architecture is designed to handle the complexities of size guide data ingestion, normalization, and recommendation generation.

## System Components

1. **API Layer**
   - FastAPI-based REST API
   - Handles incoming requests
   - Input validation and rate limiting
   - Authentication and authorization

2. **Core Services**
   - Size Guide Processing
   - Measurement Normalization
   - Vector Embedding Generation
   - Size Recommendation Engine

3. **Data Storage**
   - PostgreSQL Database
   - Vector Database (FAISS)
   - File Storage for Raw Data

4. **UI Components**
   - Streamlit-based Web Interface
   - Interactive Size Guide Upload
   - Real-time Processing Feedback
   - Size Recommendation Interface

## Data Flow

1. **Ingestion**
   - Size guide data received via API
   - Initial validation and preprocessing
   - Storage of raw data

2. **Processing**
   - Measurement extraction and normalization
   - Vector embedding generation
   - Database storage

3. **Recommendation**
   - User measurement input
   - Vector similarity search
   - Size mapping and confidence scoring

## Security

- API Key Authentication
- Environment Variable Configuration
- Input Validation
- Rate Limiting
- Error Handling

## Scalability

The system is designed to scale horizontally:
- Stateless API servers
- Connection pooling for database
- Caching layer for frequent queries
- Batch processing capabilities

## Monitoring

- Request logging
- Error tracking
- Performance metrics
- Database monitoring

## Development

- Git-based version control
- CI/CD pipeline
- Test coverage
- Documentation updates

## Database Schema

### Core Tables

1. **apparel_items**
   - Primary table for storing clothing measurements
   - Links to brands, categories, and fits
   - Stores measurement ranges (min/max) for various body parts

2. **brands**
   - Stores brand information
   - Includes default unit system (inches/cm)

3. **categories** and **subcategories**
   - Hierarchical organization of clothing types
   - Categories: tops, bottoms, outerwear, etc.
   - Subcategories: dress shirts, t-shirts, jeans, etc.

4. **fits**
   - Stores different fit types (slim, regular, relaxed)
   - Includes descriptions and gender associations

5. **size_guides**
   - Brand-specific size guide information
   - Similar structure to apparel_items
   - Includes source URLs and ingestion metadata

6. **size_aliases**
   - Maps different size labels to standardized sizes
   - Helps with cross-brand size comparison

### Supporting Tables

1. **genders**
   - Basic gender categorization

2. **units**
   - Measurement unit systems

3. **ingestion_log**
   - Tracks data ingestion processes
   - Stores metadata about source files

## Vector Search

The system uses FAISS for vector similarity search:
- Text chunks are embedded using OpenAI's embedding model
- Embeddings are stored in a FAISS index
- Similarity search is used for finding relevant size guides

## Performance Considerations

1. **Database Optimization**
   - Indexed fields for common queries
   - Partitioned tables for large datasets
   - Regular maintenance and cleanup

2. **Vector Search**
   - Optimized index structure
   - Batch processing for embeddings
   - Caching of common queries

3. **API Performance**
   - Response caching
   - Asynchronous processing
   - Load balancing ready

## Monitoring and Logging

- Application logs in `logs/` directory
- Error tracking and reporting
- Performance metrics collection
- Database query monitoring

## Deployment

The system is designed to be deployed using:
- Docker containers
- Environment-based configuration
- Database migrations
- Backup and recovery procedures

## Future Improvements

1. **Database Enhancements**
   - Add foreign key constraints
   - Create missing indexes
   - Add data validation constraints
   - Implement proper unit conversion

2. **Data Quality**
   - Standardize measurement units
   - Validate size ranges
   - Ensure consistent category hierarchy

3. **Performance Optimization**
   - Index optimization
   - Query optimization
   - Data partitioning strategy
