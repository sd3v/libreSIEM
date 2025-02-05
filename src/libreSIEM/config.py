from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional
from functools import lru_cache
import os

class KafkaSettings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CLIENT_ID_PREFIX: str = "libresiem"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_SASL_MECHANISM: Optional[str] = None
    KAFKA_SASL_USERNAME: Optional[str] = None
    KAFKA_SASL_PASSWORD: Optional[str] = None
    KAFKA_SSL_CAFILE: Optional[str] = None
    KAFKA_SSL_CERTFILE: Optional[str] = None
    KAFKA_SSL_KEYFILE: Optional[str] = None
    
    def get_kafka_config(self, client_id_suffix: str = "") -> Dict[str, Any]:
        config = {
            'bootstrap.servers': self.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': f"{self.KAFKA_CLIENT_ID_PREFIX}-{client_id_suffix}",
            'security.protocol': self.KAFKA_SECURITY_PROTOCOL,
            'message.timeout.ms': 30000,
            'socket.timeout.ms': 30000,
            'request.timeout.ms': 30000,
            'delivery.timeout.ms': 60000,
            'queue.buffering.max.ms': 5000,
            'reconnect.backoff.ms': 1000,
            'reconnect.backoff.max.ms': 10000,
            'enable.idempotence': True,
            'acks': 'all'
        }
        
        # Add SASL config if enabled
        if self.KAFKA_SASL_MECHANISM:
            config.update({
                'sasl.mechanism': self.KAFKA_SASL_MECHANISM,
                'sasl.username': self.KAFKA_SASL_USERNAME,
                'sasl.password': self.KAFKA_SASL_PASSWORD,
            })
            
        # Add SSL config if enabled
        if self.KAFKA_SSL_CAFILE:
            config.update({
                'ssl.ca.location': self.KAFKA_SSL_CAFILE,
                'ssl.certificate.location': self.KAFKA_SSL_CERTFILE,
                'ssl.key.location': self.KAFKA_SSL_KEYFILE,
            })
            
        return config

class ElasticsearchSettings(BaseSettings):
    ES_HOSTS: str = "http://localhost:9200"
    ES_USERNAME: Optional[str] = None
    ES_PASSWORD: Optional[str] = None
    ES_SSL_VERIFY: bool = True
    ES_SSL_CA_FILE: Optional[str] = None
    ES_INDEX_PREFIX: str = "libresiem"

class Settings(BaseSettings):
    # Service configuration
    SERVICE_NAME: str = "libreSIEM"
    LOG_LEVEL: str = "INFO"
    
    # Component-specific settings
    COLLECTOR_HOST: str = "0.0.0.0"
    COLLECTOR_PORT: int = 8000
    RAW_LOGS_TOPIC: str = "raw_logs"
    ENRICHED_LOGS_TOPIC: str = "enriched_logs"
    ALERTS_TOPIC: str = "alerts"
    
    # Nested settings
    kafka: KafkaSettings = KafkaSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
