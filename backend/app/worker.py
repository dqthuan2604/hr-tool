import os
from celery import Celery

# Đọc REDIS_URL từ env vars được inject bởi Docker Compose
# Fallback về localhost khi chạy thủ công trên máy host
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "hr_tool_worker",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    # Celery 6.0 compatibility: explicit retry behavior on startup
    broker_connection_retry_on_startup=True,
)

# Auto-discover tasks in the services directory
celery_app.autodiscover_tasks(["app.services", "app.routers"])
