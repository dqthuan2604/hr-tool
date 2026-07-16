# Proposal: Fix Upload Flow Bugs (Pending Fetch / Worker Disconnect)

## Vấn đề hiện tại (What & Why)

Sau khi khảo sát toàn bộ luồng upload CV, phát hiện **2 bugs nghiêm trọng** blocking toàn bộ tính năng upload:

### Bug 1: Celery Worker không kết nối được Redis (ROOT CAUSE chính)

```
[ERROR] consumer: Cannot connect to redis://redis:6379/0: Timeout connecting to server.
```

**Root cause:** File `backend/.env` chứa các URL sử dụng `localhost` thay vì Docker service names:

| Biến | Giá trị trong `.env` (SAI) | Giá trị đúng cho Docker |
|------|---------------------------|------------------------|
| `DATABASE_URL` | `postgresql://...@localhost:5432/...` | `postgresql://...@postgres:5432/...` |
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://redis:6379/0` |
| `MINIO_ENDPOINT` | `localhost:9000` | `minio:9002` |

Khi container `worker` load `env_file: ./backend/.env`, nó resolve `localhost` là chính nó → không tìm thấy Redis → toàn bộ Celery task queue bị block.

**Hệ quả downstream:**
- Template upload: POST `/api/templates/upload` trả job_id nhưng task không bao giờ chạy
- SSE stream `/api/templates/upload/{id}/stream` hang mãi → frontend thấy "Pending" trong Network tab
- MinIO upload fail vì port sai (9000 vs 9002)

### Bug 2: Thiếu healthcheck → race condition khi khởi động

Khi `docker compose up`, `worker` và `backend` start trước khi Redis/Postgres thực sự sẵn sàng nhận kết nối.

### Bug 3: `minio_client` được khởi tạo global lúc import

Trong `storage.py`, `minio_client` được tạo ở module-level với env var có thể chưa set đúng lúc import.

## Phạm vi thay đổi (Scope)

### Fix 1: Sửa `backend/.env` — URL services (CRITICAL)
- Đổi tất cả `localhost` → Docker service names
- Sửa MinIO port từ `9000` → `9002`

### Fix 2: Cải thiện `docker-compose.yml` — healthcheck & depends_on
- Thêm `healthcheck` cho `redis` và `postgres`
- Cập nhật `depends_on` của `backend` và `worker` dùng `condition: service_healthy`
- Xóa service `minio` khỏi `depends_on` của `backend` (không cần healthcheck cho minio)

### Fix 3: Loại bỏ xung đột `env_file` vs `environment` trong compose
- Trong `docker-compose.yml`, bỏ `env_file` khỏi `worker` (chỉ giữ `environment` block)
- Giữ `env_file` cho `backend` nhưng đảm bảo `environment` override đúng

## Không nằm trong phạm vi (Out of Scope)
- Thay đổi logic bóc tách CV
- Thêm tính năng mới
- Auth/RBAC

## Độ ưu tiên
**CRITICAL** — Toàn bộ tính năng template upload và candidate upload đều broken.
