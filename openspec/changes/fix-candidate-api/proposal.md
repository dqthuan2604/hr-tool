# Proposal: Fix Candidate API & Add Template Detail View

## Vấn đề hiện tại (What & Why)

Sau khi hệ thống được deploy lên Docker, phát hiện 2 bugs blocking:

### Bug 1: Candidate Upload 500 Error
Endpoint `POST /api/candidates/upload` luôn trả về `500 Internal Server Error`:
```
Error processing candidate: 'raw_text' is an invalid keyword argument for Candidate
```
**Root cause:** Router `candidates.py` truyền `raw_text=...` vào constructor model `Candidate`, nhưng model không có cột `raw_text` trong DB.

### Bug 2: Template Card thiếu action "Xem chi tiết"
Template card chỉ có nút Delete — không có cách xem dữ liệu đã bóc tách (sections, layout, schema_json). HR team không biết template phân tích tốt hay chưa.

## Phạm vi thay đổi (Scope)

### Backend
- Thêm cột `raw_text: TEXT` vào model `Candidate`
- Tạo Alembic migration thêm cột `raw_text` vào bảng `candidates` hiện có

### Frontend
- Thêm button "Xem chi tiết" trên `TemplateCard`
- Tạo `TemplateDetailModal` component hiển thị toàn bộ dữ liệu đã bóc tách:
  - Layout structure (columns)
  - Danh sách tất cả sections với label
  - Schema JSON (collapsible)
  - Metadata cơ bản (tên file, ngày tạo)

## Không nằm trong phạm vi (Out of Scope)
- UI redesign (xử lý ở change riêng `ui-dark-overhaul`)
- Thay đổi logic bóc tách template
- Auth/RBAC

## Độ ưu tiên
**HIGH** — Bug 1 blocking hoàn toàn tính năng Candidate, dẫn đến Generator không có data để test.
