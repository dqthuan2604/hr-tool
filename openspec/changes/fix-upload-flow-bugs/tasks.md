# Tasks: Fix Upload Flow Bugs

## Track A — Docker Compose Fix (CRITICAL — làm trước)

- [x] **Task 1: Sửa `docker-compose.yml` — worker không dùng env_file**
  - [x] Mở `docker-compose.yml`
  - [x] Xóa block `env_file: - ./backend/.env` khỏi service `worker`
  - [x] Thêm đầy đủ các biến môi trường vào `environment:` block của `worker`:
    - `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/hr_tool`
    - `REDIS_URL=redis://redis:6379/0`
    - `MINIO_ENDPOINT=minio:9002`
    - `MINIO_ACCESS_KEY=minioadmin`
    - `MINIO_SECRET_KEY=minioadmin`
    - `MINIO_SECURE=false`
    - `MINIO_BUCKET_NAME=hr-tool-uploads`
    - `DISABLE_LLM=true`

- [x] **Task 2: Thêm healthcheck cho `postgres` và `redis`**
  - [x] Thêm `healthcheck` block vào service `postgres`:
    ```yaml
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    ```
  - [x] Thêm `healthcheck` block vào service `redis`:
    ```yaml
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    ```

- [x] **Task 3: Cập nhật `depends_on` cho `backend` và `worker`**
  - [x] Sửa `depends_on` của `backend` sang dạng condition:
    ```yaml
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_started
    ```
  - [x] Sửa `depends_on` của `worker` sang dạng condition:
    ```yaml
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    ```

## Track B — .env annotation (cho local dev clarity)

- [x] **Task 4: Thêm comment vào `backend/.env` để rõ ràng hơn**
  - [x] Thêm header comment: `# ⚠️ Dùng cho local dev (uvicorn thủ công). Docker dùng docker-compose.yml environment block.`
  - [x] Thêm comment cho từng URL localhost để cảnh báo

## Track C — Verification

- [x] **Task 5: Restart và verify worker kết nối Redis thành công**
  - [x] Chạy: `docker compose down && docker compose up -d --build`
  - [x] Verify: `docker compose logs worker` hiển thị `[celery@... ready]` (không có ERROR)
  - [x] Verify: `docker compose ps` tất cả services đều `healthy` hoặc `Up`

- [ ] **Task 6: Test toàn bộ luồng upload Template**
  - [ ] Mở UI tại `http://localhost:5173/templates`
  - [ ] Upload 1 file PDF mẫu CV
  - [ ] Verify: spinner hiển thị progress (parsing → extracting → done)
  - [ ] Verify: không còn "Pending" trong Network tab
  - [ ] Verify: template xuất hiện trong danh sách sau khi xử lý xong

- [ ] **Task 7: Test toàn bộ luồng upload Candidate**
  - [ ] Mở UI tại `http://localhost:5173/candidates`
  - [ ] Upload 1 file PDF CV ứng viên
  - [ ] Verify: `POST /api/candidates/upload` trả về 200 với dữ liệu candidate
  - [ ] Verify: candidate xuất hiện trong danh sách
