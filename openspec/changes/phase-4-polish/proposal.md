# Proposal: Phase 4 Polish, Debug & Integration

## Vấn đề hiện tại (What & Why)
Chúng ta đã hoàn thành 3 module chính của MVP (Templates, Candidates, Generator). Tuy nhiên, qua quá trình Explore (Audit), chúng ta phát hiện một số điểm cần khắc phục và cải thiện:
1. **Lỗi Database Migration:** Quên khởi tạo bảng (Alembic) ở Phase 0 dẫn đến lỗi `relation "templates" does not exist` khi sử dụng app.
2. **Quản lý File (MinIO):** File upload hiện đang lưu local, rủi ro cao khi scale Worker. Cần chuyển hướng đẩy file trực tiếp vào MinIO.
3. **Error Handling Global:** Toàn bộ API Backend chưa có bẫy lỗi tập trung (422 validation, 500 internal server error, max file size...).
4. **HTML & Fonts trong Backend:** Cần làm rõ cấu trúc thư mục chứa file tĩnh/CSS (nếu có) để WeasyPrint render PDF mượt mà với font chuẩn.
5. **AI Local (Ollama):** Tạm thời "Pass", tập trung ưu tiên thuật toán Heuristic bóc tách chuẩn và ổn định trước, giảm mức độ phụ thuộc (hoặc bypass hoàn toàn) LLM ở phase này nếu Heuristic chạy tốt.

## Phạm vi thay đổi (Scope)
- Sửa lỗi DB ngay lập tức bằng việc thiết lập Alembic Migration đúng chuẩn.
- Cấu hình lại cơ chế lưu trữ file: FastAPI đẩy thẳng lên MinIO bucket, lưu S3 URL vào DB, Celery download từ S3 URL.
- Cài đặt Global Exception Handlers ở `main.py` để xử lý Exception, chặn file rác hoặc file quá to.
- Tinh giản giao diện Upload (hiển thị lỗi đẹp bằng Toast).

## Không nằm trong phạm vi (Out of Scope)
- Tính năng phân quyền (Auth/RBAC).
- Nâng cấp model LLM.
