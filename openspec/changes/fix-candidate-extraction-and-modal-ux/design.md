# Design: Fix Candidate Extraction & Modal UX

## Kiến trúc tổng thể

```
Upload PDF/DOCX
      │
      ▼
 file_parser.py           ← Fix Bug #1: x_tolerance + text normalization
 ┌─────────────────────────────────────────────────────┐
 │  extract_text(x_tolerance=1.5)  [WAS: 3]            │
 │  + _normalize_text() post-processing                 │
 └─────────────────────────────────────────────────────┘
      │ raw_text + column_texts
      ▼
 candidate_extractor.py   ← Fix Bug #2 & #3
 ┌─────────────────────────────────────────────────────┐
 │  _parse_candidate_subcontents()  ← Fix date-first   │
 │  _extract_educations()           ← Fix school=date  │
 │  _extract_basic_info()           ← Fix summary mix  │
 │  _extract_objective()            ← Better detection │
 └─────────────────────────────────────────────────────┘
      │ profile_json
      ▼
 CandidateDetailModal.jsx  ← Fix Bug #4: fixed height
 ┌─────────────────────────────────────────────────────┐
 │  h-[85vh] min-h-[600px]  [WAS: max-h-[90vh] only]  │
 │  Sidebar: overflow-y-auto (scroll independently)    │
 │  Content: overflow-y-auto (scroll independently)    │
 └─────────────────────────────────────────────────────┘
```

---

## Fix Chi Tiết

### Fix #1 — file_parser.py: Word-boundary loss

**Thay đổi 1: x_tolerance**
```python
# BEFORE (line 68):
raw_text = page.extract_text(x_tolerance=3, y_tolerance=3) or ""

# AFTER:
raw_text = page.extract_text(x_tolerance=1.5, y_tolerance=3) or ""
```
Lý do: `x_tolerance=1.5` phù hợp hơn với nhiều loại PDF tiếng Anh. Giá trị `3` quá lớn, merge các char gần nhau thành 1 token mà không có space.

**Thay đổi 2: Post-processing normalization**
Thêm function `_normalize_text(text: str) -> str` ngay sau khi extract:
- Detect chuỗi CamelCase bất thường (nhiều uppercase liên tiếp không có space) — dấu hiệu bị dính chữ
- Dùng regex để thêm space trước uppercase letter trong một số pattern nhất định
- Không dùng AI/LLM, chỉ dùng heuristic an toàn

```python
def _normalize_text(text: str) -> str:
    """Add spaces between words that got merged during PDF extraction."""
    # Pattern: lowercase immediately followed by uppercase (camelCase merge)
    # e.g. "designedAsync" → "designed Async"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Multiple spaces → single space
    text = re.sub(r' {2,}', ' ', text)
    return text
```

---

### Fix #2 — candidate_extractor.py: Education date-first bug

**Root cause cụ thể:**
CV tiếng Anh thường có format:
```
EDUCATION
2022 - 2026           ← line này là date, không phải tên trường!
Ho Chi Minh City University of Technology
Computer Science
```

Nhưng `_parse_candidate_subcontents()` hiện tại gán line đầu tiên vào `title` (kể cả khi nó là date), rồi tạo block mới.

**Fix trong `_parse_candidate_subcontents()`:**
Thêm điều kiện: nếu `current_block is None` và line chỉ là date (has_date=True và stripped của date range == toàn bộ line), thì buffer date đó, không tạo block mới với title=date.

```python
# Thêm biến pending_date để buffer date trước khi gặp title thực sự
pending_date = ""

# Trong vòng lặp:
if is_new_entry:
    if current_block is None and (has_date or has_year) and _is_pure_date_line(line):
        pending_date = line  # buffer, không tạo block
        continue
    current_block = {"title": line, "date": pending_date or "", "bullets": [], "raw_text": line}
    pending_date = ""
    blocks.append(current_block)
    if has_date or has_year:
        current_block["date"] = line if not pending_date else pending_date
```

**Helper function:**
```python
def _is_pure_date_line(line: str) -> bool:
    """True nếu line CHỈ chứa date range, không có text khác."""
    stripped = line.strip()
    # Remove date pattern
    without_date = re.sub(
        r'(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\d{4}|nay|present|now|hiện tại)',
        '', stripped, flags=re.IGNORECASE
    ).strip(' -–—')
    return len(without_date) < 5  # Còn lại < 5 ký tự → thuần date
```

---

### Fix #3 — candidate_extractor.py: Summary detection

**Vấn đề 3a: Tên trộn vào summary**

Trong `_extract_basic_info()`, orphan text không lọc được tên:
```python
# BEFORE: chỉ skip nếu line chứa email/phone/linkedin
# AFTER: thêm filter tên

full_name = info.get("full_name", "")
name_words = set(full_name.lower().split()) if full_name else set()

for line in header_lines:
    line_clean = line.strip()
    if not line_clean or len(line_clean) < 15:
        continue
    # Skip nếu line chủ yếu là tên ứng viên
    line_words = set(line_clean.lower().split())
    if name_words and len(name_words & line_words) / max(len(line_words), 1) > 0.5:
        continue
    # ... rest of filters
    orphan_text.append(line_clean)
```

**Vấn đề 3b: Miss summary khi không có section header**

Mở rộng fallback: nếu sau khi check `objective` section và orphan text, summary vẫn trống, thử detect block text dài đầu tiên trong `header` section:
```python
# Sau khi build orphan_text:
if not info["summary"]:
    # Fallback: tìm paragraph đầu tiên trong header đủ dài (> 50 chars)
    for line in header_lines:
        line_clean = line.strip()
        if len(line_clean) > 50 and ' ' in line_clean:
            # Không phải date, không phải URL, không phải chỉ contact info
            if not re.search(r'https?://|@|\+84|0[3-9]\d{8}', line_clean):
                info["summary"] = line_clean
                break
```

---

### Fix #4 — CandidateDetailModal.jsx: Fixed height

**Thay đổi modal container (line 102):**
```jsx
// BEFORE:
className="w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden rounded-2xl shadow-2xl animate-fade-up"

// AFTER:
className="w-full max-w-5xl h-[85vh] min-h-[600px] flex flex-col overflow-hidden rounded-2xl shadow-2xl animate-fade-up"
```

**Tại sao `h-[85vh]` thay vì `max-h`?**
- `max-h` → modal có thể nhỏ hơn → UX "trồi sụt"
- `h-[85vh]` → modal luôn chiếm 85% viewport height, content scroll bên trong
- `min-h-[600px]` → đảm bảo modal không quá nhỏ trên màn hình nhỏ

**Body layout đã đúng** (flex-grow + overflow-hidden), chỉ cần fix container height là đủ.

---

## Thứ tự implementation

1. **Fix #4** (Frontend, 5 phút, zero risk)
2. **Fix #2** (Backend, medium risk, cần test)
3. **Fix #3** (Backend, medium risk, cần test)
4. **Fix #1** (Backend parser, cần test nhiều loại PDF)

## Testing

Dùng 2 loại CV mẫu:
- `sample/` directory (nếu có) — CV tiếng Việt
- CV tiếng Anh dạng single column (Software Engineer.pdf từ screenshots)
- CV tiếng Anh dạng multi-column (Fresher Fullstack.pdf từ screenshots)
