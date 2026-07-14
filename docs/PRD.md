# Product Requirements Document (PRD)
## HR Tool — Hệ thống Hỗ trợ Tuyển dụng & Quản lý Hồ sơ Ứng viên

---

| Thông tin | Chi tiết |
|---|---|
| Tài liệu | Product Requirements Document (PRD) |
| Phiên bản | v1.0 |
| Ngày tạo | 2026-07-14 |
| Trạng thái | Draft |
| Tài liệu liên quan | [BRD.md](./BRD.md) · [HR-Tool-MVP-Implement-plan.md](../HR-Tool-MVP-Implement-plan.md) |

---

## 1. Tổng quan Sản phẩm

### 1.1. Vision

Biến HR Tool thành người trợ lý kỹ thuật số của chuyên viên tuyển dụng: **chỉ cần tải lên CV của ứng viên và mẫu CV của công ty, hệ thống sẽ tự động tạo ra hồ sơ chuẩn hóa sẵn sàng gửi cho khách hàng.**

### 1.2. Kiến trúc tổng quan

Hệ thống được xây dựng theo mô hình **Monorepo** với 3 lớp chính:

```
┌───────────────────────────────────────────┐
│         Frontend (React + Vite)            │
│      Giao diện người dùng trình duyệt      │
└───────────────────┬───────────────────────┘
                    │ HTTP/REST API
┌───────────────────▼───────────────────────┐
│      Backend API (Python / FastAPI)        │
│  Xử lý nghiệp vụ, trích xuất, render CV   │
└──────────┬─────────────────┬──────────────┘
           │                 │
┌──────────▼──────┐   ┌──────▼──────────────┐
│  PostgreSQL DB  │   │  AI Engine (Ollama)  │
│  Lưu trữ dữ liệu│   │  on-premise, local  │
└─────────────────┘   └─────────────────────┘
```

**Công nghệ cốt lõi:**
- **Backend:** Python / FastAPI — phục vụ REST API, xử lý tài liệu
- **Frontend:** React (Vite) + TailwindCSS — giao diện web
- **Cơ sở dữ liệu:** PostgreSQL — lưu templates, candidates, drafts
- **AI Hỗ trợ:** Ollama (local) với model `qwen2.5:1.5b` — fallback khi trích xuất heuristic thất bại
- **Xử lý tài liệu:** `pdfplumber` (PDF), `python-docx` (DOCX)
- **Xuất file:** `WeasyPrint` (PDF), `python-docx` (DOCX)
- **Triển khai:** Docker Compose

---

## 2. User Persona

> Hệ thống MVP phục vụ **duy nhất một nhóm người dùng: bộ phận HR nội bộ**. Không có phân quyền vai trò trong phạm vi này.

### Persona: Minh — Chuyên viên Tuyển dụng (HR)
- **Thói quen:** Xử lý 10–20 CV/ngày, gửi 3–5 hồ sơ chuẩn hóa cho khách hàng mỗi tuần.
- **Nỗi đau:** Mất 30–60 phút mỗi hồ sơ để copy-paste vào mẫu Word công ty. Thông tin hay bị sai sót khi chép tay.
- **Kỳ vọng:** Tải CV lên → hệ thống xử lý → có hồ sơ PDF đẹp trong 5 phút, có thể sửa trực tiếp trên web nếu cần, không cần học phần mềm phức tạp.

---

## 3. User Stories & Acceptance Criteria

### 3.1. Module A — Quản lý Mẫu CV (Template Creator)

---

**US-T01: Tải lên mẫu CV**

> *Là chuyên viên HR, tôi muốn tải lên file mẫu CV của công ty (PDF) để hệ thống có thể nhận diện cấu trúc và lưu lại để sử dụng sau.*

**Acceptance Criteria:**
- [ ] Giao diện có khu vực kéo-thả file (drag & drop) và nút click để chọn file.
- [ ] **Bắt buộc** chấp nhận file `.pdf` (có text layer). Các định dạng khác hiển thị thông báo lỗi.
- [ ] **Should-have:** Chấp nhận thêm định dạng `.docx`.
- [ ] Giới hạn kích thước file tối đa: 10MB. File lớn hơn hiển thị thông báo lỗi.
- [ ] Hiển thị trạng thái "Đang xử lý..." trong khi hệ thống phân tích file.
- [ ] Sau khi xử lý thành công, template mới xuất hiện trong danh sách.
- [ ] Nếu file PDF là dạng scan (không có text layer), hiển thị thông báo lỗi rõ ràng hướng dẫn người dùng tải lại file đúng định dạng.
- [ ] Nếu xử lý thất bại vì lý do khác, hiển thị thông báo lỗi rõ ràng (không hiển thị lỗi kỹ thuật nội bộ).

**Luồng kỹ thuật:**
```
[Upload File] → save_upload() → parse_file() → extract_template_schema()
     → [Nếu detect < 2 sections] → llm_fallback.detect_sections_with_llm()
     → Lưu Template vào DB → Trả về TemplateResponse
```

---

**US-T02: Xem danh sách mẫu CV**

> *Là chuyên viên HR, tôi muốn xem tất cả các mẫu CV đã tải lên để chọn mẫu phù hợp khi tạo hồ sơ.*

**Acceptance Criteria:**
- [ ] Trang template hiển thị danh sách dạng lưới (grid) các card mẫu.
- [ ] Mỗi card hiển thị: tên mẫu, số phần (sections), ngày tạo.
- [ ] Khi danh sách trống, hiển thị thông báo hướng dẫn tải lên mẫu đầu tiên.

---

**US-T03: Xóa mẫu CV**

> *Là chuyên viên HR, tôi muốn xóa mẫu CV không còn dùng để giữ danh sách gọn gàng.*

**Acceptance Criteria:**
- [ ] Mỗi card mẫu có nút "Xóa".
- [ ] Trước khi xóa, hệ thống hiển thị hộp thoại xác nhận.
- [ ] Sau khi xóa, mẫu biến mất khỏi danh sách ngay lập tức.

---

### 3.2. Module B — Quản lý Hồ sơ Ứng viên (Candidate Data Extractor)

---

**US-C01: Tải lên và trích xuất thông tin CV ứng viên**

> *Là chuyên viên HR, tôi muốn tải lên CV của ứng viên (PDF) và để hệ thống tự động trích xuất thông tin, giúp tôi không cần nhập tay từng mục.*

**Acceptance Criteria:**
- [ ] Giao diện có khu vực kéo-thả file (drag & drop), **chấp nhận file PDF có text layer** (copyable PDF).
- [ ] Nếu upload PDF dạng scan: hiển thị thông báo lỗi rõ ràng hướng dẫn tải lại đúng định dạng.
- [ ] Sau khi xử lý, hiển thị thông tin đã trích xuất được bao gồm:
  - Họ tên, email, số điện thoại, địa chỉ, LinkedIn
  - Danh sách kinh nghiệm làm việc (công ty, vị trí, thời gian, mô tả)
  - Thông tin học vấn
  - Danh sách kỹ năng
- [ ] Nếu email và kinh nghiệm làm việc đều rỗng → hệ thống tự động thử trích xuất bằng AI hỗ trợ.
- [ ] Thời gian xử lý không quá 60 giây.

**Luồng kỹ thuật:**
```
[Upload CV] → save_upload() → parse_file() → extract_candidate_profile()
     → [Nếu email rỗng VÀ work_experiences rỗng] → llm_fallback.extract_full_profile_with_llm()
     → Lưu Candidate vào DB (version 1) → Trả về CandidateResponse
```

**Quy tắc trích xuất heuristic:**
- **Email:** Regex pattern chuẩn
- **Số điện thoại:** Nhận diện số điện thoại Việt Nam (ưu tiên prefix VN)
- **LinkedIn:** Pattern `linkedin.com/in/`
- **Tên ứng viên:** Dòng đầu tiên hoặc text có font size lớn nhất trong tài liệu
- **Thời gian:** Dùng thư viện `dateparser` để nhận diện đa dạng định dạng ngày

---

**US-C02: Chỉnh sửa thông tin ứng viên trực tiếp trên web**

> *Là chuyên viên HR, tôi muốn xem và sửa thông tin ứng viên đã trích xuất trực tiếp trên web, và mỗi lần lưu sẽ tạo ra một phiên bản mới để tôi có thể xem lại hoặc khôi phục nếu cần.*

**Acceptance Criteria:**
- [ ] Click vào card ứng viên → mở trang/modal hiển thị toàn bộ thông tin.
- [ ] Tất cả các trường đều có thể chỉnh sửa trực tiếp trên giao diện web (inline edit), không cần tải file về.
- [ ] Với các section dạng danh sách (kinh nghiệm, học vấn, dự án), có nút "Thêm mục" để thêm bản ghi mới.
- [ ] Validate định dạng email trước khi lưu.
- [ ] Nút **"Lưu"** → tạo một **phiên bản mới** trong lịch sử (không ghi đè), hiển thị thông báo thành công.
- [ ] Hiển thị danh sách lịch sử phiên bản với: số thứ tự, ngày giờ lưu.
- [ ] Người dùng có thể click vào phiên bản cũ để xem lại nội dung tại thời điểm đó.
- [ ] Nút **"Khôi phục"** phiên bản cũ → tạo một phiên bản mới với nội dung của phiên bản được chọn (không xóa lịch sử).

**Luồng kỹ thuật:**
```
POST /api/candidates/{id}/versions
  { profile_json } → Tạo bản ghi CandidateVersion mới
  → Cập nhật con trỏ "current_version" trong bảng candidates
  → Trả về { version_id, version_number, created_at }

GET /api/candidates/{id}/versions        → Danh sách phiên bản
GET /api/candidates/{id}/versions/{vid}  → Nội dung một phiên bản
POST /api/candidates/{id}/versions/{vid}/restore → Tạo phiên bản mới từ phiên bản cũ
```

---

**US-C03: Xem danh sách và xóa ứng viên**

> *Là chuyên viên HR, tôi muốn quản lý danh sách ứng viên trong hệ thống.*

**Acceptance Criteria:**
- [ ] Trang Candidate hiển thị danh sách card ứng viên với: avatar initials, tên, email, số năm kinh nghiệm, 3 kỹ năng đầu.
- [ ] Có nút "Xóa" với xác nhận trước khi xóa.

---

### 3.3. Module C — Tạo & Xuất CV (CV Generator)

---

**US-G01: Tạo CV chuẩn hóa**

> *Là chuyên viên HR, tôi muốn chọn một ứng viên và một mẫu CV rồi bấm "Tạo" để hệ thống tự ghép thông tin vào mẫu và cho tôi xem kết quả.*

**Acceptance Criteria:**
- [ ] Trang Generator có 3 cột: Chọn ứng viên/mẫu | Xem trước CV | Tùy chỉnh & Xuất file.
- [ ] Dropdown chọn ứng viên: hiển thị tên + email.
- [ ] Dropdown chọn mẫu: hiển thị tên mẫu.
- [ ] Nút "Tạo CV" chỉ active khi đã chọn đủ cả hai.
- [ ] Sau khi tạo, cột giữa hiển thị bản xem trước CV trong khung iframe.
- [ ] CV xem trước trung thành với bố cục, màu sắc, phông chữ của mẫu đã chọn.
- [ ] Mỗi lần tạo, hệ thống tự động lưu một bản nháp (draft).

**Luồng kỹ thuật:**
```
POST /api/generator/render
  { candidate_id, template_id, custom_json? }
  → Lấy candidate + template từ DB
  → Merge profile_json với custom_json (custom có priority)
  → Render Jinja2 template cv_full.html
  → Tạo/Cập nhật CVDraft trong DB
  → Trả về { draft_id, html }
```

---

**US-G02: Tùy chỉnh nội dung trước khi xuất**

> *Là chuyên viên HR, tôi muốn chỉnh sửa một số nội dung của CV (ví dụ: thay đổi mô tả tóm tắt) mà không làm mất thông tin gốc của ứng viên.*

**Acceptance Criteria:**
- [ ] Cột phải có panel chỉnh sửa các trường tùy chỉnh (custom fields).
- [ ] Sau khi thay đổi, đợi 800ms (debounce) rồi tự động cập nhật bản xem trước.
- [ ] Thay đổi được lưu vào `custom_json` riêng biệt, không ghi đè dữ liệu gốc của ứng viên.
- [ ] Có nút "Đặt lại mặc định" để xóa tất cả tùy chỉnh và quay về dữ liệu gốc.
- [ ] CVPreview có nút zoom in/out.

---

**US-G03: Xuất CV dạng PDF**

> *Là chuyên viên HR, tôi muốn tải xuống CV đã tạo dưới dạng PDF chất lượng cao để gửi cho khách hàng.*

**Acceptance Criteria:**
- [ ] Nút "Xuất PDF" trong ExportBar.
- [ ] Click → hiển thị trạng thái loading → tự động tải file về máy.
- [ ] File PDF giữ nguyên bố cục và màu sắc như bản xem trước.
- [ ] Tên file mặc định: `{ten_ung_vien}_{ten_mau}.pdf`.

**Luồng kỹ thuật:**
```
POST /api/generator/export/pdf
  { draft_id } → Load draft → WeasyPrint.write_pdf(rendered_html)
  → Trả về FileResponse (application/pdf)
FE: axios { responseType: 'blob' } → URL.createObjectURL() → trigger download
```

---

**US-G04: Xuất CV dạng DOCX** *(Should-have)*

> *Là chuyên viên HR, tôi muốn tải xuống CV dạng Word để có thể chỉnh sửa thêm nếu cần — tính năng bổ sung sau khi PDF đã hoạt động ổn.*

**Acceptance Criteria:**
- [ ] Nút "Xuất DOCX" trong ExportBar (chỉ hiển thị khi tính năng được bật).
- [ ] Click → tải file `.docx` về máy.
- [ ] File DOCX mở được bằng Microsoft Word / LibreOffice.
- [ ] Tên file mặc định: `{ten_ung_vien}_{ten_mau}.docx`.

> [!NOTE]
> **Should-have:** Tính năng này được triển khai SAU khi PDF export ổn định. Chất lượng định dạng DOCX ở mức "đủ dùng" — không đảm bảo pixel-perfect như PDF.

---

## 4. Luồng Người dùng (User Flow)

### Luồng chính: Từ CV thô đến hồ sơ chuẩn hóa

```
[1] HR tải lên CV ứng viên (PDF copyable)
        ↓
[2] Hệ thống tự động trích xuất thông tin (tên, email, kinh nghiệm...)
        ↓
[3] HR xem kết quả trích xuất trực tiếp trên web
    → Chỉnh sửa inline nếu cần → Lưu (tạo phiên bản mới)
    → Có thể xem lại / khôi phục phiên bản cũ bất kỳ lúc nào
        ↓
[4] HR chọn ứng viên + mẫu CV → Click "Tạo CV"
        ↓
[5] Hệ thống render CV → Hiển thị bản xem trước trên web
        ↓
[6] HR tùy chỉnh nội dung nếu cần → Xem trước cập nhật tự động (debounce)
        ↓
[7] HR click "Xuất PDF" → File PDF tải về máy  [MUST-HAVE]
    HR click "Xuất DOCX" → File DOCX tải về máy [SHOULD-HAVE]
        ↓
[8] HR gửi file PDF cho khách hàng ✓
```

### Luồng thiết lập ban đầu (Setup Flow)

```
[1] HR tải lên mẫu CV của công ty (PDF)
[2] Hệ thống nhận diện cấu trúc mẫu (sections, layout, màu sắc, font)
[3] Mẫu sẵn sàng sử dụng trong Generator
```

---

## 5. Yêu cầu Chức năng Chi tiết (Functional Requirements)

### 5.1. Xử lý file đầu vào

| FR | Yêu cầu | Mức độ |
|---|---|---|
| FR-F01 | Hỗ trợ upload file **PDF có text layer** (copyable PDF) | Must-have |
| FR-F02 | Giới hạn kích thước file: tối đa 10MB | Must-have |
| FR-F03 | Validate MIME type khi nhận file phía server | Must-have |
| FR-F04 | Lưu file gốc vào thư mục upload nội bộ | Must-have |
| FR-F05 | Phát hiện và từ chối PDF dạng scan hình ảnh — hiển thị thông báo lỗi rõ ràng | Must-have |
| FR-F06 | Hỗ trợ upload thêm file `.docx` | Should-have |

### 5.2. Trích xuất Template

| FR | Yêu cầu | Mức độ |
|---|---|---|
| FR-T01 | Phát hiện header section dựa trên font size nổi bật, in đậm, hoặc màu sắc khác biệt so với thân văn bản | Must-have |
| FR-T02 | Phát hiện layout: single-column (mặc định) hoặc two-column (khi tài liệu có 2 cột nội dung rõ ràng) | Must-have |
| FR-T03 | Trích xuất bảng màu chính: lấy top 3 màu xuất hiện nhiều nhất | Must-have |
| FR-T04 | Map text header về section key chuẩn (VD: "kinh nghiệm" → `work_experiences`) | Must-have |
| FR-T05 | Khi detect < 2 sections → gọi AI fallback để nhận diện sections | Should-have |
| FR-T06 | Lưu `schema_json` theo cấu trúc chuẩn (layout, colors, fonts, sections) | Must-have |

### 5.3. Trích xuất Candidate

| FR | Yêu cầu | Mức độ |
|---|---|---|
| FR-C01 | Trích xuất email bằng regex pattern chuẩn | Must-have |
| FR-C02 | Trích xuất số điện thoại với hint vùng Việt Nam (VN) | Must-have |
| FR-C03 | Trích xuất LinkedIn URL bằng pattern `linkedin.com/in/` | Must-have |
| FR-C04 | Xác định tên ứng viên từ dòng đầu hoặc text có font size lớn nhất | Must-have |
| FR-C05 | Parse ngày tháng đa dạng định dạng (VD: "Jan 2022", "01/2022", "Tháng 1, 2022") | Must-have |
| FR-C06 | Khi email rỗng VÀ work_experiences rỗng → kích hoạt AI fallback toàn bộ profile | Should-have |
| FR-C07 | Lưu `profile_json` theo cấu trúc chuẩn đã định nghĩa | Must-have |

### 5.4. Render & Export CV

| FR | Yêu cầu | Mức độ |
|---|---|---|
| FR-G01 | Merge `profile_json` với `custom_json` (custom override có độ ưu tiên cao hơn) | Must-have |
| FR-G02 | Render CV qua Jinja2 template với CSS inline/embedded (không load external CSS) | Must-have |
| FR-G03 | Hỗ trợ render cả layout single-column và two-column | Must-have |
| FR-G04 | Tạo **PDF** từ HTML render qua WeasyPrint | **Must-have** |
| FR-G05 | Lưu `rendered_html` vào bảng `cv_drafts` | Must-have |
| FR-G06 | Auto-save draft sau mỗi lần render hoặc cập nhật custom_json | Must-have |
| FR-G07 | Tạo DOCX trực tiếp từ `profile_json` và `schema_json` | Should-have |

### 5.5. Version History (Lịch sử phiên bản ứng viên)

| FR | Yêu cầu | Mức độ |
|---|---|---|
| FR-V01 | Mỗi lần lưu chỉnh sửa candidate tạo một bản ghi `CandidateVersion` mới trong DB | Must-have |
| FR-V02 | Không ghi đè phiên bản cũ — mỗi lần lưu là append | Must-have |
| FR-V03 | API trả về danh sách phiên bản theo thứ tự thời gian giảm dần | Must-have |
| FR-V04 | API cho phép lấy nội dung `profile_json` của bất kỳ phiên bản nào | Must-have |
| FR-V05 | Restore: tạo phiên bản mới với nội dung sao chép từ phiên bản được chọn | Must-have |

---

## 6. Yêu cầu Phi chức năng (Non-Functional Requirements)

### 6.1. Hiệu năng
- Thời gian xử lý upload và trích xuất: ≤ 60 giây/file
- Thời gian render CV: ≤ 10 giây
- Thời gian export PDF: ≤ 30 giây

### 6.2. Bảo mật
- CORS chỉ cho phép `http://localhost:5173` (dev) — cần cập nhật cho production.
- Không expose stack trace / lỗi kỹ thuật nội bộ ra response API.
- Toàn bộ xử lý AI chạy on-premise qua Ollama — không có network call ra internet.
- Không lưu credentials trong source code, dùng file `.env`.

### 6.3. Độ tin cậy
- Xử lý lỗi file không hợp lệ (sai format, hỏng, có password protection) với thông báo rõ ràng.
- Nếu AI fallback không khả dụng (Ollama offline), hệ thống vẫn trả kết quả heuristic dù có thể thiếu sections.

### 6.4. Khả năng bảo trì
- Cấu trúc code phân layer rõ ràng: routers → services → models.
- Migration DB qua Alembic — mỗi thay đổi schema là 1 migration riêng.

---

## 7. Data Models (Mức sản phẩm)

### 7.1. Template Schema (schema_json)
Thông tin được trích xuất từ mẫu CV và lưu lại, bao gồm:
- **Layout:** Loại bố cục (1 cột / 2 cột)
- **Colors:** Bộ màu chính (primary, accent, background, text)
- **Fonts:** Thông tin font heading và body (family, size, weight)
- **Sections:** Danh sách các phần theo thứ tự (key, tên hiển thị, thứ tự, hiển thị hay không)

### 7.2. Candidate Profile (profile_json)
Thông tin được trích xuất từ CV ứng viên, bao gồm:
- **basic_info:** Họ tên, email, điện thoại, địa chỉ, LinkedIn, website, tóm tắt
- **skills:** Danh sách kỹ năng phân theo nhóm (Backend, Frontend, Tools...)
- **work_experiences:** Danh sách kinh nghiệm (công ty, vị trí, thời gian, mô tả)
- **educations:** Danh sách học vấn (trường, bằng, chuyên ngành, thời gian, GPA)
- **certifications:** Chứng chỉ (tên, đơn vị cấp, ngày)
- **languages:** Ngoại ngữ (tên, mức độ)
- **projects:** Dự án cá nhân (tên, mô tả, tech stack, URL)

### 7.3. CandidateVersion (Lịch sử phiên bản)

Mỗi khi người dùng lưu chỉnh sửa, một bản ghi `CandidateVersion` mới được tạo ra (không ghi đè):
- **version_id:** Định danh duy nhất của phiên bản
- **version_number:** Số thứ tự tăng dần (1, 2, 3...) trong phạm vi một ứng viên
- **profile_json snapshot:** Toàn bộ nội dung `profile_json` tại thời điểm lưu
- **created_at:** Thời gian tạo phiên bản
- **is_current:** Cờ đánh dấu đây là phiên bản đang hoạt động

> **Quy tắc:** Khi tải CV lần đầu → tạo Version 1. Mỗi lần lưu chỉnh sửa → append Version N+1. Restore phiên bản cũ → tạo Version mới có nội dung sao chép từ phiên bản được chọn.

## 8. API Summary

| Method | Endpoint | Mô tả | Mức độ |
|---|---|---|---|
| POST | `/api/templates/upload` | Tải lên và phân tích mẫu CV | Must |
| GET | `/api/templates` | Danh sách mẫu | Must |
| GET | `/api/templates/{id}` | Chi tiết một mẫu | Must |
| DELETE | `/api/templates/{id}` | Xóa mẫu | Must |
| POST | `/api/candidates/upload` | Tải lên và trích xuất thông tin ứng viên | Must |
| GET | `/api/candidates` | Danh sách ứng viên (chỉ basic_info) | Must |
| GET | `/api/candidates/{id}` | Full profile ứng viên (phiên bản hiện tại) | Must |
| DELETE | `/api/candidates/{id}` | Xóa ứng viên | Must |
| POST | `/api/candidates/{id}/versions` | Lưu chỉnh sửa → tạo phiên bản mới | Must |
| GET | `/api/candidates/{id}/versions` | Danh sách lịch sử phiên bản | Must |
| GET | `/api/candidates/{id}/versions/{vid}` | Nội dung một phiên bản cụ thể | Must |
| POST | `/api/candidates/{id}/versions/{vid}/restore` | Khôi phục phiên bản cũ (tạo version mới) | Must |
| POST | `/api/generator/render` | Render CV từ candidate + template | Must |
| POST | `/api/generator/export/pdf` | Xuất PDF từ draft | **Must** |
| PUT | `/api/generator/drafts/{id}` | Cập nhật custom_json và re-render | Must |
| POST | `/api/generator/export/docx` | Xuất DOCX từ draft | Should |

---

## 9. Kế hoạch Phát hành (Release Plan)

| Giai đoạn | Nội dung | Mục tiêu |
|---|---|---|
| **Phase 0** | Bootstrap: Cấu trúc dự án, kết nối DB, trang trắng FE, Docker | Môi trường chạy được |
| **Phase 1** | Module Template Creator: Upload + trích xuất mẫu + hiển thị danh sách | Checkpoint: Upload mẫu → thấy card |
| **Phase 2** | Module Data Extractor: Upload CV + trích xuất + xem/sửa thông tin | Checkpoint: Upload CV → thấy thông tin ứng viên |
| **Phase 3** | Module CV Generator: Render + xem trước + xuất **PDF** (DOCX nếu đủ thời gian) | Checkpoint: Tạo CV → download PDF |
| **Phase 4** | Polish: Error handling, UX cải tiến, seed data | Sản phẩm ổn định, demo được |

---

## 10. Tiêu chí Chấp nhận MVP (MVP Acceptance Criteria)

> [!IMPORTANT]
> MVP chỉ được coi là hoàn thành khi TOÀN BỘ các tiêu chí **Must-have** dưới đây được xác nhận. Các tiêu chí Should-have là mục tiêu của vòng tiếp theo.

**Must-have (bắt buộc hoàn thành):**
- [ ] **[Template]** Tải lên 1 file mẫu CV PDF (có text layer) → hệ thống nhận diện ≥ 2 sections → card template xuất hiện.
- [ ] **[Candidate]** Tải lên 1 CV ứng viên PDF → hệ thống trích xuất đúng: tên, email, ≥ 1 kinh nghiệm làm việc.
- [ ] **[Error - Scan PDF]** Upload PDF dạng scan → hệ thống hiển thị thông báo lỗi rõ ràng hướng dẫn người dùng.
- [ ] **[Edit Online]** Mở giao diện chỉnh sửa, thay đổi một trường → click Lưu → tạo phiên bản mới trong lịch sử.
- [ ] **[Version History]** Xem danh sách phiên bản → click vào phiên bản cũ → xem được nội dung tại thời điểm đó.
- [ ] **[Restore Version]** Khôi phục phiên bản cũ → tạo phiên bản mới với nội dung đã khôi phục.
- [ ] **[Generate]** Chọn ứng viên + mẫu → click "Tạo CV" → bản xem trước hiển thị trong ≤ 10 giây.
- [ ] **[Export PDF]** Click "Xuất PDF" → file PDF tải về máy → mở được, nội dung đúng, giữ đúng layout mẫu.
- [ ] **[E2E Time]** Toàn bộ quy trình từ Upload CV → Xuất PDF hoàn thành trong ≤ 5 phút.
- [ ] **[Error Handling]** Upload file định dạng sai → hiển thị thông báo lỗi rõ ràng (không hiện lỗi kỹ thuật).

**Should-have (mục tiêu vòng tiếp):**
- [ ] **[Export DOCX]** Click "Xuất DOCX" → file DOCX tải về máy → mở được bằng Word/LibreOffice.
- [ ] **[Template DOCX]** Tải lên mẫu CV định dạng DOCX và hệ thống nhận diện cấu trúc.

---

*Tài liệu PRD này là cầu nối giữa yêu cầu nghiệp vụ (BRD) và kế hoạch triển khai kỹ thuật chi tiết. Mọi thay đổi nghiệp vụ cần được phản ánh đồng thời vào cả BRD, PRD và Implementation Plan.*
