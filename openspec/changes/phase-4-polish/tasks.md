# Tasks: Phase 4 Polish, Debug & Integration

- [x] **Task 1: Setup Alembic & Fix Database**
  - [x] Khởi tạo thư mục alembic `alembic init alembic`.
  - [x] Cập nhật `env.py` để trỏ vào `Base.metadata`.
  - [x] Chạy `alembic revision --autogenerate` để tạo migration file đầu tiên.
  - [x] Chạy `alembic upgrade head` để tạo các bảng `templates`, `candidates`, `cv_drafts` trong DB.

- [x] **Task 2: MinIO Integration**
  - [x] Thêm thư viện `minio` vào `requirements.txt`.
  - [x] Viết hàm `upload_file_to_minio` trong `backend/app/services/file_parser.py` hoặc tạo util storage riêng.
  - [x] Sửa endpoint POST `/api/templates/upload` và `/api/candidates/upload` để đẩy file vào MinIO và lưu DB đường dẫn dạng `minio://...`.
  - [x] Cập nhật Celery tasks (file parsing) để download file từ MinIO nếu gặp prefix `minio://`.

- [x] **Task 3: Global Error Handling & File Validation**
  - [x] Tạo file `app/utils/exceptions.py` chứa custom handlers cho 422, 500, 404.
  - [x] Nhúng handlers này vào `app/main.py`.
  - [x] Trong router upload, check `file.size` < 10MB và định dạng MIME.

- [x] **Task 4: Cờ tắt AI (Disable LLM Flag)**
  - [x] Thêm cờ cấu hình `DISABLE_LLM` trong `config.py` và lấy từ `.env`.
  - [x] Áp dụng vào luồng fallback của `candidate_extractor.py` (nếu cờ = True, chỉ return kết quả heuristic).

- [ ] **Task 5: Frontend UX Polish (Optional/Toast)**
  - [ ] Cập nhật Axios requests để bắn Error Toast ra UI thay vì chỉ hiện text.
  - [ ] Chạy thử nghiệm toàn luồng từ Upload -> Render -> Xuất PDF.
