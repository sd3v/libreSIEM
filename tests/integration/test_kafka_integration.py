import pytest
import json
from datetime import datetime, UTC
from confluent_kafka import Producer, Consumer, KafkaError
from fastapi.testclient import TestClient
import time
from typing import Generator

@pytest.fixture
def kafka_consumer() -> Generator[Consumer, None, None]:
    """Create a Kafka consumer for testing"""
    consumer = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'test-consumer-group',
        'auto.offset.reset': 'earliest',
        'session.timeout.ms': 60000,  # Increased timeout
        'max.poll.interval.ms': 300000,  # Increased poll interval
        'fetch.max.bytes': 1048576,  # 1MB
        'fetch.message.max.bytes': 1048576,  # 1MB
        'max.partition.fetch.bytes': 1048576,  # 1MB
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 1000,
        'enable.partition.eof': False  # Don't treat partition EOF as error
    })
    
    # Wait for Kafka to be ready with exponential backoff
    max_retries = 10
    retry_delay = 1
    for retry in range(max_retries):
        try:
            consumer.subscribe(['test_raw_logs'])
            # Test connection
            consumer.poll(timeout=5.0)  # Increased poll timeout
            break
        except Exception as e:
            if retry == max_retries - 1:
                raise Exception(f"Failed to connect to Kafka after {max_retries} retries: {e}")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 10)  # Exponential backoff capped at 10s
    
    yield consumer
    
    try:
        consumer.close()
    except Exception:
        pass  # Ignore errors during cleanup

def test_message_delivery(client: TestClient, kafka_consumer: Consumer):
    """Test end-to-end message delivery to Kafka"""
    # Clear any existing messages with timeout
    start_clear = time.time()
    while time.time() - start_clear < 10:  # 10 second timeout for clearing
        msg = kafka_consumer.poll(0.5)
        if msg is None:
            break
        
    # Send test event
    test_event = {
        "source": "integration-test",
        "event_type": "kafka-test",
        "timestamp": datetime.now(UTC).isoformat(),
        "data": {
            "test_id": "test-1",
            "message": "Integration test message"
        }
    }
    
    # Send event and verify response
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200, f"Failed to send event: {response.text}"
    
    # Wait for and verify message in Kafka with increased timeout
    message = None
    start_time = time.time()
    timeout = 60  # Increased timeout to 60 seconds
    
    while time.time() - start_time < timeout:
        try:
            msg = kafka_consumer.poll(5.0)  # Increased poll timeout
            
            if msg is None:
                continue
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                pytest.fail(f"Kafka error: {msg.error()}")
            
            message = json.loads(msg.value().decode('utf-8'))
            if message['data']['test_id'] == 'test-1':
                break
                
        except Exception as e:
            pytest.fail(f"Error processing message: {e}")
    
    assert message is not None, f"No message received after {timeout} seconds"
    assert message['source'] == 'integration-test', "Incorrect message source"
    assert message['event_type'] == 'kafka-test', "Incorrect event type"
    assert message['data']['test_id'] == 'test-1', "Incorrect test ID"

def test_batch_message_delivery(client: TestClient, kafka_consumer: Consumer):
    """Test batch message delivery to Kafka"""
    # Clear any existing messages
    while kafka_consumer.poll(0.1) is not None:
        pass
        
    # Send a single test event first to verify basic functionality
    event = {
        "source": "integration-test",
        "event_type": "kafka-batch-test",
        "timestamp": datetime.now(UTC).isoformat(),
        "data": {
            "test_id": "batch-0",
            "message": "Batch test message 0"
        }
    }
    response = client.post("/ingest", json=event)
    assert response.status_code == 200
    
    # Wait for the first message to be processed
    time.sleep(1)
    
    # Send second test event
    event = {
        "source": "integration-test",
        "event_type": "kafka-batch-test",
        "timestamp": datetime.now(UTC).isoformat(),
        "data": {
            "test_id": "batch-1",
            "message": "Batch test message 1"
        }
    }
    response = client.post("/ingest", json=event)
    assert response.status_code == 200
    
    # Verify messages in Kafka
    received_messages = set()
    start_time = time.time()
    while len(received_messages) < 2 and time.time() - start_time < 10:
        msg = kafka_consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            assert False, f"Kafka error: {msg.error()}"
        
        message = json.loads(msg.value().decode('utf-8'))
        if message['event_type'] == 'kafka-batch-test':
            received_messages.add(message['data']['test_id'])
            
        # Clear message from memory
        del message
        del msg
    
    assert len(received_messages) == 2
    assert all(f"batch-{i}" in received_messages for i in range(2))

def test_large_message_delivery(client: TestClient, kafka_consumer: Consumer):
    """Test delivery of large messages to Kafka"""
    # Create a moderately large test event (~ 10KB)
    large_data = {f"key_{i}": "x" * 10 for i in range(100)}
    test_event = {
        "source": "integration-test",
        "event_type": "kafka-large-test",
        "timestamp": datetime.now(UTC).isoformat(),
        "data": large_data
    }
    
    # Clear any existing messages
    while kafka_consumer.poll(0.1) is not None:
        pass
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200
    
    # Verify message in Kafka
    message = None
    start_time = time.time()
    while time.time() - start_time < 10:
        msg = kafka_consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            assert False, f"Kafka error: {msg.error()}"
        
        message = json.loads(msg.value().decode('utf-8'))
        if message['event_type'] == 'kafka-large-test':
            break
    
    assert message is not None
    assert message['source'] == 'integration-test'
    assert message['event_type'] == 'kafka-large-test'
    assert len(message['data']) == 100
