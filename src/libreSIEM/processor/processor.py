"""Log processor service for LibreSIEM."""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging
from confluent_kafka import Consumer, KafkaError, Message
from libreSIEM.config import Settings, get_settings
from libreSIEM.collector.models import LogEvent
from libreSIEM.processor.elasticsearch import ElasticsearchManager
from libreSIEM.processor.enrichment import EnrichmentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogProcessor:
    """Process logs from Kafka and store them in Elasticsearch."""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        
        # Initialize Kafka consumer
        kafka_config = self.settings.kafka.get_kafka_config(client_id_suffix="processor")
        kafka_config.update({
            'group.id': 'log_processor',
            'auto.offset.reset': 'earliest'
        })
        self.consumer = Consumer(kafka_config)
        self.consumer.subscribe([self.settings.RAW_LOGS_TOPIC])
        
        # Initialize Elasticsearch manager
        self.es_manager = ElasticsearchManager(settings)
        
        # Initialize enrichment processor
        self.enrichment_processor = EnrichmentProcessor(settings)
        
        logger.info("Log processor initialized")
    
    def _ensure_index(self):
        """Deprecated: Index management is now handled by ElasticsearchManager."""
        pass
    
    async def enrich_log(self, log_event: LogEvent) -> Dict[str, Any]:
        """Enrich a log event with additional context."""
        # Add timestamp if not present
        if not log_event.timestamp:
            log_event.timestamp = datetime.now()
        
        # Convert LogEvent to dictionary
        base_event = {
            'timestamp': log_event.timestamp.isoformat(),
            'source': log_event.source,
            'event_type': log_event.event_type,
            'data': log_event.data
        }
        
        if hasattr(log_event, 'vendor') and log_event.vendor:
            base_event['vendor'] = log_event.vendor
        
        # Apply enrichment processors
        enriched = await self.enrichment_processor.enrich_log(base_event)
        
        # If the event was deduplicated, return None
        if enriched is None:
            logger.debug(f"Dropping duplicate event from {log_event.source}")
            return None
        
        return enriched
    
    async def process_message(self, msg: Message) -> Optional[Dict[str, Any]]:
        """Process a single message from Kafka."""
        try:
            # Parse the message
            value = json.loads(msg.value().decode('utf-8'))
            log_event = LogEvent(**value)
            
            # Enrich the log
            enriched = await self.enrich_log(log_event)
            
            # Skip if the event was deduplicated
            if enriched is None:
                return None
            
            return enriched
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None
    
    def store_document(self, doc: Dict[str, Any]):
        """Store a document in Elasticsearch."""
        try:
            self.es_manager.store_document(doc)
        except Exception as e:
            logger.error(f"Error storing document in Elasticsearch: {str(e)}")
    
    async def run(self):
        """Run the processor loop."""
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Kafka error: {msg.error()}")
                    continue
                
                doc = self.process_message(msg)
                if doc:
                    self.store_document(doc)
                    
        except KeyboardInterrupt:
            logger.info("Shutting down")
        finally:
            self.consumer.close()

def main():
    """Main entry point."""
    processor = LogProcessor()
    processor.run()

if __name__ == "__main__":
    main()
