from libreSIEM.config import Settings, KafkaSettings

def get_test_settings() -> Settings:
    """Get test settings"""
    return Settings(
        SERVICE_NAME="libreSIEM-test",
        LOG_LEVEL="DEBUG",
        RAW_LOGS_TOPIC="test_raw_logs",
        kafka=KafkaSettings(
            KAFKA_BOOTSTRAP_SERVERS="kafka:9092",
            KAFKA_CLIENT_ID_PREFIX="libresiem-test",
            KAFKA_SECURITY_PROTOCOL="PLAINTEXT"
        )
    )
