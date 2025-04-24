# API Documentation

## Overview

The Jester Ingestion Service provides a RESTful API for ingesting and processing men's clothing size data. The API is built using FastAPI and provides endpoints for data ingestion, size guide processing, and size recommendations.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints require authentication using an API key. Include the API key in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Size Guide Ingestion

POST `/size-guides`

Ingest a new size guide into the system.

Request body:
```json
{
    "brand": "string",
    "category": "string",
    "measurements": [
        {
            "name": "string",
            "value": "number",
            "unit": "string"
        }
    ]
}
```

### Size Recommendations

GET `/recommendations`

Get size recommendations based on measurements.

Query parameters:
- `brand`: string
- `category`: string
- `measurements`: json

Example:
```
/recommendations?brand=nike&category=shirts&measurements={"chest":42,"waist":36}
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

API requests are limited to 100 requests per minute per API key.

## Development

To run the API server locally:

```bash
python main.py
```

The API will be available at `http://localhost:8000`.
