# Tasks: Fix Candidate API & Add Template Detail View

## Track A — Backend Bug Fix

- [x] **Task 1: Thêm cột `raw_text` vào Candidate model**
  - [x] Mở `backend/app/models/candidate.py`
  - [x] Import `Text` từ sqlalchemy
  - [x] Thêm `raw_text = Column(Text, nullable=True)` vào class `Candidate`

- [x] **Task 2: Tạo Alembic Migration**
  - [x] Chạy: `docker compose exec backend alembic revision --autogenerate -m "add_raw_text_to_candidates"`
  - [x] Verify file migration được tạo trong `alembic/versions/`
  - [x] Chạy: `docker compose exec backend alembic upgrade head`
  - [x] Verify: `docker compose exec backend alembic current` hiển thị head

- [x] **Task 3: Verify fix**
  - [x] Upload 1 CV candidate lên UI
  - [x] Kiểm tra `POST /api/candidates/upload` trả về 200
  - [x] Kiểm tra candidate xuất hiện trong list

## Track B — Frontend Template Detail Modal

- [x] **Task 4: Tạo `TemplateDetailModal` component**
  - [x] Tạo file `frontend/src/components/TemplateDetailModal.jsx`
  - [x] Layout: overlay + card với header, 2-col grid (layout info | sections list), collapsible JSON
  - [x] Sections list: scroll để hiện tất cả sections, không chỉ 3 cái đầu
  - [x] Close on overlay click + Escape key

- [x] **Task 5: Update `TemplateCard` để trigger modal**
  - [x] Thêm state `showDetail` vào TemplateCard
  - [x] Thêm button "Xem chi tiết" với eye icon
  - [x] Render `TemplateDetailModal` khi `showDetail === true`

- [ ] **Task 6: Verify Template Detail**
  - [ ] Click vào template card → modal mở
  - [ ] Kiểm tra tất cả sections hiển thị đúng
  - [ ] Kiểm tra layout info hiển thị đúng
  - [ ] Đóng modal bằng [×] và click overlay
