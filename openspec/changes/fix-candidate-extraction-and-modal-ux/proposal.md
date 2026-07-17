# Proposal: Fix Candidate Extraction & Modal UX

## Vấn đề hiện tại (What & Why)

Sau quá trình sử dụng thực tế, phát hiện 4 bugs ảnh hưởng trực tiếp đến trải nghiệm và chất lượng dữ liệu của Feature Ứng Viên (Candidate):

### Bug 1: CV tiếng Anh bị dính chữ (Word-boundary loss)
Khi upload CV PDF tiếng Anh, nội dung bị mất khoảng trắng giữa các từ:
```
# Kết quả sai:
AudioAIProcessing: DesignedasyncmixingpipelinewithFastAPI
# Kết quả đúng:
Audio AI Processing: Designed async mixing pipeline with FastAPI
```
**Root cause:** `file_parser.py` dùng `pdfplumber.extract_text(x_tolerance=3)` — ngưỡng quá cao, nhiều PDF tiếng Anh với font spacing nhỏ không được nhận ra word boundary.

### Bug 2: Phần Học vấn detect sai field
Trường **Trường** và **Chuyên ngành** bị điền bằng năm (e.g., `2022`, `2026`):
```
TRƯỜNG: 2022       CHUYÊN NGÀNH: 2026
THỜI GIAN BĐ: 2022  THỜI GIAN KT: 2026
```
**Root cause:** Trong `_parse_candidate_subcontents()`, line date-only (`"2022 - 2026"`) bị gán vào `title`→`school` thay vì `date`. Phổ biến với CV tiếng Anh format: Date → School → Major.

### Bug 3: Phần Summary không detect được trong một số trường hợp
Summary bị bỏ sót hoặc bị trộn với tên ứng viên.
**Root cause:** Orphan text fallback trong `_extract_basic_info()` không lọc bỏ tên ứng viên. Nếu objective keyword không khớp chính xác, summary bị miss hoàn toàn.

### Bug 4: Modal height ứng viên không cố định (Bad UX)
Modal **Chi tiết Hồ sơ** thay đổi chiều cao theo content của từng section tab — gây hiệu ứng "trồi sụt" khó chịu.
**Root cause:** Modal container dùng `max-h-[90vh]` nhưng không có `min-height` cố định.

## Phạm vi thay đổi (Scope)

### Backend — `file_parser.py`
- Giảm `x_tolerance` từ `3` xuống `1.5`
- Thêm post-processing `_normalize_text()` để handle word-boundary còn sót

### Backend — `candidate_extractor.py`
- Fix `_parse_candidate_subcontents()`: detect "date-first" block, không dùng date làm title
- Fix `_extract_educations()`: skip title nếu chỉ là date range
- Cải thiện `_extract_basic_info()` + `_extract_objective()`:
  - Lọc tên ứng viên khỏi orphan summary text
  - Mở rộng fallback detection khi không có section header rõ ràng

### Frontend — `CandidateDetailModal.jsx`
- Thêm `min-h-[600px]` vào modal body để giữ chiều cao cố định
- Sidebar + content area dùng `overflow-y-auto` scroll đúng trong vùng cố định

## Không nằm trong phạm vi (Out of Scope)
- LLM fallback cho candidate extraction
- Redesign UI modal
- Xử lý scan/image PDF
- Thay đổi database schema

## Thứ tự ưu tiên
Bug 4 (nhanh, CSS) → Bug 2 (data quality critical) → Bug 3 (summary detection) → Bug 1 (parser improvement)
