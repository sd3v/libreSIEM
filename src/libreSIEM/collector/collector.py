from fastapi import FastAPI, HTTPException, Depends
from libreSIEM.config import Settings
from pydantic import BaseModel
from confluent_kafka import Producer
import json
import logging
from datetime import datetime, UTC
from typing import Dict, Any, Optional
from libreSIEM.config import get_settings

# Settings will be injected via dependency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LibreSIEM Collector",
    description="Log collector service for LibreSIEM",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

class LogEvent(BaseModel):
    source: str
    event_type: str
    timestamp: Optional[datetime] = None
    data: Dict[str, Any]

class Collector:
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        kafka_config = self.settings.kafka.get_kafka_config(client_id_suffix="collector")
        # Add producer-specific configs
        kafka_config.update({
            'message.max.bytes': 1048576,  # 1MB
            'compression.type': 'gzip',
            'retries': 3,
            'retry.backoff.ms': 1000,
            'queue.buffering.max.messages': 100,
            'queue.buffering.max.kbytes': 1024  # 1MB
        })
        self.producer = Producer(kafka_config)
        logger.info("Collector initialized with Kafka connection")
        
        # Create the topic if it doesn't exist
        try:
            self.producer.poll(0)
            self.producer.produce(topic=self.settings.RAW_LOGS_TOPIC, value=b'test')
            self.producer.flush(5)
            logger.info(f"Successfully connected to Kafka and created topic '{settings.RAW_LOGS_TOPIC}'")
        except Exception as e:
            logger.warning(f"Initial Kafka connection test failed: {str(e)}. Will retry on first message.")

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    async def process_event(self, event: LogEvent) -> bool:
        try:
            # Add timestamp if not provided
            if not event.timestamp:
                event.timestamp = datetime.now(UTC)
            
            # Prepare event for Kafka - use the event data directly
            event_data = event.data
            event_data.update({
                "source": event.source,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat()
            })
            
            # Send to Kafka
            self.producer.produce(
                topic=self.settings.RAW_LOGS_TOPIC,
                key=str(event.source).encode('utf-8'),  # Use source as key for partitioning
                value=json.dumps(event_data).encode('utf-8'),
                callback=self.delivery_report
            )
            # Ensure message is delivered
            self.producer.poll(0)
            self.producer.flush(timeout=5.0)
            
            logger.info(f"Event processed successfully from source: {event.source}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

def get_collector(settings: Settings = Depends(get_settings)) -> Collector:
    return Collector(settings)

# Create a collector instance for direct use (e.g., health checks)
collector = Collector(get_settings())

@app.post("/ingest")
async def ingest_log(event: LogEvent):
    """Ingest a log event into the SIEM system"""
    # Use the global collector instance
    success = await collector.process_event(event)
    return {"status": "success", "message": "Event ingested successfully"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
