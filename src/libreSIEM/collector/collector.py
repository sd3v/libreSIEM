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
import os
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

# Initialize Redis for rate limiting
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

# Initialize rate limiter with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}"
)

# Rate limit configuration per endpoint
INGEST_RATE_LIMIT = "1000/minute"  # 1000 requests per minute
BATCH_RATE_LIMIT = "100/minute"    # 100 batch requests per minute
QUERY_RATE_LIMIT = "60/minute"     # 60 queries per minute

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

# Add CORS middleware with more restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)

@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check endpoint with rate limiting"""
    try:
        # Check Redis connection
        redis_client.ping()
        redis_status = "connected"
    except redis.ConnectionError:
        redis_status = "disconnected"
        
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "services": {
            "redis": redis_status,
            "kafka": "connected" if collector.producer else "disconnected"
        }
    }

@app.post("/token", response_model=Token)
@limiter.limit("5/minute")  # Limit login attempts
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Get access token for authentication with rate limiting."""
    # Track failed login attempts
    failed_attempts_key = f"failed_login:{form_data.username}"
    failed_attempts = redis_client.get(failed_attempts_key)
    
    if failed_attempts and int(failed_attempts) >= 5:
        # Lock out for 15 minutes after 5 failed attempts
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )
    
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        # Increment failed attempts
        redis_client.incr(failed_attempts_key)
        redis_client.expire(failed_attempts_key, 900)  # 15 minutes
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Clear failed attempts on successful login
    redis_client.delete(failed_attempts_key)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "scopes": user.scopes,
            "ip": request.client.host  # Include IP in token for additional security
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }



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
@limiter.limit(INGEST_RATE_LIMIT)
async def ingest_log(
    request: Request,
    event: LogEvent,
    current_user: User = Depends(get_current_active_user)
):
    """Ingest a log event into the SIEM system with rate limiting."""
    check_scope("logs:write", current_user)
    
    # Get user-specific rate limit key
    rate_limit_key = f"ingest_rate:{current_user.username}"
    
    try:
        # Check user-specific rate limit
        current_count = redis_client.incr(rate_limit_key)
        if redis_client.ttl(rate_limit_key) == -1:
            redis_client.expire(rate_limit_key, 60)  # 1 minute window
            
        user_limit = int(os.getenv(f"RATE_LIMIT_{current_user.username.upper()}", "1000"))
        if current_count > user_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="User rate limit exceeded"
            )
            
        # Process the log event
        success = await collector.process_event(event)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process event"
            )
        
        # Add rate limit headers to response
        response = {"status": "success", "message": "Event ingested successfully"}
        request.state.view_rate_limit = {
            "limit": user_limit,
            "remaining": max(0, user_limit - current_count),
            "reset": redis_client.ttl(rate_limit_key)
        }
        return response
        
    except Exception as e:
        logger.error(f"Error ingesting log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting log: {str(e)}"
        )

@app.post("/ingest/batch")
@limiter.limit(BATCH_RATE_LIMIT)
async def ingest_batch(
    request: Request,
    batch: BatchLogEvents,
    current_user: User = Depends(get_current_active_user)
):
    """Ingest multiple log events in a single request with rate limiting."""
    check_scope("logs:write", current_user)
    
    # Get user-specific rate limit keys
    batch_limit_key = f"batch_rate:{current_user.username}"
    event_count_key = f"event_count:{current_user.username}"
    
    try:
        # Check batch request rate limit
        current_batch_count = redis_client.incr(batch_limit_key)
        if redis_client.ttl(batch_limit_key) == -1:
            redis_client.expire(batch_limit_key, 60)  # 1 minute window
            
        # Check total events per minute limit
        current_event_count = redis_client.incrby(event_count_key, len(batch.events))
        if redis_client.ttl(event_count_key) == -1:
            redis_client.expire(event_count_key, 60)  # 1 minute window
            
        # Get user-specific limits
        user_batch_limit = int(os.getenv(f"BATCH_LIMIT_{current_user.username.upper()}", "100"))
        user_event_limit = int(os.getenv(f"EVENT_LIMIT_{current_user.username.upper()}", "10000"))
        
        if current_batch_count > user_batch_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Batch request rate limit exceeded"
            )
            
        if current_event_count > user_event_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Total event rate limit exceeded"
            )
            
        # Process the batch
        results = []
        successful_events = 0
        failed_events = []
        
        for event in batch.events:
            try:
                success = await collector.process_event(event)
                if success:
                    successful_events += 1
                    results.append({"status": "success", "event_id": id(event)})
                else:
                    failed_events.append({"event_id": id(event), "error": "Failed to process event"})
                    results.append({"status": "error", "event_id": id(event), "error": "Failed to process event"})
            except Exception as e:
                failed_events.append({"event_id": id(event), "error": str(e)})
                results.append({"status": "error", "event_id": id(event), "error": str(e)})
                
        # Add rate limit headers to response
        response = {
            "status": "completed",
            "results": results,
            "summary": {
                "total": len(batch.events),
                "successful": successful_events,
                "failed": len(failed_events)
            }
        }
        
        request.state.view_rate_limit = {
            "batch_limit": user_batch_limit,
            "batch_remaining": max(0, user_batch_limit - current_batch_count),
            "event_limit": user_event_limit,
            "event_remaining": max(0, user_event_limit - current_event_count),
            "reset": min(
                redis_client.ttl(batch_limit_key),
                redis_client.ttl(event_count_key)
            )
        }
        return response
        
    except Exception as e:
        logger.error(f"Error ingesting batch: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting batch: {str(e)}"
        )

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
