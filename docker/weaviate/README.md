# Weaviate Vector Database - Docker Setup

This directory contains the Docker Compose configuration for running Weaviate, a semantic vector database with ML-first architecture and GraphQL API.

## Architecture

The Docker Compose file sets up a Weaviate instance with the following components:

- **Weaviate**: The main vector database service
- **text2vec-transformers**: Module for text vectorization
- **img2vec-neural**: Module for image vectorization
- **backup**: Container for backup operations

## Prerequisites

- Docker and Docker Compose installed
- At least 6GB of available RAM (8GB recommended)
- Available port: 8080

## Getting Started

1. Start Weaviate:

```bash
docker-compose up -d
```

2. Verify the service is running:

```bash
curl http://localhost:8080/v1/meta
```

3. Access the Weaviate GraphQL interface:
   - Open your browser and navigate to http://localhost:8080/v1/graphql

## Configuration

### Modules

This configuration includes several Weaviate modules:

- **text2vec-transformers**: Vectorizes text input using the sentence-transformers-multi-qa-MiniLM-L6-cos-v1 model
- **img2vec-neural**: Vectorizes image input using the ResNet50 model
- **backup-filesystem**: Enables backup and restore functionality

### Environment Variables

You can customize the setup by modifying these environment variables in the `docker-compose.yml` file:

- `QUERY_DEFAULTS_LIMIT`: Default limit for queries (default: 25)
- `DEFAULT_VECTORIZER_MODULE`: Default vectorizer module (default: text2vec-transformers)
- `ENABLE_MODULES`: Enabled modules
- `TRANSFORMERS_INFERENCE_API`: Endpoint for text transformer inference
- `IMGNEURAL_INFERENCE_API`: Endpoint for image vectorization
- `CLUSTER_HOSTNAME`: Hostname for this node in a cluster

### Authentication

For production use, uncomment and configure these security-related environment variables:

- `AUTHENTICATION_APIKEY_ENABLED`: Enable API key authentication
- `AUTHENTICATION_APIKEY_ALLOWED_KEYS`: List of allowed API keys
- `AUTHENTICATION_APIKEY_USERS`: List of user names associated with API keys

### GPU Acceleration

To enable GPU acceleration for the vectorizer modules:

1. Set `ENABLE_CUDA: '1'` for the desired module
2. Ensure your host has NVIDIA Docker support configured
3. Add the required GPU configuration to the service

## Data Persistence

All Weaviate data is stored in the `weaviate_data` volume.

## Backups

This setup includes a backup container for convenient backup and restore operations:

1. To create a backup:

```bash
docker-compose exec backup bash -c "cd /data && tar -czf /backup/weaviate-backup-$(date +%F).tar.gz ."
```

2. To restore from a backup:

```bash
# Stop Weaviate first
docker-compose stop weaviate

# Restore data
docker-compose exec backup bash -c "rm -rf /data/* && tar -xzf /backup/weaviate-backup-DATE.tar.gz -C /data"

# Restart Weaviate
docker-compose start weaviate
```

## Resource Allocation

The default configuration allocates:
- Weaviate: 0.5-2 CPU cores, 1-4 GB RAM
- Text vectorizer: 1 CPU core, 2 GB RAM
- Image vectorizer: 1 CPU core, 2 GB RAM

Adjust these values in the `deploy` section of each service based on your workload.

## Troubleshooting

### Common Issues

- **High memory usage**: The transformer modules require significant memory; reduce limits or use smaller models
- **Slow startup**: The first start can take several minutes while models are downloaded
- **Module errors**: Check if the vectorizer modules are healthy

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs weaviate
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