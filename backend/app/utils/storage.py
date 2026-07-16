import os
import io
from minio import Minio

# Tự động lấy từ biến môi trường (hoặc fallback về localhost)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9002")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "hr-tool-uploads")

# Khởi tạo client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def ensure_bucket_exists():
    """Tạo bucket nếu chưa tồn tại"""
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        minio_client.make_bucket(MINIO_BUCKET_NAME)

def upload_file_to_minio(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Upload file byte stream lên MinIO và trả về định dạng minio://bucket/filename"""
    ensure_bucket_exists()
    
    file_stream = io.BytesIO(file_bytes)
    length = len(file_bytes)
    
    minio_client.put_object(
        MINIO_BUCKET_NAME,
        filename,
        file_stream,
        length,
        content_type=content_type
    )
    
    return f"minio://{MINIO_BUCKET_NAME}/{filename}"

def download_file_from_minio(minio_uri: str, local_path: str):
    """Tải file từ MinIO về máy local (dùng cho Celery worker)"""
    if not minio_uri.startswith("minio://"):
        raise ValueError("URI không đúng định dạng minio://")
    
    # Loại bỏ "minio://" và split
    parts = minio_uri.replace("minio://", "").split("/", 1)
    if len(parts) != 2:
        raise ValueError("URI không chứa đủ bucket và filename")
        
    bucket_name, object_name = parts
    minio_client.fget_object(bucket_name, object_name, local_path)
