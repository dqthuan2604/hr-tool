# Design: Phase 4 Polish, Debug & Integration

## 1. Database Migration (Alembic)
- Chạy lệnh `alembic init alembic`.
- Map `target_metadata = Base.metadata` trong `alembic/env.py`.
- Gom tất cả model vào `app/models/__init__.py`.
- Sinh file migration `alembic revision --autogenerate -m "init_tables"`.
- Run `alembic upgrade head`.

## 2. MinIO Storage Integration
- Cài `minio` python package (`pip install minio`).
- Tạo file `app/utils/storage.py` chứa class `MinioStorage`.
- **FastAPI Flow:** Endpoint upload file sẽ đẩy thẳng file vào bucket `hr-tool-uploads`. File path lưu vào cột `source_file` của DB dưới dạng `minio://bucket/filename`.
- **Celery Flow:** Khi Worker nhận `job`, nó sẽ check nếu file có prefix `minio://`, nó sẽ tải file đó từ bucket xuống thư mục `/tmp` rồi mới chạy quá trình extract.

## 3. Global Error Handling
- Trong `main.py`, định nghĩa các Exception Handler:
  - `@app.exception_handler(Exception)` -> catch `500`. Trả về `{"detail": "Internal server error", "error_code": "ERR_500"}` và ghi log traceback ra console (không leak ra API response).
  - `@app.exception_handler(RequestValidationError)` -> catch `422`. Trả về format đẹp hơn.
- Trong Router (ví dụ `templates.py`, `candidates.py`), validate `file.size` và `file.content_type` trước khi gọi Celery. Trả `400` nếu file > 10MB hoặc khác (pdf, docx).

## 4. Bỏ qua AI (LLM) nếu không cần thiết
- Logic hiện tại của `candidate_extractor.py`: Nếu không tìm thấy tên/email hoặc kinh nghiệm làm việc -> Mới gọi LLM.
- Ta sẽ thêm một cờ `DISABLE_LLM=True` trong `config.py` (hoặc `.env`) để cho phép tắt tạm thời Ollama. Nếu cờ này bật, ta cứ trả về dữ liệu rỗng nếu Heuristic fail, không làm treo máy (Pass thư viện trước).

## 5. HTML trong Backend & Font Chữ
- Như đã trả lời ở phần Explore, HTML phải ở Backend (Jinja2) vì để render PDF tĩnh (WeasyPrint) không phụ thuộc client.
- Vấn đề font: Thay vì yêu cầu OS cài font, trong `cv_full.html`, CSS `@import` Google Fonts là đủ để WeasyPrint tải font lúc xuất PDF. Việc này đã được thêm từ Phase 3. Ta sẽ chỉ audit lại để đảm bảo không lỗi CSS.
