from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka import Producer
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LibreSIEM Collector")

class LogEvent(BaseModel):
    source: str
    event_type: str
    timestamp: Optional[datetime] = None
    data: Dict[str, Any]

class Collector:
    def __init__(self, kafka_bootstrap_servers: str = "localhost:9092"):
        self.producer = Producer({
            'bootstrap.servers': kafka_bootstrap_servers,
            'client.id': 'libresiem-collector',
            'message.timeout.ms': 5000,
            'socket.timeout.ms': 5000,
            'request.timeout.ms': 5000,
            'delivery.timeout.ms': 10000,
            'queue.buffering.max.ms': 2000,
            'reconnect.backoff.ms': 1000,
            'reconnect.backoff.max.ms': 10000
        })
        logger.info("Collector initialized with Kafka connection")
        
        # Create the topic if it doesn't exist
        try:
            self.producer.poll(0)
            self.producer.produce('raw_logs', value=b'test')
            self.producer.flush(5)
            logger.info("Successfully connected to Kafka and created topic 'raw_logs'")
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
                event.timestamp = datetime.utcnow()
            
            # Prepare event for Kafka
            event_data = {
                "source": event.source,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data
            }
            
            # Send to Kafka
            self.producer.produce(
                'raw_logs',
                json.dumps(event_data).encode('utf-8'),
                callback=self.delivery_report
            )
            self.producer.poll(0)
            
            logger.info(f"Event processed successfully from source: {event.source}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

collector = Collector()

@app.post("/ingest")
async def ingest_log(event: LogEvent):
    """
    Ingest a log event into the SIEM system
    """
    success = await collector.process_event(event)
    return {"status": "success", "message": "Event ingested successfully"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
