# LibreSIEM

A modern, open-source Security Information and Event Management (SIEM) system with real-time monitoring, advanced analytics, and a beautiful dashboard.

## Screenshots

### Dashboard Overview
![Dashboard Overview](./SIEMS_Images/Dashboard_LibreSIEM.png)

## Dashboard Features
 🛡️

A lightweight, cloud-native, open-source Security Information & Event Management (SIEM) system providing real-time log analysis, threat detection, and alerting capabilities. LibreSIEM is designed to be modular, scalable, and easy to integrate.

## 🌟 Key Features

- **Event Collection & Ingestion** 🔄
  - ✅ REST API for log ingestion
  - ✅ JWT authentication with IP binding and brute-force protection
  - ✅ Redis-based rate limiting with per-user quotas
  - ✅ Multi-format log parsing:
    - Apache Combined Log Format
    - Syslog with automatic year handling
    - JSON with flexible schema
  - ✅ Batch ingestion with granular rate limits
  - ✅ Input validation and sanitization
  - ✅ Detailed error reporting and rate limit tracking
  - ✅ Webhooks support
  - ⏳ Fluentd and Filebeat support (coming soon)
  - ✅ Agentless collection for cloud services:
    - AWS CloudWatch
    - Azure Monitor
    - Google Cloud Logging
  - ✅ Security device integration:
    - Firewalls
    - IDS/IPS systems
    - Endpoint security

- **Data Processing & Storage** 🔄
  - ✅ Elasticsearch integration:
    - Primary storage with optimized mappings
    - Monthly index rotation with ILM policies
    - Hot/Warm/Cold/Delete lifecycle management
    - Enrichment pipeline support
  - ✅ Log enrichment pipeline:
    - Timestamp normalization and timezone handling
    - Processing metadata
    - Structured data extraction
  - ✅ Efficient search capabilities:
    - Full-text search
    - Time-based queries
    - Field-specific filtering
  - ✅ Advanced enrichment:
    - GeoIP lookup with city, country, ASN data
    - DNS resolution with caching
    - Threat intelligence from multiple sources
  - ✅ Cold storage support:
    - AWS S3 integration
    - MinIO compatibility
    - Configurable archival rules
  - ✅ Log deduplication:
    - Fuzzy matching based on event fingerprints
    - Configurable deduplication window
    - Memory-efficient caching

- **Threat Detection & Correlation** ✅
  - ✅ Real-time detection rules:
    - Custom rule engine with flexible conditions
    - Field matching, regex support, and numerical comparisons
    - AND/OR operators for complex rules
  - ✅ Sigma Rules support:
    - Full Sigma rule parsing and matching
    - Support for all Sigma operators and conditions
    - Compatible with standard Sigma rule format
  - ✅ YARA malware signatures:
    - File content scanning
    - Multiple rule support
    - Binary pattern matching
  - ✅ ML-based anomaly detection:
    - Isolation Forest algorithm
    - Event type-specific models
    - Automatic feature extraction
  - ✅ Alert management:
    - Rich HTML email notifications
    - Webhook integrations for custom systems
    - Slack integration with formatted messages
    - Discord integration with embeds
    - Telegram bot notifications
    - Severity-based routing

- **Modern Dashboard & UI** 🔄
  - ✅ Next.js 14 frontend with App Router
  - ✅ Real-time data visualization with Tremor
  - ✅ Dark/Light mode support
  - ✅ Responsive design for all devices
  - ✅ Interactive security events management
  - ✅ Real-time threat analytics
  - ✅ User settings and preferences
  - ✅ Interactive analytics dashboard:
    - Log volume trends and patterns
    - Source distribution analysis
    - Real-time security events
    - System health monitoring
  - ✅ Advanced features:
    - Log search with filters
    - Security incident timeline
    - Alert management system
    - System configuration
  - ✅ Beautiful UI components:
    - Smooth animations
    - Interactive charts
    - Real-time updates
    - Modern card layouts

- **SOAR Capabilities** ✅
  - ✅ Automated response playbooks:
    - YAML-based playbook definitions
    - Flexible trigger conditions
    - Action chaining and orchestration
    - Timeout and error handling
  - ✅ Integration with:
    - TheHive:
      - Automated case creation
      - Alert correlation
      - Evidence management
    - Cortex:
      - Threat intelligence analysis
      - File and URL scanning
      - IOC enrichment
    - Ansible:
      - Network device automation
      - System configuration
      - Security control automation
  - ✅ Custom Python automation:
    - Custom module support
    - Async function execution
    - Rich context passing

## 🚀 Innovation Features

- 🆓 **Freemium Model**: Open-source core with optional enterprise cloud add-ons
- 🎯 **No-Code Rule Editor**: Create SIEM rules without deep security expertise
- 🤖 **AI-Powered Analysis**: GPT-based suspicious log entry analysis
- 🎯 **Threat Assessment**: MITRE ATT&CK-based attacker risk analysis
- ⚡ **Automated Response**: Integrated SOAR capabilities

## 🔧 Technology Stack

- **Frontend**: React, Next.js
- **Backend**: Node.js, FastAPI
- **Storage**: Elasticsearch/OpenSearch/ClickHouse
- **Queue**: Kafka/RabbitMQ/NATS
- **Monitoring**: Prometheus, Grafana
- **Deployment**: Docker, Kubernetes, Helm

## 🔌 API & Integration

- REST & GraphQL APIs
- Multi-tenant support
- OpenTelemetry compatibility
- Extensive third-party integration support

## 🚀 Getting Started

### Quick Start

1. Clone the repository
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start required services:
   ```bash
   docker-compose up -d
   ```
5. Run the collector and processor:
   ```bash
   # Terminal 1: Run the collector
   python -m uvicorn libreSIEM.collector.collector:app --host 0.0.0.0 --port 8000

   # Terminal 2: Run the processor
   python -m libreSIEM.processor
   ```

### API Usage

1. Get an access token:
   ```bash
   curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"
   ```

2. Ingest a single log event:
   ```bash
   curl -X POST "http://localhost:8000/ingest" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"source": "test", "event_type": "test", "data": {"message": "test"}}'
   ```

3. Ingest raw logs:
   LibreSIEM supports multiple log formats out of the box:

   **Apache Combined Log Format**:
   ```bash
   curl -X POST "http://localhost:8000/ingest/raw" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "source": "apache",
       "format": "apache_combined",
       "log_line": "127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326 \"http://www.example.com/start.html\" \"Mozilla/4.08 [en] (Win98; I ;Nav)\""
     }'
   ```

   **Syslog Format**:
   ```bash
   curl -X POST "http://localhost:8000/ingest/raw" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "source": "syslog",
       "format": "syslog",
       "log_line": "Feb  5 12:23:09 myhost program[123]: Sample log message"
     }'
   ```

   **JSON Format**:
   ```bash
   curl -X POST "http://localhost:8000/ingest/raw" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "source": "app",
       "format": "json",
       "log_line": "{\"timestamp\": \"2024-02-05T12:23:09Z\", \"level\": \"info\", \"message\": \"Sample log\"}"
     }'
   ```

4. Query logs from Elasticsearch:
   ```bash
   # Get all logs
   curl -X GET "http://localhost:9200/logs-*/_search" \
     -H "Content-Type: application/json" \
     -d '{"query": {"match_all": {}}}'

   # Search by source
   curl -X GET "http://localhost:9200/logs-*/_search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": {
         "term": {
           "source.keyword": "apache"
         }
       }
     }'

   # Search by time range
   curl -X GET "http://localhost:9200/logs-*/_search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": {
         "range": {
           "timestamp": {
             "gte": "now-1h",
             "lte": "now"
           }
         }
       }
     }'
   ```

### Architecture

LibreSIEM follows a modular, event-driven architecture:

1. **Collector Service**:
   - REST API with JWT authentication and rate limiting
   - Multi-format log parsing (Syslog, Apache, JSON)
   - Kafka producer for reliable message delivery
   - Input validation and sanitization

2. **Processor Service**:
   - Consumes logs from Kafka
   - Enriches logs with additional context
   - Handles timestamp normalization
   - Stores logs in Elasticsearch

3. **Storage Layer**:
   - Monthly index rotation for efficient data management
   - Structured mappings for optimized search
   - Support for hot/warm/cold architectures

### Configuration

LibreSIEM is configured through environment variables:

```bash
# Collector Service
COLLECTOR_HOST=0.0.0.0
COLLECTOR_PORT=8000

# Kafka Settings
KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
RAW_LOGS_TOPIC=raw_logs
KAFKA_CLIENT_ID_PREFIX=libresiem
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# Redis (Rate Limiting)
REDIS_URL=redis://localhost:6379

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Elasticsearch
ES_HOSTS=http://localhost:9200
ES_USERNAME=elastic
ES_PASSWORD=changeme
ES_SSL_VERIFY=true
ES_INDEX_PREFIX=libresiem
```

### Data Model

1. **Log Event Structure**:
   ```json
   {
     "timestamp": "2025-02-05T12:23:09+01:00",
     "source": "apache",
     "event_type": "log",
     "data": {
       "remote_host": "127.0.0.1",
       "request": "GET /apache_pb.gif HTTP/1.0",
       "status": 200
     },
     "enriched": {
       "processing_timestamp": "2025-02-05T12:23:09+01:00"
     }
   }
   ```

2. **Index Pattern**: `logs-YYYY.MM`
   - Monthly rotation for efficient data management
   - Automatic mapping for common fields
   - Support for dynamic fields in `data` object

## 📦 Deployment

- Docker Compose and Kubernetes Helm Charts available
- CI/CD integration with GitHub Actions/GitLab CI
- Built-in monitoring with Prometheus & Grafana

## ⚠️ Known Issues

### Testing
- **Azure Integration Tests**: The Azure integration tests are currently skipped due to difficulties in mocking the Azure SDK's async context managers. This needs to be fixed by properly mocking the `query_workspace` method's async context manager behavior.

## 👥 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE)

## 📞 Support

- GitHub Issues: For bug reports and feature requests
- Documentation: [Coming Soon]
- Community Forum: [Coming Soon]