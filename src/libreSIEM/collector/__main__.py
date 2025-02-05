import uvicorn
from libreSIEM.collector.collector import app
from libreSIEM.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.COLLECTOR_HOST,
        port=settings.COLLECTOR_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
