# Design: Fix Upload Flow Bugs

## Kiến trúc hiện tại

```
docker-compose.yml
  ├── postgres
  ├── minio
  ├── redis
  ├── backend  ←── env_file: .env (localhost URLs) + environment (service names)
  └── worker   ←── env_file: .env (localhost URLs) + environment (service names)
                    ↑ .env được load TRƯỚC và chứa localhost → override environment fails
                    → worker.REDIS_URL = "redis://localhost:6379/0" (SAI)
```

## Giải pháp

### Fix 1: Sửa `backend/.env` (cho local dev không dùng Docker)

File `.env` dùng cho local development (chạy uvicorn thủ công). Khi dùng Docker Compose, các giá trị trong `environment:` block sẽ **override** `env_file:`. Tuy nhiên, cần đảm bảo `.env` có giá trị hợp lý cho cả hai môi trường.

**Giải pháp đơn giản nhất:** Tách `.env` thành 2 file:
- `backend/.env` → cho local dev (giữ localhost)
- Compose tự inject đúng service names qua `environment:` block

Hoặc **đơn giản hơn**: Xóa `env_file` khỏi worker trong compose — chỉ dùng `environment:` block.

### Fix 2: `docker-compose.yml` — loại bỏ `env_file` khỏi `worker`

```yaml
# TRƯỚC
worker:
  env_file:
    - ./backend/.env      # ← Load localhost URLs, ghi đè environment block
  environment:
    - REDIS_URL=redis://redis:6379/0   # ← Bị .env override mất

# SAU  
worker:
  # Không dùng env_file — chỉ dùng environment block trực tiếp
  environment:
    - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/hr_tool
    - REDIS_URL=redis://redis:6379/0
    - MINIO_ENDPOINT=minio:9002
    - MINIO_ACCESS_KEY=minioadmin
    - MINIO_SECRET_KEY=minioadmin
    - MINIO_SECURE=false
    - MINIO_BUCKET_NAME=hr-tool-uploads
    - DISABLE_LLM=true
```

> **Lưu ý quan trọng về precedence Docker Compose:**
> Khi cả `env_file` và `environment` cùng định nghĩa một key, `environment` THẮNG.
> Nhưng `.env` định nghĩa keys mà `environment` block KHÔNG định nghĩa (như DISABLE_LLM, MINIO_ACCESS_KEY) → chúng vẫn được load từ `.env` với giá trị localhost.

### Fix 3: Thêm healthcheck cho redis và postgres

```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    timeout: 5s
    retries: 5

redis:
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 5

backend:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
    minio:
      condition: service_started

worker:
  depends_on:
    redis:
      condition: service_healthy
    postgres:
      condition: service_healthy
```

## Files sẽ thay đổi

| File | Thay đổi |
|------|---------|
| `docker-compose.yml` | Thêm healthchecks, sửa worker env (bỏ env_file), cập nhật depends_on |
| `backend/.env` | Ghi chú rõ là dùng cho local dev; không dùng trong Docker |

## Không thay đổi

- Logic xử lý CV (candidate_extractor, file_parser)
- Frontend code
- Backend API endpoints
- Models và schemas
