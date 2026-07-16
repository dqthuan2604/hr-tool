import os
from minio import Minio
import io

client = Minio(
    "127.0.0.1:9002",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
print("MinIO buckets:", client.list_buckets())

client.put_object(
    "hr-tool-uploads",
    "test.txt",
    io.BytesIO(b"Hello World"),
    11,
    content_type="text/plain"
)
print("Upload done")
