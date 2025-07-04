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

```bash
# Run individual examples (requires database to be running)
python examples/milvus_example.py
python examples/qdrant_example.py
python examples/weaviate_example.py
python examples/chroma_example.py
python examples/faiss_example.py

# Run performance benchmark across all databases
python examples/vector_db_benchmark.py
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
