# LibreSIEM Deployment Guide

This guide explains how to deploy LibreSIEM in various environments.

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for local development)
- Apache Kafka 2.8+ or a managed Kafka service
- Elasticsearch 8.x or OpenSearch
- (Optional) Prometheus and Grafana for monitoring

## Configuration

LibreSIEM uses environment variables for configuration. Copy `.env.example` to `.env` and modify the values according to your environment:

```bash
cp .env.example .env
```

### Common Deployment Scenarios

1. **Local Development**
   ```bash
   # Start required services
   docker-compose up -d
   
   # Install dependencies
   poetry install
   
   # Run the collector
   poetry run python -m libreSIEM.collector
   ```

2. **Production with External Kafka**
   ```bash
   # Update .env with your Kafka configuration
   KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092,kafka3:9092
   KAFKA_SECURITY_PROTOCOL=SASL_SSL
   KAFKA_SASL_MECHANISM=PLAIN
   KAFKA_SASL_USERNAME=your-username
   KAFKA_SASL_PASSWORD=your-password
   KAFKA_SSL_CAFILE=/path/to/ca.pem
   ```

3. **Kubernetes Deployment**
   - Use the provided Helm charts in the `deployment/kubernetes` directory
   - Configure using Kubernetes ConfigMaps and Secrets
   - See `deployment/kubernetes/README.md` for detailed instructions

### Security Considerations

1. **Kafka Security**
   - Enable SASL authentication in production
   - Use SSL/TLS encryption for data in transit
   - Configure ACLs to restrict topic access

2. **API Security**
   - Deploy behind a reverse proxy (nginx, traefik)
   - Enable TLS termination
   - Implement authentication (coming soon)

3. **Network Security**
   - Use private networks for component communication
   - Implement network policies in Kubernetes
   - Configure firewalls to restrict access

### Scaling Considerations

1. **Kafka Topics**
   - Configure proper partitioning for your load
   - Consider using multiple consumer groups
   - Monitor consumer lag

2. **Collector Service**
   - Can be horizontally scaled
   - Use load balancer for distribution
   - Monitor resource usage

### Monitoring

1. **Metrics Available**
   - Kafka producer/consumer metrics
   - Collector API metrics
   - System resource usage

2. **Prometheus Integration**
   - Metrics exposed on `/metrics`
   - Use provided Grafana dashboards

### Backup and Disaster Recovery

1. **Configuration Backup**
   - Version control your configurations
   - Regular backup of .env files
   - Document custom changes

2. **Data Backup**
   - Regular Elasticsearch snapshots
   - Kafka topic replication
   - Backup automation scripts provided

## Troubleshooting

### Common Issues

1. **Kafka Connection Issues**
   - Verify network connectivity
   - Check security configuration
   - Validate broker addresses

2. **Performance Issues**
   - Monitor consumer lag
   - Check resource utilization
   - Adjust buffer sizes

### Getting Help

- Open issues on GitHub
- Check existing documentation
- Join the community discussions
