# Qdrant Vector Database - Docker Setup

This directory contains the Docker Compose configuration for running Qdrant, a vector database focused on extended filtering and high query performance.

## Overview

Qdrant, written in Rust, provides excellent performance in containerized environments with minimal overhead. This configuration sets up a single Qdrant node with customizable settings through a configuration file.

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB of available RAM (4GB recommended)
- Available ports:
  - 6333: REST API
  - 6334: gRPC API

## Getting Started

1. Create the config directory if it doesn't exist:

```bash
mkdir -p config
```

2. Start Qdrant:

```bash
docker-compose up -d
```

3. Verify the service is running:

```bash
curl http://localhost:6333/health
```

## Configuration

### Configuration File

The `config/config.yaml` file contains Qdrant configuration options:

- Storage settings
- API port configuration
- Performance tuning
- Authentication settings (commented out by default)

Modify this file to adjust Qdrant's behavior for your specific requirements.

### Environment Variables

You can override configuration file settings using environment variables in the `docker-compose.yml` file:

- `QDRANT__SERVICE__GRPC_PORT`: gRPC API port (default: 6334)
- `QDRANT__SERVICE__HTTP_PORT`: REST API port (default: 6333)
- `QDRANT__STORAGE__STORAGE_PATH`: Data storage path (default: /qdrant/storage)
- `QDRANT__SERVICE__ENABLE_TLS`: Enable TLS (default: false)
- `QDRANT__SERVICE__API_KEY`: API key for authentication (commented out)

### Resource Allocation

The default configuration allocates:
- 0.5-2 CPU cores (min-max)
- 1-4 GB RAM (min-max)

Adjust these values in the `deploy` section of the `docker-compose.yml` file based on your workload.

## Security

For production use, enable security features:

1. Uncomment and set the API key in both `docker-compose.yml` and `config.yaml`
2. Consider enabling TLS by setting `QDRANT__SERVICE__ENABLE_TLS=true` and providing certificates

## Data Persistence

All data is stored in the Docker volume `qdrant_storage`, which maps to `./qdrant_storage` on the host.

To completely reset all data:

```bash
docker-compose down -v
rm -rf ./qdrant_storage
```

## Clustered Deployment

For high availability or scaling, modify the `config.yaml` file to enable clustering:

1. Set `cluster.enabled: true`
2. Uncomment and configure the p2p section
3. Create a separate docker-compose file for additional nodes

## Troubleshooting

### Common Issues

- **Slow search performance**: Adjust `storage.optimizers` and `storage.performance` settings
- **High memory usage**: Reduce `max_segment_size_kb` in the config file
- **API timeout errors**: Increase `update_queue.retry_timeout_sec`

### Viewing Logs

```bash
docker-compose logs qdrant
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