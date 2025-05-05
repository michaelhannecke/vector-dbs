# Vector Database Docker Setups

This directory contains Docker Compose configurations for quickly spinning up each vector database for testing and benchmarking.

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available (16GB recommended for running multiple databases)
- Available ports on your machine (see each database section for specific ports)

## General Usage

Each database has its own directory with a `docker-compose.yml` file. To start a database:

```bash
cd docker/[database-name]
docker-compose up -d
```

To stop:

```bash
docker-compose down
```

To stop and remove volumes (wipes all data):

```bash
docker-compose down -v
```

## Database Configurations

### Milvus

```bash
cd docker/milvus
docker-compose up -d
```

- Ports:
  - 19530: Milvus server
  - 9091: Milvus web UI

Milvus requires etcd and MinIO services, which are included in the docker-compose file.

### Qdrant

```bash
cd docker/qdrant
docker-compose up -d
```

- Ports:
  - 6333: REST API
  - 6334: gRPC API

### Weaviate

```bash
cd docker/weaviate
docker-compose up -d
```

- Ports:
  - 8080: HTTP API

The configuration includes the text2vec-transformers module for text vectorization.

### Chroma

```bash
cd docker/chroma
docker-compose up -d
```

- Ports:
  - 8000: HTTP API

## Running Multiple Databases

You can run multiple databases simultaneously if your machine has sufficient resources. Be aware of port conflicts if you're running other services on these ports.

## Checking Status

Check if all containers are running:

```bash
docker ps
```

## Troubleshooting

### Memory Issues

If containers are stopping or failing to start, check Docker's resource allocation. Increase allocated memory in Docker Desktop settings or on your host system.

### Connection Issues

If you can't connect to a database, verify:

1. The container is running: `docker ps`
2. Ports are not blocked by firewalls
3. No port conflicts with other services
4. Container logs for errors: `docker logs [container-name]`

### Data Persistence

All database data is stored in Docker volumes by default. If you want to preserve data between restarts, don't use the `-v` flag when stopping containers.