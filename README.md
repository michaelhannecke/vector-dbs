# Containerizing Vector Databases: A Docker Guide for Modern AI Infrastructure

This repository provides production-ready Docker configurations, example scripts, and comprehensive test suites for deploying the top 5 open source vector databases as containerized applications.

![Containerization of Vector DBs](/docu/container.jpeg)


## Introduction

In the era of AI applications, vector databases have become crucial infrastructure components for storing and querying high-dimensional data. Containerization offers numerous advantages for vector database deployments, including:

- **Isolation**: Run your vector database in a controlled environment without dependency conflicts
- **Portability**: Deploy the same configuration across development, testing, and production
- **Scalability**: Easily scale with container orchestration platforms like Kubernetes
- **Reproducibility**: Share configurations through Docker files for consistent environments
- **Resource management**: Allocate specific CPU and memory resources to optimize performance

This guide provides ready-to-use Docker configurations for the top 5 open source vector databases: Milvus, Qdrant, Weaviate, Chroma, and FAISS (with a custom REST API wrapper).

## Vector Databases Included

This repository includes Docker configurations for:

1. **Milvus**: Production-ready vector database with high scalability
2. **Qdrant**: Vector search engine with powerful filtering capabilities
3. **Weaviate**: Semantic vector database with ML-first architecture
4. **Chroma**: Lightweight and developer-friendly vector database
5. **FAISS**: Efficient similarity search library (with a custom API wrapper)

## Getting Started

Each database has its own directory with all necessary configuration files. Follow the README in each directory for specific instructions.

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available (16GB recommended for running multiple databases)
- Git

### Quick Start

Clone this repository:

```bash
git clone https://github.com/yourusername/vector-db-docker.git
cd vector-db-docker
```

To run a specific database (e.g., Milvus):

```bash
cd docker/milvus
docker-compose up -d
```

Each database runs on a different port to avoid conflicts:
- **Milvus**: 19530 (gRPC), 9091 (HTTP)
- **Qdrant**: 6333 (REST), 6334 (gRPC)  
- **Weaviate**: 8080 (HTTP)
- **Chroma**: 8000 (HTTP)
- **FAISS API**: 5000 (HTTP)

## Repository Structure

```
vector-dbs/
├── docker/                          # Docker configurations for each database
│   ├── milvus/                      # Milvus multi-container setup
│   ├── qdrant/                      # Qdrant single-container setup  
│   ├── weaviate/                    # Weaviate with transformer modules
│   ├── chroma/                      # Chroma with optional NGINX proxy
│   └── faiss-api/                   # FAISS with custom REST API
├── examples/                        # Python client examples
│   ├── chroma_example.py            # Chroma usage with persistence
│   ├── faiss_example.py             # FAISS local usage patterns
│   ├── milvus_example.py            # Milvus with schema management
│   ├── qdrant_example.py            # Qdrant with filtering
│   ├── weaviate_example.py          # Weaviate GraphQL queries
│   └── vector_db_benchmark.py       # Performance comparison script
├── tests/                           # Comprehensive test suite
│   ├── test_docker_compose.py       # Docker configuration validation
│   ├── test_faiss_api.py            # FAISS API functionality tests
│   ├── test_examples.py             # Example script validation
│   ├── test_integration.py          # End-to-end integration tests
│   └── conftest.py                  # Test fixtures and configuration
├── monitoring/                      # Observability stack
│   ├── docker-compose.yaml          # Prometheus + Grafana setup
│   └── prometheus/                  # Monitoring configurations
├── run_tests.sh                     # Test runner script
├── pytest.ini                      # Test configuration
└── CLAUDE.md                        # Development guidelines
```


## Configuration Options

Each database's Docker Compose file includes common configuration options:

- Volume mounts for data persistence
- Port mappings
- Environment variables for customization
- Memory/CPU constraints
- Health checks

## Monitoring Setup

The `/monitoring` directory contains a Docker Compose file for deploying Prometheus and Grafana to monitor your vector databases. 

## Testing and Quality Assurance

This repository includes a comprehensive test suite covering:

### Test Categories
- **Unit Tests**: Configuration validation and API logic testing
- **Integration Tests**: End-to-end service deployment verification
- **Example Tests**: Python script syntax and functionality validation
- **Docker Tests**: Container build and configuration verification

### Running Tests
```bash
# Run all tests
./run_tests.sh

# Run specific test categories
./run_tests.sh unit           # Unit tests only
./run_tests.sh integration    # Integration tests (requires Docker)
./run_tests.sh coverage      # Generate coverage report

# Run tests with pytest directly
pytest tests/                 # All tests
pytest -m "not integration"   # Skip integration tests
pytest tests/test_faiss_api.py # Specific test file
```

### Test Requirements
```bash
# Install test dependencies
pip install -r tests/requirements.txt
```

## Example Usage

Each database includes a complete Python example demonstrating:
- Connection and authentication
- Collection/index creation and management
- Vector insertion with metadata
- Similarity search with filtering
- Cleanup and resource management

### Setting Up Python Environment

First, install the required Python dependencies:

```bash
# Install all vector database client dependencies
pip install -r requirements.txt
```

### Running Examples

**Important**: Each example requires the corresponding Docker service to be running first.

#### 1. Start a Vector Database Service

Choose one of the following databases to start:

```bash
# Start Milvus
cd docker/milvus && docker-compose up -d

# Start Qdrant
cd docker/qdrant && docker-compose up -d

# Start Weaviate
cd docker/weaviate && docker-compose up -d

# Start Chroma
cd docker/chroma && docker-compose up -d

# Start FAISS API
cd docker/faiss-api && docker-compose up -d
```

#### 2. Wait for Service to be Ready

Check that the service is healthy before running examples:

```bash
# Check service status
docker-compose ps

# Check service logs
docker-compose logs -f
```

#### 3. Run the Corresponding Example

Return to the repository root and run the example:

```bash
# Run individual examples (requires corresponding database to be running)
python examples/milvus_example.py     # Requires Milvus running on port 19530
python examples/qdrant_example.py     # Requires Qdrant running on port 6333
python examples/weaviate_example.py   # Requires Weaviate running on port 8080
python examples/chroma_example.py     # Uses local file storage (no service required)
python examples/faiss_example.py      # Uses local FAISS library (no service required)

# Run performance benchmark across all databases
python examples/vector_db_benchmark.py
```

#### 4. Service-Specific Notes

- **Chroma**: The example uses local file storage by default. To use the Docker service, modify the connection in `examples/chroma_example.py` to connect to `http://localhost:8000`
- **FAISS**: The example uses the local FAISS library. For the REST API version, use the endpoint `http://localhost:5000`
- **Milvus**: Requires the most time to start due to multiple dependencies (etcd, MinIO)
- **Qdrant, Weaviate**: Usually ready within 30-60 seconds

#### 5. Stopping Services

When finished with examples:

```bash
# Stop a specific service
cd docker/{database-name}
docker-compose down

# Stop all services and remove volumes (data will be lost)
docker-compose down -v
```

## Production Considerations

For production deployments, consider:

1. **Container Orchestration**: Use Kubernetes for scalability and management
2. **Security**: Enable authentication, configure TLS, secure API tokens
3. **Persistence**: Configure proper volume mounts and backup strategies
4. **Monitoring**: Deploy the included Prometheus/Grafana stack
5. **Resource Tuning**: Adjust memory/CPU limits based on workload
6. **High Availability**: Configure clustering for supported databases
7. **Network Security**: Use proper firewall rules and network segmentation
