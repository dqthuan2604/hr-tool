# Proposal: UI Dark Mode Full Overhaul

## Vấn đề hiện tại (What & Why)

UI hiện tại được build nhanh bằng default Tailwind với white/gray, không có design system, trông như một prototype:
- Toàn bộ màu sắc white/gray, không có accent color nhất quán
- Font chữ browser default (Inter/system-ui), không có typography premium
- Navigation chỉ là text links không có active state hay icon
- Upload zone bare, kém trực quan
- Cards thiếu depth và visual hierarchy
- Empty states đơn giản và nhàm
- Generator page quá minimal, thiếu visual
- Không có Toast notification system (lỗi chỉ hiện dạng alert hoặc console)
- Không có Skeleton loaders

## Mục tiêu
Redesign toàn bộ frontend thành **Dark Mode by default** với design language **"Professional Dark Tech"**:
- OLED-near-black base (`#0a0a0f`)
- Electric Indigo accent (`#6366f1`)
- Geist font cho cả heading và body
- Sidebar navigation thay navbar
- Glassmorphism nhẹ cho cards và modals
- Micro-animations cho entry, hover, và feedback states
- Toast notification system
- Skeleton loaders

## Phạm vi thay đổi (Scope)

### Design System
- `index.css`: CSS variables cho toàn bộ design tokens (color, spacing, border, shadow, font)
- Google Fonts import: Geist / Geist Mono

### Layout
- `App.jsx`: Chuyển từ top navbar → fixed sidebar layout (240px)
- `Sidebar.jsx` (NEW): Navigation với icons, active state, branding

### Components (redesign)
- `FileUpload.jsx`: Dark version với animated glow border khi drag
- `TemplateCard.jsx`: Dark glass card với hover lift effect
- `CandidateCard.jsx`: Dark glass card với extracted data preview
- `Toast.jsx` (NEW): Toast notification system (success, error, info)

### Pages (redesign)
- `TemplatePage.jsx`: Dark layout, dùng dark FileUpload và TemplateCard
- `CandidatePage.jsx`: Dark layout, integrated với Toast
- `GeneratorPage.jsx`: Split layout polish — dark controls panel + CV preview on dark bg

## Không nằm trong phạm vi (Out of Scope)
- Thay đổi API/Backend logic
- Auth/RBAC
- Mobile responsive (tool nội bộ, desktop-first là đủ)
- Animation library ngoài CSS transitions (không cần Framer Motion)

## Tech Stack
- **Framework**: React 18 + Vite (hiện có)
- **Styling**: Tailwind CSS v3 (hiện có) + CSS Variables
- **Icons**: `@phosphor-icons/react` (cần install)
- **Font**: Google Fonts — Geist (via @import)
- **Motion**: CSS transitions + keyframes thuần (không thêm thư viện)
