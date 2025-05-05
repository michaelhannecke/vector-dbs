# Vector Database Monitoring Setup

This directory contains a Prometheus and Grafana setup for monitoring vector databases.

## Components

- **Prometheus**: Time-series database for metrics collection
- **Grafana**: Visualization dashboard
- **Node Exporter**: Host metrics collection
- **cAdvisor**: Container metrics collection

## Prerequisites

- Docker and Docker Compose installed
- Vector database services already running
- Available ports:
  - 9090: Prometheus web interface
  - 3000: Grafana dashboard

## Getting Started

1. Create the necessary directories:

```bash
mkdir -p prometheus grafana/provisioning/datasources grafana/provisioning/dashboards grafana/dashboards
```

2. Start the monitoring stack:

```bash
docker-compose up -d
```

3. Access Grafana:
   - Open your browser and navigate to http://localhost:3000
   - Login with admin/admin_password_change_me
   - The default dashboards should be automatically loaded

## Configuration

### Prometheus Configuration

The `prometheus/prometheus.yml` file configures which services are monitored. It includes:

- Basic system monitoring (Prometheus itself, Node Exporter, cAdvisor)
- Vector database services (Milvus, Qdrant, Weaviate)
- HTTP endpoint checks for services without direct metrics (Chroma, FAISS API)

To add custom metrics or alerting, modify this file.

### Grafana Configuration

- **Data Sources**: Automatically provisioned to connect to Prometheus
- **Dashboards**: Pre-configured dashboards for each vector database

## Dashboards

The following dashboards are included:

1. **System Overview**: Host and container metrics
2. **Milvus Dashboard**: Milvus-specific metrics and performance indicators
3. **Qdrant Dashboard**: Qdrant performance monitoring
4. **Weaviate Dashboard**: Weaviate metrics
5. **Chroma & FAISS**: Basic availability and response time monitoring

## Network Configuration

The monitoring services are configured to connect to each vector database's network:

- milvus-network
- qdrant-network
- weaviate-network
- chroma-network
- faiss-network

These networks must be created and set to "external" in their respective docker-compose files.

## Security Considerations

For production use:

1. Change the default Grafana admin password
2. Add authentication to Prometheus
3. Configure TLS for all services
4. Implement proper network isolation

## Adding Custom Alerts

To add alerts:

1. Create a rules file in the prometheus directory:

```yaml
# prometheus/alert_rules.yml
groups:
- name: vector-db-alerts
  rules:
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes{name=~"milvus.*|qdrant.*|weaviate.*|chroma.*|faiss.*"} > 1e9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.name }}"
      description: "Container {{ $labels.name }} memory usage is above 1GB for 5 minutes."
```

2. Add the rules file to prometheus.yml:

```yaml
rule_files:
  - "alert_rules.yml"
```

## Troubleshooting

### Common Issues

- **Can't scrape metrics**: Check network connectivity and firewall settings
- **Missing dashboards**: Verify Grafana provisioning configuration
- **High resource usage**: Adjust Prometheus storage retention and scrape intervals

### Viewing Logs

```bash
docker-compose logs prometheus
docker-compose logs grafana
```

## Cleanup

To stop and remove the monitoring services:

```bash
docker-compose down
```

To also remove the data volumes:

```bash
docker-compose down -v
```