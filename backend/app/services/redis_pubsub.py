import json
import redis.asyncio as aioredis
import redis
from app import config

# Async client for FastAPI SSE
redis_client = aioredis.from_url(config.REDIS_URL, decode_responses=True)

async def publish_job_progress(job_id: str, status: str, message: str, payload: dict = None):
    data = {
        "status": status,
        "message": message,
        "payload": payload or {}
    }
    await redis_client.publish(f"job_progress_{job_id}", json.dumps(data))
    
def publish_job_progress_sync(job_id: str, status: str, message: str, payload: dict = None):
    """Used by Celery synchronous worker tasks"""
    sync_redis = redis.from_url(
        config.REDIS_URL,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5
    )
    data = {
        "status": status,
        "message": message,
        "payload": payload or {}
    }
    sync_redis.publish(f"job_progress_{job_id}", json.dumps(data))
