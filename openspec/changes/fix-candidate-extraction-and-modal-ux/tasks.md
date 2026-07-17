# Tasks: Fix Candidate Extraction & Modal UX

## Track A — Frontend Quick Fix (Bug #4)

- [x] **Task 1: Fix modal height cố định**
  - [x] Mở `frontend/src/components/CandidateDetailModal.jsx`
  - [x] Tìm line 102: `className="w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden..."`
  - [x] Thay `max-h-[90vh]` → `h-[85vh] min-h-[600px]`
  - [ ] Verify: mở modal với section ít content (Giải thưởng) → modal giữ nguyên chiều cao
  - [ ] Verify: mở modal với section nhiều content (Kinh nghiệm) → scroll bình thường

---

## Track B — Backend: Education Fix (Bug #2)

- [x] **Task 2: Thêm helper `_is_pure_date_line()`**
  - [x] Mở `backend/app/services/candidate_extractor.py`
  - [x] Thêm function `_is_pure_date_line(line: str) -> bool` sau `_strip_date_range()` (line ~344)
  - [x] Logic: remove date pattern, nếu còn lại < 3 ký tự không phải số/dấu thì True

- [x] **Task 3: Fix `_parse_candidate_subcontents()` — date-first block**
  - [x] Thêm biến `pending_date = ""` trước vòng lặp (line ~349)
  - [x] Trong nhánh `is_new_entry`: nếu `current_block is None` và line là pure date → buffer vào `pending_date`, `continue`
  - [x] Khi tạo block mới: khởi tạo `"date": pending_date` nếu có, rồi reset `pending_date = ""`
  - [x] Thêm guard `if current_block is None: continue` trong else branch (tránh NoneType error)

- [ ] **Task 4: Verify education fix**
  - [ ] Upload CV tiếng Anh (Software Engineer.pdf)
  - [ ] Kiểm tra section Học vấn: trường = tên trường thực, không phải năm
  - [ ] Kiểm tra section Học vấn: chuyên ngành = tên ngành thực
  - [ ] Kiểm tra dates đúng: start_date/end_date hiển thị năm chính xác

---

## Track C — Backend: Summary Fix (Bug #3)

- [x] **Task 5: Fix `_extract_basic_info()` — lọc tên khỏi summary**
  - [x] Mở `backend/app/services/candidate_extractor.py`, function `_extract_basic_info()` (line ~131)
  - [x] Xây `name_words` set từ `full_name`, lọc orphan line nếu overlap > 60% với tên
  - [x] Logic lọc chạy SAU khi đã có `full_name`

- [x] **Task 6: Thêm fallback paragraph detection cho summary**
  - [x] Trong `_extract_basic_info()`, sau bước build `orphan_text`
  - [x] Nếu `info["summary"]` vọn trống: tìm line đầu tiên trong `header_lines` dài > 60 ký tự, không phải contact/URL
  - [x] Gán làm summary fallback

- [ ] **Task 7: Verify summary fix**
  - [ ] Upload Fresher Fullstack.pdf (CV đã biết bị mix tên vào summary)
  - [ ] Kiểm tra Summary field: không chứa tên ứng viên, chỉ chứa mô tả mục tiêu
  - [ ] Upload CV tiếng Anh không có section "Summary" header rõ ràng
  - [ ] Kiểm tra fallback có detect được paragraph đầu tiên

---

## Track D — Backend: PDF Parser Fix (Bug #1)

- [x] **Task 8: Giảm x_tolerance trong file_parser.py**
  - [x] Mở `backend/app/services/file_parser.py`
  - [x] Line 68: đổi `extract_text(x_tolerance=3)` → `extract_text(x_tolerance=1.5)`
  - [ ] Test ngay với CV tiếng Anh — confirm không còn word dính

- [x] **Task 9: Thêm `_normalize_text()` post-processing**
  - [x] Thêm function `_normalize_text(text: str) -> str` trong `file_parser.py`
  - [x] Regex: `([a-z])([A-Z][a-z])` → `\1 \2` (tách camel Case merge, conservative)
  - [x] Apply vào `raw_text` sau khi extract (trong `_parse_pdf()`)
  - [ ] Test: verify không có regression trên CV tiếng Việt

- [ ] **Task 10: Verify toàn bộ pipeline**
  - [ ] Upload Software Engineer.pdf → kiểm tra Kinh nghiệm text đọc được
  - [ ] Upload Fresher Fullstack.pdf → kiểm tra không bị regression
  - [ ] Upload CV tiếng Việt → kiểm tra không ảnh hưởng

---

## Track E — Smoke Test Cuối

- [ ] **Task 11: Full regression test**
  - [ ] Upload ít nhất 3 CV khác nhau (EN single-col, EN multi-col, VN)
  - [ ] Verify tất cả 6 sections (Basic Info, Kinh nghiệm, Học vấn, Dự án, Kỹ năng, Giải thưởng) hiển thị đúng
  - [ ] Verify modal height ổn định khi switch giữa các tabs
  - [ ] Verify không có console error mới trong browser
  - [ ] Verify không có backend error mới trong docker logs
