# Chroma Vector Database - Docker Setup

This directory contains the Docker Compose configuration for running Chroma, a lightweight, developer-friendly vector database.

## Overview

Chroma is a modern vector database designed for ease of use and developer productivity. This configuration sets up a Chroma instance with authentication and optional HTTPS support through NGINX.

## Prerequisites

- Docker and Docker Compose installed
- At least 1GB of available RAM
- Available port: 8000 (and 443 if using NGINX)

## Getting Started

1. Configure authentication:
   - Edit `credentials.json` with your preferred usernames and tokens

2. Start Chroma:

```bash
docker-compose up -d
```

3. Verify the service is running:

```bash
curl http://localhost:8000/api/v1/heartbeat
```

## Configuration

### Environment Variables

You can customize Chroma by modifying these environment variables in the `docker-compose.yml` file:

- `CHROMA_DB_IMPL`: Database implementation (default: duckdb+parquet)
- `CHROMA_PERSISTENCE_DIRECTORY`: Data storage path (default: /chroma/chroma)
- `CHROMA_SERVER_HTTP_PORT`: HTTP server port (default: 8000)
- `CHROMA_SERVER_HOST`: Server host (default: 0.0.0.0)
- `ALLOW_RESET`: Allow collection reset (set to False in production)
- `ANONYMIZED_TELEMETRY`: Enable/disable telemetry (default: False)

### Authentication

Chroma uses token-based authentication configured in `credentials.json`:

- **users**: List of users with their authentication tokens
- **tenants**: Tenant configurations
- **tenant_memberships**: User roles within tenants

For production use:
1. Generate strong tokens
2. Set appropriate roles
3. Mount the credentials file as a volume

### HTTPS Configuration (Optional)

For production deployments, you can enable HTTPS using NGINX:

1. Generate SSL certificates and place them in `nginx/certs/`
2. Uncomment the NGINX service in `docker-compose.yml`
3. Customize `nginx/nginx.conf` with your domain name
4. Start the services with `docker-compose up -d`

## Resource Allocation

The default configuration allocates:
- 0.25-1 CPU cores (min-max)
- 512MB-2GB RAM (min-max)

Adjust these values in the `deploy` section based on your workload.

## Data Persistence

All Chroma data is stored in the `chroma_data` volume.

To reset all data:

```bash
docker-compose down -v
```

## Client Connection

To connect to Chroma from a Python client with authentication:

```python
import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host="localhost",
    port=8000,
    settings=Settings(
        chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
        chroma_client_auth_credentials="admin-secret-token-change-me"
    )
)
```

## Production Considerations

For production deployments:

1. Set `ALLOW_RESET=False` to prevent accidental data deletion
2. Use NGINX for HTTPS and rate limiting
3. Generate strong authentication tokens
4. Consider using a Docker orchestration platform like Kubernetes
5. Set up proper monitoring and backups

## Troubleshooting

### Common Issues

- **Authentication failures**: Check credentials.json format and mounted path
- **Connection refused**: Verify port mappings and firewall settings
- **Slow queries**: Adjust resource limits based on your workload

### Viewing Logs

```bash
docker-compose logs chroma
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