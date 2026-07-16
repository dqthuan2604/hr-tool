# Tasks: UI Dark Mode Full Overhaul

## Phase 1 — Foundation (Design System)

- [x] **Task 1: Install Phosphor Icons**
  - [x] `docker compose exec frontend npm install @phosphor-icons/react`

- [x] **Task 2: Rewrite `src/index.css`**
  - [x] Import Google Fonts (JetBrains Mono)
  - [x] Khai báo tất cả CSS custom properties (design tokens)
  - [x] Base styles: `body { background, color, font-family }`
  - [x] CSS animations: `fadeUp`, `slideInRight`, `glowPulse`, `spin`, `shimmer`
  - [x] Utility classes: `.glass-card`, `.dark-input`, `.skeleton`, `.badge-*`

## Phase 2 — Layout

- [x] **Task 3: Tạo `Sidebar.jsx` component**
  - [x] Logo + brand + version badge
  - [x] Nav items: Templates (FilePdf icon), Candidates (Users icon), Generator (MagicWand icon)
  - [x] Active state dùng `useLocation()` qua NavLink `isActive`
  - [x] "System online" status badge ở footer

- [x] **Task 4: Rewrite `App.jsx`**
  - [x] Layout: `flex h-screen` — sidebar 240px + main `flex-1 overflow-auto`
  - [x] ToastProvider wrapper
  - [x] Background: `var(--bg-base)`

## Phase 3 — Components

- [x] **Task 5: Tạo `Toast.jsx` + ToastContext**
  - [x] `ToastContext` với `useToast()` hook
  - [x] `ToastContainer` fixed bottom-right
  - [x] Toast variants: success/error/info với icon + message + auto-dismiss 4s
  - [x] Slide-in animation

- [x] **Task 6: Rewrite `FileUpload.jsx` (dark version)**
  - [x] Dark background `var(--bg-surface)`
  - [x] Glow pulse animation khi dragover
  - [x] UploadSimple, FilePdf, FileDoc icons từ Phosphor
  - [x] Progress overlay: dark glassmorphism
  - [x] Lỗi → `useToast()` error thay vì state

- [x] **Task 7: Rewrite `TemplateCard.jsx` (dark glass)**
  - [x] Glass card base từ `.glass-card` utility
  - [x] Hover effects qua inline styles
  - [x] Actions: Eye icon (chi tiết) + Trash icon (xóa)
  - [x] Badge sections count với badge-success/badge-warning

- [x] **Task 8: Rewrite `CandidateCard.jsx` (dark glass)**
  - [x] Hiển thị: full_name, email, work_exp count
  - [x] Status badge: "Trích xuất OK" (green) vs "Một phần" (yellow)
  - [x] Glass card + hover effect via inline styles

## Phase 4 — Pages

- [x] **Task 9: Rewrite `TemplatePage.jsx`**
  - [x] Page header với eyebrow tag + title + CTA toggle button
  - [x] FileUpload dark version trong collapsible section
  - [x] Grid cards với TemplateCard (dark)
  - [x] Skeleton loaders khi loading
  - [x] Empty state: dark với icon

- [x] **Task 10: Rewrite `CandidatePage.jsx`**
  - [x] Page header
  - [x] FileUpload dark version (candidate mode)
  - [x] Grid CandidateCard (dark)
  - [x] Toast integration cho upload success/error/delete

- [x] **Task 11: Polish `GeneratorPage.jsx`**
  - [x] Controls panel: dark glass sidebar
  - [x] Select dropdowns styled với `.dark-input`
  - [x] Empty state preview: icon + description
  - [x] Generate button: accent gradient với icon
  - [x] Toast integration

## Phase 5 — QA

- [ ] **Task 12: Visual QA**
  - [ ] Frontend build thành công (no errors)
  - [ ] Toast hiện khi upload success/error
  - [ ] Sidebar active state đúng cho từng route
  - [ ] Cards hover effect mượt
  - [ ] Template detail modal dark theme
  - [ ] Generator preview hiển thị CV trên dark background
