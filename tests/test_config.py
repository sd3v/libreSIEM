import pytest
from libreSIEM.config import Settings, KafkaSettings

def test_default_settings():
    """Test default settings"""
    settings = Settings()
    assert settings.SERVICE_NAME == "libreSIEM"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.COLLECTOR_PORT == 8000

def test_kafka_settings():
    """Test Kafka settings"""
    kafka_settings = KafkaSettings()
    config = kafka_settings.get_kafka_config("test")
    
    assert config['bootstrap.servers'] == "localhost:9092"
    assert config['client.id'] == "libresiem-test"
    assert config['security.protocol'] == "PLAINTEXT"

def test_kafka_ssl_settings():
    """Test Kafka SSL settings"""
    kafka_settings = KafkaSettings(
        KAFKA_SECURITY_PROTOCOL="SSL",
        KAFKA_SSL_CAFILE="/path/to/ca.pem",
        KAFKA_SSL_CERTFILE="/path/to/cert.pem",
        KAFKA_SSL_KEYFILE="/path/to/key.pem"
    )
    config = kafka_settings.get_kafka_config("test")
    
    assert config['security.protocol'] == "SSL"
    assert config['ssl.ca.location'] == "/path/to/ca.pem"
    assert config['ssl.certificate.location'] == "/path/to/cert.pem"
    assert config['ssl.key.location'] == "/path/to/key.pem"

def test_kafka_sasl_settings():
    """Test Kafka SASL settings"""
    kafka_settings = KafkaSettings(
        KAFKA_SECURITY_PROTOCOL="SASL_SSL",
        KAFKA_SASL_MECHANISM="PLAIN",
        KAFKA_SASL_USERNAME="user",
        KAFKA_SASL_PASSWORD="pass"
    )
    config = kafka_settings.get_kafka_config("test")
    
    assert config['security.protocol'] == "SASL_SSL"
    assert config['sasl.mechanism'] == "PLAIN"
    assert config['sasl.username'] == "user"
    assert config['sasl.password'] == "pass"
