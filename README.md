# LibreSIEM 🛡️

A lightweight, cloud-native, open-source Security Information & Event Management (SIEM) system providing real-time log analysis, threat detection, and alerting capabilities. LibreSIEM is designed to be modular, scalable, and easy to integrate.

## 🌟 Key Features

- **Event Collection & Ingestion** 🔄
  - ✅ Basic Kafka support implemented
  - ✅ REST API with JWT authentication and rate limiting
  - ✅ Multi-format log parsing (Syslog, Apache, JSON)
  - ✅ Batch ingestion support
  - ⏳ Webhooks, Fluentd, and Filebeat support
  - ⏳ Agentless collection for cloud services (AWS, Azure, GCP)
  - ⏳ Support for firewalls, IDS/IPS, endpoints, Kubernetes, and VPNs
  - ⏳ Additional queue systems (RabbitMQ, NATS)

- **Data Processing & Storage** ⏳
  - ⏳ Elasticsearch/OpenSearch/ClickHouse for primary storage
  - ⏳ Cold storage support (S3, Google Cloud Storage, MinIO)
  - ⏳ Automated log deduplication, parsing, and threat intelligence enrichment

- **Threat Detection & Correlation**
  - Sigma Rules & YARA malware signature detection
  - ML-based anomaly detection (Scikit-Learn, TensorFlow, PyTorch)
  - Real-time alerts via Webhook, Slack, Discord, Telegram
  - SIEM integrations (Splunk, Sentinel, QRadar)

- **Modern Dashboard & UI** 🔄
  - ✅ FastAPI backend foundation
  - ⏳ React/Next.js frontend
  - ⏳ Advanced visualization with Grafana/Kibana

- **SOAR Capabilities**
  - Automated response playbooks
  - Integration with TheHive, Cortex, Ansible, SaltStack
  - Python-based automation scripts

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
5. Run the collector:
   ```bash
   python -m uvicorn libreSIEM.collector.collector:app --host 0.0.0.0 --port 8000
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

3. Ingest raw logs (supports Syslog, Apache Combined, and JSON formats):
   ```bash
   curl -X POST "http://localhost:8000/ingest/raw" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"source": "apache", "log_line": "127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326", "format": "apache_combined"}'
   ```

### Configuration

LibreSIEM is highly configurable through environment variables. Key configuration areas:

- **Kafka Settings**: Configure brokers, security, and topics
- **Redis Settings**: Configure connection for rate limiting
- **JWT Settings**: Configure secret key and token expiration
- **Service Settings**: Configure ports, hosts, and logging

Key environment variables:
```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
RAW_LOGS_TOPIC=raw_logs

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📦 Deployment

- Docker Compose and Kubernetes Helm Charts available
- CI/CD integration with GitHub Actions/GitLab CI
- Built-in monitoring with Prometheus & Grafana

## 👥 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE)

## 📞 Support

- GitHub Issues: For bug reports and feature requests
- Documentation: [Coming Soon]
- Community Forum: [Coming Soon]