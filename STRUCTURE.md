# Repository Structure

```
vector-db-docker/
├── README.md                  # Main documentation
├── STRUCTURE.md               # This file
│
├── milvus/                    # Milvus Docker configuration
│   ├── docker-compose.yml     # Milvus Docker Compose file
│   ├── README.md              # Milvus-specific documentation
│   └── volumes/               # Created on first run
│       ├── etcd/              # etcd data
│       ├── minio/             # MinIO data
│       └── milvus/            # Milvus data
│
├── qdrant/                    # Qdrant Docker configuration
│   ├── docker-compose.yml     # Qdrant Docker Compose file
│   ├── config/                # Qdrant configuration
│   │   └── config.yaml        # Qdrant configuration file
│   ├── README.md              # Qdrant-specific documentation
│   └── qdrant_storage/        # Created on first run
│
├── weaviate/                  # Weaviate Docker configuration
│   ├── docker-compose.yml     # Weaviate Docker Compose file
│   ├── README.md              # Weaviate-specific documentation
│   └── volumes/               # Created on first run
│
├── chroma/                    # Chroma Docker configuration
│   ├── docker-compose.yml     # Chroma Docker Compose file
│   ├── credentials.json       # Chroma authentication
│   ├── nginx/                 # NGINX for HTTPS and rate limiting
│   │   ├── nginx.conf         # NGINX configuration
│   │   └── certs/             # SSL certificates (to be added)
│   ├── README.md              # Chroma-specific documentation
│   └── chroma_data/           # Created on first run
│
├── faiss-api/                 # FAISS with API wrapper
│   ├── docker-compose.yml     # FAISS API Docker Compose file
│   ├── Dockerfile             # FAISS API Dockerfile
│   ├── app.py                 # FAISS API implementation
│   ├── requirements.txt       # Python dependencies
│   ├── README.md              # FAISS-specific documentation
│   └── data/                  # Created on first run
│
├── monitoring/                # Monitoring setup
│   ├── docker-compose.yml     # Prometheus & Grafana setup
│   ├── prometheus/            # Prometheus configuration
│   │   └── prometheus.yml     # Prometheus config file
│   ├── grafana/               # Grafana configuration
│       └── provisioning/      # Grafana provisioning
│           └── datasources/   # Datasource configuration
│               └── prometheus.yml # Prometheus datasource 
│
├── examples/                  # Example client scripts
│   ├── milvus_examples.py       # Milvus Python client example
│   ├── qdrant_examples.py       # Qdrant Python client example
│   ├── weaviate_examples.py     # Weaviate Python client example
│   ├── chroma_examples.py       # Chroma Python client example
│   └── faiss_examples.py        # FAISS API client example
│

```

## Directory Contents

### `/milvus`, `/qdrant`, `/weaviate`, `/chroma`, `/faiss-api`

Each directory contains everything needed to deploy a specific vector database using Docker:
- Docker Compose file for container orchestration
- Configuration files specific to each database
- README with setup and usage instructions

### `/monitoring`

Contains Prometheus and Grafana configuration for monitoring all vector databases:
- Docker Compose file for monitoring stack
- Prometheus configuration


### `/examples`

Contains Python client examples for interacting with each containerized vector database.

