# FAISS Vector Search API - Docker Setup

This directory contains a custom RESTful API wrapper for Facebook AI Similarity Search (FAISS), making it accessible as a containerized vector database service.

## Overview

FAISS is a library for efficient similarity search, not a standalone database. This solution includes:

- A Flask-based REST API for FAISS
- Docker containerization for easy deployment
- Persistent storage for index files
- Authentication and performance optimization

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB of available RAM
- Available port: 5000

## Getting Started

1. Build and start the FAISS API service:

```bash
docker-compose up -d
```

2. Verify the service is running:

```bash
curl http://localhost:5000/health
```

## Configuration

### Environment Variables

You can customize the FAISS API by modifying these environment variables in the `docker-compose.yml` file:

- `INDEX_PATH`: Path to store the index file (default: /data/faiss/index.idx)
- `VECTOR_DIMENSION`: Dimension of vectors (default: 384)
- `INDEX_TYPE`: FAISS index type (options: Flat, IVF, HNSW)
- `NLIST`: Number of clusters for IVF indexes (default: 100)
- `NPROBE`: Number of clusters to probe during search (default: 10)
- `API_TOKEN`: Authentication token (set a strong value for production)

### Index Types

This API supports multiple FAISS index types:

- **Flat**: Exact search, no approximation
- **IVF**: Inverted file index with approximate search
- **HNSW**: Hierarchical Navigable Small World graph index

Choose based on your requirements for search speed versus accuracy.

## API Endpoints

### Authentication

All endpoints (except /health) require authentication when API_TOKEN is set:

```
Authorization: Bearer your-api-token-change-me
```

### Endpoints

- **GET /health**: Check if the service is running
- **GET /stats**: Get index statistics
- **POST /add**: Add vectors to the index
- **POST /search**: Search for similar vectors
- **POST /delete**: Delete vectors by ID
- **POST /reset**: Reset the index

## API Usage Examples

### Adding Vectors

```bash
curl -X POST http://localhost:5000/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-token-change-me" \
  -d '{
    "vectors": [[0.1, 0.2, ..., 0.3], [0.4, 0.5, ..., 0.6]],
    "ids": [1, 2]
  }'
```

### Searching Vectors

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-token-change-me" \
  -d '{
    "query_vectors": [[0.1, 0.2, ..., 0.3]],
    "k": 5,
    "nprobe": 20
  }'
```

## Performance Optimization

For improved performance:

1. Choose the appropriate index type:
   - **Flat**: Best for small datasets (up to 1M vectors) or when exact results are required
   - **IVF**: Good for medium to large datasets with a small accuracy trade-off
   - **HNSW**: Best for large datasets with good approximate results

2. Tune parameters:
   - Increase `NPROBE` for better search accuracy (at the cost of speed)
   - Adjust `NLIST` based on your dataset size (typically sqrt(n) where n is the dataset size)

3. Consider GPU acceleration:
   - Replace `faiss-cpu` with `faiss-gpu` in requirements.txt
   - Modify the Dockerfile to use a CUDA-enabled base image
   - Add GPU configuration to the docker-compose.yml file

## Resource Allocation

The default configuration allocates:
- 0.5-2 CPU cores (min-max)
- 1-4 GB RAM (min-max)

Adjust these values in the `deploy` section based on your workload.

## Data Persistence

The FAISS index is stored in the `faiss_data` volume.

## Client Integration

Here's an example of how to use the API from Python:

```python
import requests
import numpy as np

API_URL = "http://localhost:5000"
API_TOKEN = "your-api-token-change-me"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# Add vectors
vectors = np.random.random((100, 384)).astype('float32').tolist()
ids = list(range(100))

response = requests.post(
    f"{API_URL}/add",
    headers=HEADERS,
    json={"vectors": vectors, "ids": ids}
)
print(response.json())

# Search vectors
query_vector = np.random.random((1, 384)).astype('float32').tolist()

response = requests.post(
    f"{API_URL}/search",
    headers=HEADERS,
    json={"query_vectors": query_vector, "k": 5}
)
print(response.json())
```

## Troubleshooting

### Common Issues

- **Memory errors**: Check if your vectors are too large for the allocated memory
- **Dimension mismatch**: Ensure all vectors have the dimension specified in the environment variables
- **Authentication failures**: Verify API_TOKEN is correctly set and used in the Authorization header

### Viewing Logs

```bash
docker-compose logs faiss-api
```

## Cleanup

To stop and remove the service:

```bash
docker-compose down
```

To also remove the data volume:

```bash
docker-compose down -v
```