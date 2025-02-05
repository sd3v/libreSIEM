from fastapi import FastAPI, HTTPException, Depends, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from libreSIEM.config import Settings, get_settings
from confluent_kafka import Producer
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import json
import logging
import redis
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .models import LogEvent, BatchLogEvents
from .parsers import LogParser
from .auth import (
    Token, User, fake_users_db, authenticate_user,
    create_access_token, get_current_active_user, check_scope,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Settings will be injected via dependency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="LibreSIEM Collector",
    description="Log collector service for LibreSIEM",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get access token for authentication."""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



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
        self.parser = LogParser()
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
            
            # Prepare event for Kafka - maintain event structure
            event_data = {
                "source": event.source,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data
            }
            
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
@limiter.limit("100/minute")
async def ingest_log(
    request: Request,
    event: LogEvent,
    current_user: User = Depends(get_current_active_user)
):
    """Ingest a log event into the SIEM system."""
    check_scope("logs:write", current_user)
    success = await collector.process_event(event)
    return {"status": "success", "message": "Event ingested successfully"}

@app.post("/ingest/batch")
@limiter.limit("10/minute")
async def ingest_batch(
    request: Request,
    batch: BatchLogEvents,
    current_user: User = Depends(get_current_active_user)
):
    """Ingest multiple log events in a single request."""
    check_scope("logs:write", current_user)
    results = []
    for event in batch.events:
        try:
            success = await collector.process_event(event)
            results.append({"status": "success", "event_id": id(event)})
        except Exception as e:
            results.append({"status": "error", "event_id": id(event), "error": str(e)})
    return {"status": "completed", "results": results}

class RawLogRequest(BaseModel):
    source: str
    log_line: str
    format: Optional[str] = None

@app.post("/ingest/raw")
@limiter.limit("100/minute")
async def ingest_raw_log(
    request: Request,
    raw_log: RawLogRequest = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """Ingest a raw log line, automatically detecting and parsing the format."""
    check_scope("logs:write", current_user)
    
    # Parse the log line
    success, data = collector.parser.parse_line(raw_log.log_line, raw_log.format)
    if not success:
        raise HTTPException(status_code=400, detail=data["error"])
    
    # Create and process event
    event = collector.parser.create_event(data, raw_log.source)
    success = await collector.process_event(event)
    return {"status": "success", "message": "Raw log ingested successfully"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
