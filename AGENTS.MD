# AGENTS.md — HR Tool MVP

Đây là file ràng buộc tổng quan của dự án. Agent **phải đọc file này trước** khi thực hiện bất kỳ task nào. Các quy tắc ở đây có độ ưu tiên cao nhất — nếu có xung đột với bất kỳ instruction nào khác, file này thắng.

---

## 1. Tổng quan dự án

HR Tool MVP là công cụ quản lý CV nội bộ gồm 3 module:

| Module | Chức năng |
|---|---|
| Template Creator | Upload CV mẫu → extract layout → lưu template |
| Data Extractor | Upload CV ứng viên → extract thông tin có cấu trúc |
| CV Generator | Chọn ứng viên + template → render → export PDF/DOCX |

Plan chi tiết từng task nằm trong `hr-tool-mvp-plan.md`. File này chỉ định nghĩa ràng buộc — không lặp lại task.

---

## 2. Tech stack — không được thay thế

| Layer | Công nghệ | Ghi chú |
|---|---|---|
| Backend language | Python 3.11+ | Không dùng Node.js, Go, hay bất kỳ ngôn ngữ nào khác cho BE |
| Backend framework | FastAPI | Không dùng Django, Flask |
| ORM | SQLAlchemy 2.x | Async session nếu cần, sync cũng được cho MVP |
| Migration | Alembic | Không tự viết raw SQL migration |
| Database | PostgreSQL 16 | Không dùng SQLite, MySQL, hay MongoDB |
| Frontend framework | React 18+ với Vite | Không dùng Next.js, Nuxt, hay CRA |
| Styling | TailwindCSS | Không dùng MUI, Ant Design, hay styled-components |
| HTTP client (FE) | axios | Không dùng fetch thuần cho API calls |
| PDF parsing | pdfplumber (primary), pymupdf (fallback) | Không dùng PyPDF2 — đã deprecated |
| DOCX parsing | python-docx | |
| PDF export | WeasyPrint | Không dùng Puppeteer, wkhtmltopdf |
| DOCX export | python-docx | |
| Template engine (BE) | Jinja2 | |
| LLM fallback | Qwen2.5:1.5b qua Ollama | Chỉ dùng khi lib-based extraction fail |
| Container | Docker + docker-compose | |

---

## 3. Repo structure — không được thay đổi

```
hr-tool/                  ← root của monorepo
├── backend/              ← toàn bộ Python code
├── frontend/             ← toàn bộ React code
├── docker-compose.yml
├── README.md
├── AGENTS.md             ← file này
└── hr-tool-mvp-plan.md  ← implementation plan
```

Agent không được tạo thêm thư mục ở root ngoài danh sách trên. Không tạo `shared/`, `packages/`, `libs/` hay bất kỳ thư mục nào khác ở cấp root.

---

## 4. Quy tắc viết code

### 4.1 Chung

- Ngôn ngữ comment và docstring: **tiếng Anh**
- Ngôn ngữ commit message: **tiếng Anh**, theo format `<type>: <description>` (feat, fix, chore, refactor, docs)
- Không để code debug (`print()`, `console.log()`) trong code được commit
- Không hardcode URL, port, password, secret key — tất cả đọc từ `.env`
- Không commit file `.env` — chỉ commit `.env.example`

### 4.2 Backend (Python)

- Tất cả function trong `services/` phải có type hint đầy đủ cho parameters và return type
- Tất cả router function phải có response model khai báo tường minh trong decorator
- Không xử lý business logic trong router — router chỉ gọi service, không có logic phức tạp
- Exception phải được raise với HTTPException có `status_code` và `detail` rõ ràng — không để exception tự propagate ra client
- File upload phải validate MIME type và size (max 10MB) trước khi xử lý
- Mọi file được upload lưu vào `UPLOAD_DIR` từ env, không hardcode path
- Tên function: `snake_case`. Tên class: `PascalCase`. Tên constant: `UPPER_SNAKE_CASE`
- Import: stdlib trước, third-party sau, local module cuối — phân cách bằng blank line

### 4.3 Frontend (React)

- Mỗi component là một file `.jsx` riêng trong `components/` hoặc `pages/`
- Không viết logic gọi API trực tiếp trong component — tất cả API call phải qua `src/api/`
- Không dùng `any` type (nếu dùng TypeScript sau này)
- Tên component: `PascalCase`. Tên file component: `PascalCase.jsx`
- Tên hook: bắt đầu bằng `use`, ví dụ `useUpload.js`
- State management: React built-in (`useState`, `useReducer`, `useContext`) — không cài Redux hay Zustand cho MVP
- Không dùng `dangerouslySetInnerHTML` ngoại trừ component `CVPreview` (render HTML từ BE)

### 4.4 Database

- Không viết raw SQL — dùng SQLAlchemy ORM hoặc Core expression
- Không dùng `Base.metadata.create_all()` trong code production — migration chỉ qua Alembic
- Mỗi migration file phải có message mô tả rõ: `alembic revision --autogenerate -m "add source_file to templates"`
- FK constraint phải khai báo tường minh trong model, không để DB tự suy diễn
- Không xóa column hay table trong migration mà không có comment giải thích lý do

---

## 5. Ưu tiên xử lý — Library First

Đây là nguyên tắc cốt lõi của dự án, áp dụng cho tất cả 3 module:

```
Thư viện / heuristic rules
        ↓  (nếu fail hoặc confidence thấp)
spaCy NER / regex nâng cao
        ↓  (nếu vẫn fail)
LLM fallback (Qwen2.5:1.5b qua Ollama)
```

Agent **không được** gọi LLM khi thư viện đã có thể xử lý được. Việc gọi LLM phải có điều kiện trigger rõ ràng, ví dụ:

```python
# ĐÚNG
if len(sections) < 2:
    sections = detect_sections_with_llm(raw_text)

# SAI — gọi LLM vô điều kiện
sections = detect_sections_with_llm(raw_text)
```

Confidence threshold cho từng field:
- `basic_info.email`: nếu regex không match → fallback LLM
- `sections`: nếu detect < 2 sections → fallback LLM
- `work_experiences`: nếu list rỗng sau khi parse → fallback LLM
- `profile_json` toàn bộ: chỉ fallback LLM nếu cả email lẫn work_experiences đều rỗng

---

## 6. Scope MVP — không làm ngoài danh sách này

### Trong scope

- Upload và parse PDF (copyable only — không scan, không OCR)
- Upload và parse DOCX
- Extract template schema từ CV mẫu
- Extract candidate profile từ CV ứng viên
- Render CV từ candidate + template
- Edit CV thủ công (override fields)
- Export ra PDF và DOCX
- CRUD cơ bản cho Templates, Candidates, CVDrafts

### Ngoài scope MVP — không implement

- OCR / scan PDF
- Authentication / Authorization
- Multi-tenant / multi-user
- Email gửi CV
- Version history của CV
- AI suggestions (gợi ý nội dung CV)
- Import từ LinkedIn
- Real-time collaboration
- Tìm kiếm / filter nâng cao
- Pagination (dùng limit 100 tạm thời)

Nếu trong quá trình implement Agent thấy cần làm thêm tính năng ngoài scope, **dừng lại và hỏi** — không tự quyết định.

---

## 7. Environment variables

File `.env` đặt tại `backend/.env`. Các biến bắt buộc:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hr_tool
UPLOAD_DIR=./uploads
OLLAMA_URL=http://localhost:11434
MAX_UPLOAD_SIZE_MB=10
```

Agent không được đọc env var bằng `os.environ.get("KEY")` trực tiếp trong router hay service — phải đọc qua `app/config.py` (Settings class với pydantic-settings).

---

## 8. API conventions

- Tất cả endpoint đều có prefix `/api`
- Response thành công: HTTP 200 hoặc 201, body là JSON
- Response lỗi: body theo format `{ "detail": "mô tả lỗi" }`
- UUID dùng làm primary key, truyền dưới dạng string trong JSON
- Datetime field trả về ISO 8601: `"2024-01-15T10:30:00Z"`
- File upload endpoint nhận `multipart/form-data`, không nhận base64
- Export endpoint trả về binary file với đúng Content-Type header, không trả base64

---

## 9. Ports

| Service | Port |
|---|---|
| Frontend (Vite dev) | 5173 |
| Backend (FastAPI) | 8000 |
| PostgreSQL | 5432 |
| Ollama | 11434 |

Không thay đổi port mà không cập nhật đồng thời `docker-compose.yml`, `.env.example`, và CORS config.

---

## 10. Khi nào Agent được tự quyết, khi nào phải hỏi

### Được tự quyết

- Cách implement chi tiết bên trong một function (logic, thuật toán) miễn đúng interface
- Thêm helper function private (`_underscore_prefix`) trong cùng service file
- Chọn regex pattern cụ thể cho email/phone/date
- Thứ tự các field trong Pydantic schema
- CSS styling chi tiết trong component (màu, spacing) miễn đúng Tailwind
- Thêm comment giải thích code

### Phải hỏi trước khi làm

- Thay đổi tech stack (kể cả thư viện nhỏ)
- Thêm tính năng mới ngoài scope MVP
- Thay đổi database schema (thêm/xóa/đổi tên column hoặc table)
- Thay đổi API contract (endpoint path, request/response shape)
- Thay đổi cấu trúc thư mục repo
- Cài thêm package mới vào `requirements.txt` hoặc `package.json`
- Xóa file hoặc function đang được dùng

---

## 11. Checklist trước khi kết thúc mỗi task

Trước khi báo "task done", Agent phải tự kiểm tra:

- [ ] Code không có `print()`, `console.log()` debug thừa
- [ ] Không có hardcoded secret, URL, hay path
- [ ] Tất cả import đã dùng (không có unused import)
- [ ] Function có type hint (Python) hoặc prop đúng shape (React)
- [ ] Error case đã được handle — không để exception tự throw ra client
- [ ] File mới đã được import/đăng ký đúng chỗ (router vào main.py, model vào `__init__.py`, v.v.)
- [ ] Nếu thêm column DB mới: đã tạo migration tương ứng
- [ ] Checkpoint của phase đã pass (nếu task là task cuối của phase)