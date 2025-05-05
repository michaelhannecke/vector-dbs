# Milvus Vector Database - Docker Setup

This directory contains the Docker Compose configuration for running Milvus, a production-ready vector database built for scalability.

## Architecture

The Docker Compose file sets up a standalone Milvus instance with its required dependencies:

- **Milvus**: The main vector database service
- **etcd**: Used for metadata storage and service discovery
- **MinIO**: Object storage for vector data

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB of available RAM
- Available ports:
  - 19530: Milvus server
  - 9091: Milvus web UI
  - 9000: MinIO API
  - 9001: MinIO Console

## Getting Started

1. Start the Milvus stack:

```bash
docker-compose up -d
```

2. Verify all services are running:

```bash
docker-compose ps
```

3. Check Milvus health:

```bash
curl http://localhost:9091/api/v1/health
```

## Configuration Options

### Environment Variables

You can customize the setup by modifying these environment variables in the `docker-compose.yml` file:

- `MINIO_ACCESS_KEY`: MinIO access key (default: minioadmin)
- `MINIO_SECRET_KEY`: MinIO secret key (default: minioadmin)
- `DOCKER_VOLUME_DIRECTORY`: Base directory for volumes (default: current directory)

### Resource Allocation

The default configuration allocates:
- 1-4 CPU cores (min-max)
- 2-8 GB RAM (min-max)

For production use, adjust these values in the `deploy` section of the Milvus service.

## Data Persistence

All data is stored in Docker volumes:
- `./volumes/etcd`: etcd data
- `./volumes/minio`: MinIO data
- `./volumes/milvus`: Milvus data

To completely reset all data:

```bash
docker-compose down -v
rm -rf ./volumes
```

## Accessing MinIO Console

You can access the MinIO Console at http://localhost:9001 with:
- Username: minioadmin
- Password: minioadmin

This allows you to manage the object storage used by Milvus.

## Production Considerations

For production deployments:

1. Configure secure credentials for MinIO
2. Enable TLS for all services
3. Set up monitoring with Prometheus and Grafana
4. Configure regular backups
5. Consider switching to a clustered deployment

## Troubleshooting

### Common Issues

- **Memory errors**: Increase Docker memory allocation
- **Slow startup**: The first start can take up to 2 minutes
- **Connection refused**: Check if all services are running

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs milvus-standalone
```

## Cleanup

To stop and remove all services:

```bash
docker-compose down
```

To also remove volumes (deletes all data):

```bash
docker-compose down -v
```