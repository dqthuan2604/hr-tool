# HR Tool MVP — Implementation Plan for AI Agent

## Meta

| Key | Value |
|---|---|
| Project | HR Tool MVP |
| Repo structure | Monorepo |
| Auth | None (skip for MVP) |
| Database | PostgreSQL |
| Backend | Python — FastAPI + SQLAlchemy + Alembic |
| Frontend | React (Vite) + TailwindCSS |
| CV Export | WeasyPrint (PDF), python-docx (DOCX) |
| LLM Fallback | Ollama local — Qwen2.5:1.5b |
| PDF parsing | pdfplumber (copyable PDF only, no scan) |
| DOCX parsing | python-docx |

---

## Repo Structure

```
hr-tool/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── template.py
│   │   │   └── candidate.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── template.py
│   │   │   └── candidate.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── templates.py
│   │   │   ├── candidates.py
│   │   │   └── generator.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── file_parser.py
│   │   │   ├── template_extractor.py
│   │   │   ├── candidate_extractor.py
│   │   │   ├── cv_renderer.py
│   │   │   ├── cv_exporter.py
│   │   │   └── llm_fallback.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── heuristics.py
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   ├── templates.js
│   │   │   ├── candidates.js
│   │   │   └── generator.js
│   │   ├── pages/
│   │   │   ├── TemplatePage.jsx
│   │   │   ├── CandidatePage.jsx
│   │   │   └── GeneratorPage.jsx
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── TemplateCard.jsx
│   │   │   ├── CandidateCard.jsx
│   │   │   ├── CVPreview.jsx
│   │   │   └── ExportBar.jsx
│   │   └── hooks/
│   │       └── useUpload.js
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Database Schema

```sql
-- templates table
CREATE TABLE templates (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(255) NOT NULL,
  source_file VARCHAR(255),
  schema_json JSONB NOT NULL,       -- sections, slots, styles
  preview_html TEXT,
  created_at  TIMESTAMP DEFAULT NOW()
);

-- candidates table
CREATE TABLE candidates (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_file  VARCHAR(255),
  raw_text     TEXT,
  profile_json JSONB NOT NULL,      -- basic_info, skills, work_experiences, educations, ...
  created_at   TIMESTAMP DEFAULT NOW()
);

-- cv_drafts table
CREATE TABLE cv_drafts (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id   UUID REFERENCES candidates(id),
  template_id    UUID REFERENCES templates(id),
  custom_json    JSONB,             -- user overrides on top of profile_json
  rendered_html  TEXT,
  created_at     TIMESTAMP DEFAULT NOW(),
  updated_at     TIMESTAMP DEFAULT NOW()
);
```

### Candidate profile_json schema

```json
{
  "basic_info": {
    "full_name": "",
    "email": "",
    "phone": "",
    "address": "",
    "linkedin": "",
    "website": "",
    "summary": ""
  },
  "skills": [
    { "category": "Backend", "items": ["Python", "FastAPI"] }
  ],
  "work_experiences": [
    {
      "company": "",
      "role": "",
      "start_date": "",
      "end_date": "",
      "description": ""
    }
  ],
  "educations": [
    {
      "school": "",
      "degree": "",
      "major": "",
      "start_date": "",
      "end_date": "",
      "gpa": ""
    }
  ],
  "certifications": [
    { "name": "", "issuer": "", "date": "" }
  ],
  "languages": [
    { "language": "", "level": "" }
  ],
  "projects": [
    { "name": "", "description": "", "tech_stack": [], "url": "" }
  ]
}
```

### Template schema_json schema

```json
{
  "layout": "single-column",
  "colors": {
    "primary": "#2D3748",
    "accent": "#3182CE",
    "background": "#FFFFFF",
    "text": "#1A202C"
  },
  "fonts": {
    "heading": { "family": "Arial", "size": 18, "weight": "bold" },
    "body": { "family": "Arial", "size": 11, "weight": "normal" }
  },
  "sections": [
    {
      "key": "basic_info",
      "label": "Header",
      "order": 1,
      "visible": true,
      "style": {}
    },
    {
      "key": "work_experiences",
      "label": "Kinh nghiệm làm việc",
      "order": 2,
      "visible": true,
      "style": {}
    }
  ]
}
```

---

## API Endpoints

```
# Templates
POST   /api/templates/upload        -- upload file → extract template
GET    /api/templates               -- list all templates
GET    /api/templates/{id}          -- get template detail
DELETE /api/templates/{id}

# Candidates
POST   /api/candidates/upload       -- upload CV → extract candidate data
GET    /api/candidates              -- list all candidates
GET    /api/candidates/{id}         -- get candidate detail
PUT    /api/candidates/{id}         -- update profile_json manually
DELETE /api/candidates/{id}

# Generator
POST   /api/generator/render        -- { candidate_id, template_id, custom_json? } → rendered_html
POST   /api/generator/export/pdf    -- { draft_id or html } → PDF file
POST   /api/generator/export/docx   -- { draft_id or html } → DOCX file
POST   /api/generator/drafts        -- save draft
GET    /api/generator/drafts/{id}
PUT    /api/generator/drafts/{id}   -- update custom_json
```

---

## Phase Plan

---

### PHASE 0 — Project Bootstrap

**Goal:** Repo chạy được, BE connect DB, FE hiển thị trang trống, docker-compose up.

#### Task 0.1 — Init monorepo structure
- Tạo thư mục gốc `hr-tool/`
- Tạo `backend/` và `frontend/` theo cấu trúc đã định nghĩa ở trên
- Tạo `.gitignore` (node_modules, __pycache__, .env, *.pyc, dist/)
- Tạo `README.md` với hướng dẫn setup

#### Task 0.2 — Backend: khởi tạo FastAPI
- Tạo `backend/requirements.txt` với các package:
  ```
  fastapi==0.111.0
  uvicorn[standard]==0.29.0
  sqlalchemy==2.0.30
  alembic==1.13.1
  psycopg2-binary==2.9.9
  python-multipart==0.0.9
  pdfplumber==0.11.0
  pymupdf==1.24.3
  python-docx==1.1.2
  weasyprint==62.3
  jinja2==3.1.4
  spacy==3.7.4
  dateparser==1.2.0
  phonenumbers==8.13.37
  httpx==0.27.0
  python-dotenv==1.0.1
  ```
- Tạo `backend/app/main.py`:
  - FastAPI app instance
  - CORS middleware (allow origins: `http://localhost:5173`)
  - Include routers: templates, candidates, generator
  - Health check endpoint `GET /health` → `{"status": "ok"}`
- Tạo `backend/app/config.py`:
  - Load từ `.env`: `DATABASE_URL`, `UPLOAD_DIR`, `OLLAMA_URL`
- Tạo `backend/app/database.py`:
  - SQLAlchemy engine, SessionLocal, Base
  - Dependency `get_db()`
- Tạo `backend/.env.example`:
  ```
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hr_tool
  UPLOAD_DIR=./uploads
  OLLAMA_URL=http://localhost:11434
  ```

#### Task 0.3 — Backend: SQLAlchemy models
- Tạo `backend/app/models/template.py`:
  - Model `Template` với các cột theo schema DB ở trên
  - Dùng `JSONB` từ `sqlalchemy.dialects.postgresql`
- Tạo `backend/app/models/candidate.py`:
  - Model `Candidate`
- Tạo `backend/app/models/cv_draft.py`:
  - Model `CVDraft` với FK đến Candidate và Template
- Tạo `backend/app/models/__init__.py`: import all models

#### Task 0.4 — Backend: Alembic setup
- Chạy `alembic init alembic` trong `backend/`
- Sửa `alembic/env.py`: import `Base` từ `app.models`, set `target_metadata = Base.metadata`
- Sửa `alembic.ini`: set `sqlalchemy.url` đọc từ env
- Tạo migration đầu tiên: `alembic revision --autogenerate -m "init tables"`
- **Không chạy migrate** — để Agent chạy sau khi có DB

#### Task 0.5 — Backend: Pydantic schemas
- Tạo `backend/app/schemas/template.py`:
  - `TemplateCreate`, `TemplateResponse`
- Tạo `backend/app/schemas/candidate.py`:
  - `CandidateCreate`, `CandidateResponse`, `CandidateUpdate`
- Tạo `backend/app/schemas/cv_draft.py`:
  - `CVDraftCreate`, `CVDraftResponse`, `CVDraftUpdate`
- Tạo `backend/app/schemas/generator.py`:
  - `RenderRequest` (`candidate_id`, `template_id`, `custom_json?`)
  - `ExportRequest` (`draft_id`)

#### Task 0.6 — Frontend: Vite + React init
- Trong `frontend/`: init Vite project với template React
- Cài dependencies:
  ```
  npm install axios react-router-dom
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```
- Config `tailwind.config.js`: content paths đến `./src/**/*.{js,jsx}`
- Tạo `frontend/src/api/` với 3 file (`templates.js`, `candidates.js`, `generator.js`) — mỗi file export axios instance với baseURL `http://localhost:8000/api`
- Tạo `frontend/src/App.jsx` với React Router:
  - `/templates` → `TemplatePage`
  - `/candidates` → `CandidatePage`
  - `/generator` → `GeneratorPage`
  - redirect `/` → `/templates`
- Tạo 3 page placeholder rỗng

#### Task 0.7 — Docker Compose
- Tạo `docker-compose.yml`:
  ```yaml
  services:
    postgres:
      image: postgres:16-alpine
      environment:
        POSTGRES_DB: hr_tool
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
      ports:
        - "5432:5432"
      volumes:
        - pgdata:/var/lib/postgresql/data

    backend:
      build: ./backend
      ports:
        - "8000:8000"
      depends_on:
        - postgres
      env_file:
        - ./backend/.env
      volumes:
        - ./backend:/app

    frontend:
      build: ./frontend
      ports:
        - "5173:5173"
      volumes:
        - ./frontend:/app

  volumes:
    pgdata:
  ```
- Tạo `backend/Dockerfile` và `frontend/Dockerfile`

**Checkpoint Phase 0:** `docker-compose up` → `GET /health` trả 200, FE load trang trắng với router.

---

### PHASE 1 — Module ①: Template Creator

**Goal:** Upload file CV → extract layout → lưu template vào DB → hiển thị danh sách template.

#### Task 1.1 — File parser service
- Tạo `backend/app/services/file_parser.py`:
  - Function `parse_file(file_path: str) -> dict`:
    - Nếu `.pdf`: dùng `pdfplumber.open()`, extract từng page: `page.chars`, `page.words`, `page.rects`
    - Nếu `.docx`: dùng `python_docx.Document()`, extract paragraphs với style info
    - Return: `{ "type": "pdf|docx", "pages": [...], "raw_chars": [...] }`
  - Function `save_upload(file: UploadFile) -> str`: lưu file vào `UPLOAD_DIR`, return path

#### Task 1.2 — Template extractor service
- Tạo `backend/app/services/template_extractor.py`:
  - Function `extract_template_schema(parsed: dict) -> dict`:
    - **Heuristic 1 — Section headers:** char `size > median_size * 1.3` VÀ (`bold == True` OR `color != body_color`) → đây là header
    - **Heuristic 2 — Layout detection:** kiểm tra `x0` của text blocks, nếu có 2 cụm x rõ ràng → `two-column`, không thì `single-column`
    - **Heuristic 3 — Color extraction:** lấy 3 màu xuất hiện nhiều nhất từ `chars`
    - **Heuristic 4 — Font info:** group chars theo `fontname`, lấy `size` phổ biến nhất làm body font
    - Map các header text sang section keys chuẩn: `["kinh nghiệm", "work experience"] → "work_experiences"`, tương tự cho các section khác
    - Return: `schema_json` theo cấu trúc đã định nghĩa
  - Function `generate_preview_html(schema_json: dict) -> str`:
    - Render Jinja2 template `templates/cv_preview.html` với schema để tạo preview rỗng

#### Task 1.3 — LLM fallback cho template
- Tạo `backend/app/services/llm_fallback.py`:
  - Function `detect_sections_with_llm(raw_text: str) -> list[dict]`:
    - Gọi Ollama: `POST http://OLLAMA_URL/api/generate`
    - Model: `qwen2.5:1.5b`
    - Prompt yêu cầu trả JSON list sections: `[{"key": "work_experiences", "label": "...", "order": 1}]`
    - Parse response, validate JSON
    - Trigger khi heuristic detect < 2 sections
  - Function `_call_ollama(prompt: str, schema: dict) -> dict`: helper gọi Ollama với structured output

#### Task 1.4 — Template router
- Tạo `backend/app/routers/templates.py`:
  - `POST /api/templates/upload`:
    - Nhận `UploadFile`
    - Gọi `save_upload()` → `parse_file()` → `extract_template_schema()`
    - Nếu sections < 2: gọi LLM fallback
    - Lưu vào DB, return `TemplateResponse`
  - `GET /api/templates`: return list
  - `GET /api/templates/{id}`: return detail
  - `DELETE /api/templates/{id}`: xóa DB record + file

#### Task 1.5 — Jinja2 template HTML
- Tạo `backend/app/templates/cv_preview.html`:
  - Jinja2 template render preview rỗng của CV (chỉ layout, không có data)
  - Dùng CSS variables từ `schema_json.colors`
  - Render từng section theo `schema_json.sections` theo `order`

#### Task 1.6 — Frontend: Template page
- Tạo `frontend/src/components/FileUpload.jsx`:
  - Drag-and-drop + click to upload
  - Accept: `.pdf, .docx`
  - Hiển thị loading spinner khi đang upload
  - Hiển thị error message nếu upload fail
- Tạo `frontend/src/components/TemplateCard.jsx`:
  - Hiển thị: tên template, số sections, preview thumbnail (nếu có), nút Delete
- Cập nhật `frontend/src/pages/TemplatePage.jsx`:
  - Layout: upload zone bên trên, grid template cards bên dưới
  - Gọi `GET /api/templates` khi mount
  - Sau khi upload thành công → refetch list

**Checkpoint Phase 1:** Upload 1 file CV PDF → BE trả về `schema_json` → hiển thị card template trên FE.

---

### PHASE 2 — Module ②: Data Extractor

**Goal:** Upload CV → extract thông tin ứng viên có cấu trúc → lưu vào DB → hiển thị profile.

#### Task 2.1 — Candidate extractor service
- Tạo `backend/app/services/candidate_extractor.py`:
  - Function `extract_candidate_profile(parsed: dict) -> dict`:
    - Gọi `_extract_basic_info()`, `_extract_skills()`, `_extract_work_experiences()`, `_extract_educations()`, `_extract_certifications()`, `_extract_languages()`, `_extract_projects()`
    - Merge kết quả thành `profile_json`
    - Return `profile_json`

  - Function `_extract_basic_info(text: str) -> dict`:
    - Email: regex `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
    - Phone: dùng `phonenumbers.parse()` với region hint `VN`
    - LinkedIn: regex `linkedin\.com/in/[\w-]+`
    - Website: regex `https?://[^\s]+`
    - Full name: line đầu tiên của CV (thường là tên), hoặc line có font lớn nhất từ `parsed`
    - Summary: đoạn text ngay sau tên nếu không có section header

  - Function `_extract_skills(text_blocks: list) -> list`:
    - Tìm section có label match `["skills", "kỹ năng", "technical skills"]`
    - Trong section đó: parse bullet points hoặc comma-separated items
    - Group theo category nếu có sub-heading
    - Return `[{ "category": "...", "items": [...] }]`

  - Function `_extract_work_experiences(text_blocks: list) -> list`:
    - Tìm section `["work experience", "kinh nghiệm", "experience"]`
    - Mỗi entry: detect company (thường in đậm), role (italic hoặc dòng tiếp), dates dùng `dateparser.parse()`
    - Description: các dòng còn lại trong entry
    - Return list

  - Function `_extract_educations(text_blocks: list) -> list`:
    - Tương tự work experience, tìm section `["education", "học vấn", "trình độ"]`

  - Function `_extract_certifications(text_blocks: list) -> list`
  - Function `_extract_languages(text_blocks: list) -> list`
  - Function `_extract_projects(text_blocks: list) -> list`

  - Function `_find_section_text(text_blocks: list, section_keys: list[str]) -> list`:
    - Helper: tìm blocks thuộc về 1 section cụ thể, dựa trên header detection

#### Task 2.2 — LLM fallback cho candidate extraction
- Trong `llm_fallback.py` thêm:
  - Function `extract_field_with_llm(text_chunk: str, field: str) -> any`:
    - Trigger khi regex/NER trả về empty hoặc low confidence
    - Prompt: `"Extract {field} from this CV text. Return JSON only: {...}"`
    - Dùng `qwen2.5:1.5b`
  - Function `extract_full_profile_with_llm(raw_text: str) -> dict`:
    - Fallback toàn bộ nếu extraction thủ công fail nặng
    - Prompt trả về toàn bộ `profile_json`

#### Task 2.3 — Candidate router
- Tạo `backend/app/routers/candidates.py`:
  - `POST /api/candidates/upload`:
    - Nhận `UploadFile`
    - Gọi `save_upload()` → `parse_file()` → `extract_candidate_profile()`
    - Confidence check: nếu `basic_info.email` rỗng VÀ `work_experiences` rỗng → gọi LLM fallback
    - Lưu DB, return `CandidateResponse`
  - `GET /api/candidates`: return list (chỉ trả basic_info, không trả full profile)
  - `GET /api/candidates/{id}`: return full profile
  - `PUT /api/candidates/{id}`: nhận `CandidateUpdate`, merge vào `profile_json`, save
  - `DELETE /api/candidates/{id}`

#### Task 2.4 — Frontend: Candidate page
- Tạo `frontend/src/components/CandidateCard.jsx`:
  - Hiển thị: avatar placeholder với initials, tên, email, số năm kinh nghiệm (tính từ work_experiences)
  - Badge skills (3 cái đầu)
  - Nút "Xem chi tiết" + "Xóa"
- Tạo `frontend/src/components/CandidateDetailModal.jsx`:
  - Modal hiển thị toàn bộ `profile_json` theo sections
  - Mỗi field có thể edit inline (input/textarea)
  - Nút Save → gọi `PUT /api/candidates/{id}`
- Cập nhật `frontend/src/pages/CandidatePage.jsx`:
  - Layout giống TemplatePage: upload zone + grid cards
  - Open modal khi click "Xem chi tiết"

**Checkpoint Phase 2:** Upload CV → BE extract đúng email, tên, ít nhất 1 work experience → hiển thị CandidateCard trên FE.

---

### PHASE 3 — Module ③: CV Generator

**Goal:** Chọn ứng viên + template → render CV → edit inline → export PDF/DOCX.

#### Task 3.1 — CV renderer service
- Tạo `backend/app/services/cv_renderer.py`:
  - Function `render_cv(candidate: Candidate, template: Template, custom_json: dict = None) -> str`:
    - Merge `candidate.profile_json` với `custom_json` (custom override có priority)
    - Load Jinja2 Environment từ `backend/app/templates/`
    - Render template `cv_full.html` với data đã merge
    - Return HTML string
  - Tạo `backend/app/templates/cv_full.html`:
    - Jinja2 template nhận `profile`, `schema` (từ template)
    - Render từng section theo `schema.sections` với `section.order`
    - Dùng CSS inline từ `schema.colors`, `schema.fonts`
    - Support `single-column` và `two-column` layout
    - CSS phải self-contained (WeasyPrint không load external resources)

#### Task 3.2 — CV exporter service
- Tạo `backend/app/services/cv_exporter.py`:
  - Function `export_pdf(html: str) -> bytes`:
    - Dùng `weasyprint.HTML(string=html).write_pdf()`
    - Return bytes
  - Function `export_docx(profile_json: dict, schema_json: dict) -> bytes`:
    - Dùng `python_docx.Document()`
    - Tạo document theo `schema_json.sections` và `schema_json.fonts`
    - Fill data từ `profile_json`
    - Save vào `io.BytesIO()`, return bytes
  - Lưu ý: DOCX export không đẹp bằng PDF nhưng đủ dùng cho MVP

#### Task 3.3 — Generator router
- Tạo `backend/app/routers/generator.py`:
  - `POST /api/generator/render`:
    - Body: `{ "candidate_id": UUID, "template_id": UUID, "custom_json": {} }`
    - Load candidate + template từ DB
    - Gọi `render_cv()`
    - Tạo/update `CVDraft` trong DB
    - Return: `{ "draft_id": UUID, "html": "..." }`
  - `POST /api/generator/export/pdf`:
    - Body: `{ "draft_id": UUID }`
    - Load draft, gọi `export_pdf(draft.rendered_html)`
    - Return `FileResponse` với `content-type: application/pdf`
  - `POST /api/generator/export/docx`:
    - Body: `{ "draft_id": UUID }`
    - Load draft + candidate + template từ DB
    - Gọi `export_docx()`
    - Return `FileResponse` với `content-type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `PUT /api/generator/drafts/{id}`:
    - Body: `{ "custom_json": {} }`
    - Re-render CV với custom_json mới, update draft

#### Task 3.4 — Frontend: Generator page
- Tạo `frontend/src/components/CVPreview.jsx`:
  - Nhận `html: string` prop
  - Render qua `<iframe srcDoc={html}>` với `sandbox="allow-same-origin"`
  - CSS: full height, border, shadow nhẹ
- Tạo `frontend/src/components/ExportBar.jsx`:
  - 2 nút: "Export PDF" và "Export DOCX"
  - Gọi API, nhận blob, trigger download qua `URL.createObjectURL()`
- Cập nhật `frontend/src/pages/GeneratorPage.jsx`:
  - Layout 3 cột:
    - Cột trái (25%): dropdown chọn candidate + dropdown chọn template + nút "Generate"
    - Cột giữa (50%): `CVPreview` hiển thị rendered HTML
    - Cột phải (25%): panel edit custom fields (optional overrides) + `ExportBar`
  - Flow:
    1. Chọn candidate → load từ `GET /api/candidates`
    2. Chọn template → load từ `GET /api/templates`
    3. Click "Generate" → `POST /api/generator/render` → update CVPreview
    4. Edit fields → debounce 800ms → `PUT /api/generator/drafts/{id}` → re-render
    5. Click Export → download file

**Checkpoint Phase 3:** Chọn candidate + template → CV render đúng → download được PDF.

---

### PHASE 4 — Polish & Integration

**Goal:** Fix edge cases, UX nhỏ, error handling đầy đủ.

#### Task 4.1 — Error handling toàn bộ BE
- Tạo custom exception handlers trong `main.py`:
  - `404` khi không tìm thấy resource
  - `422` khi file không đúng format
  - `500` với message rõ ràng, không leak traceback ra client
- Validate file trước khi process: check MIME type, max size 10MB

#### Task 4.2 — Upload UX
- Hiển thị progress bar khi upload file lớn (dùng axios `onUploadProgress`)
- Hiển thị skeleton loading cho cards khi đang fetch
- Toast notification khi upload thành công/thất bại

#### Task 4.3 — Candidate edit improvements
- Trong CandidateDetailModal: thêm button "Add section entry" cho work_experiences, educations, projects
- Validate email format trước khi save

#### Task 4.4 — CV Preview improvements
- Thêm zoom in/out cho CVPreview iframe
- Nút "Reset về mặc định" để xóa custom_json

#### Task 4.5 — Seed data
- Tạo `backend/scripts/seed.py`:
  - Insert 2 template mẫu (schema_json cứng, không cần upload file)
  - Insert 1 candidate mẫu (profile_json cứng)
  - Dùng để test nhanh Generator mà không cần qua Module 1, 2

---

## Thứ tự triển khai

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4

Trong từng phase: BE tasks trước → FE tasks sau → Checkpoint test
```

---

## Lưu ý quan trọng cho Agent

1. **pdfplumber** trả `chars` là list dict với keys: `text`, `fontname`, `size`, `bold`, `x0`, `y0`, `x1`, `y1`, `color`. Dùng `page.extract_text()` để lấy raw text nhanh.

2. **WeasyPrint** yêu cầu CSS phải inline hoặc embedded `<style>` — không load file CSS ngoài. Tất cả font phải là web-safe hoặc embed base64.

3. **Jinja2** trong FastAPI: khởi tạo `Jinja2Templates(directory="app/templates")` một lần trong `main.py`, inject qua dependency.

4. **JSONB** trong SQLAlchemy: dùng `from sqlalchemy.dialects.postgresql import JSONB` và type `JSONB` cho column. Khi query: `candidate.profile_json["basic_info"]["email"]`.

5. **File download** từ FE: dùng pattern sau:
   ```js
   const res = await axios.post(url, body, { responseType: 'blob' });
   const href = URL.createObjectURL(res.data);
   const a = document.createElement('a'); a.href = href; a.download = 'cv.pdf'; a.click();
   URL.revokeObjectURL(href);
   ```

6. **Ollama**: phải chạy local `ollama serve` và đã pull model `qwen2.5:1.5b`. Gọi qua `httpx.AsyncClient` async.

7. **CORS**: trong FastAPI set `allow_origins=["http://localhost:5173"]`, `allow_methods=["*"]`, `allow_headers=["*"]`.

8. **UUID**: dùng `from uuid import uuid4` và `default=uuid4` trong SQLAlchemy model. Trong Pydantic schema dùng `UUID` type từ `uuid`.

9. **Alembic**: chạy `alembic upgrade head` sau khi có DB. Mỗi khi thêm model column mới: `alembic revision --autogenerate -m "description"` rồi `alembic upgrade head`.

10. **spaCy model**: sau khi install spacy, cần `python -m spacy download en_core_web_sm`. Nếu cần tiếng Việt: `python -m spacy download vi_core_news_sm`. Nên download trong Dockerfile.