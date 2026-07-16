# Design: UI Dark Mode Full Overhaul

## Design Language

**Vibe:** Ethereal Glass Dark Tech — tool nội bộ premium
**Design Read:** Internal HR SaaS for HR team, dark-first, professional, functional + premium feel
**Dials:** DESIGN_VARIANCE: 7 | MOTION_INTENSITY: 5 | VISUAL_DENSITY: 5

---

## Design Tokens (CSS Variables)

```css
/* index.css — global tokens */
:root {
  /* Backgrounds */
  --bg-base:        #09090f;
  --bg-surface:     #111118;
  --bg-elevated:    #1a1a26;
  --bg-overlay:     #1e1e2e;
  --bg-raised:      #252535;

  /* Accent — Electric Indigo */
  --accent:         #6366f1;
  --accent-hover:   #818cf8;
  --accent-muted:   rgba(99, 102, 241, 0.15);
  --accent-glow:    rgba(99, 102, 241, 0.25);

  /* Text */
  --text-primary:   #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted:     #64748b;
  --text-disabled:  #334155;

  /* Borders */
  --border:         rgba(255, 255, 255, 0.08);
  --border-subtle:  rgba(255, 255, 255, 0.05);
  --border-accent:  rgba(99, 102, 241, 0.4);

  /* Shadows */
  --shadow-card:    0 4px 24px rgba(0, 0, 0, 0.4);
  --shadow-modal:   0 24px 64px rgba(0, 0, 0, 0.6);
  --shadow-glow:    0 0 20px rgba(99, 102, 241, 0.2);

  /* Radius */
  --radius-sm:      6px;
  --radius-md:      10px;
  --radius-lg:      14px;
  --radius-xl:      20px;

  /* Font */
  --font-sans:      'Geist', 'Inter', system-ui, sans-serif;
  --font-mono:      'Geist Mono', 'JetBrains Mono', monospace;
}

body {
  background: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-sans);
}
```

---

## Layout Architecture

### Sidebar (240px fixed left)
```
┌──────────────────────┐
│  ⚡ HR Tool          │  ← logo + brand
│  v1.0 beta           │  ← version badge
│                      │
│  ─────────────────   │
│  📄 Templates        │  ← nav item (inactive)
│  👤 Candidates       │  ← nav item (active = accent bg + left border)
│  ✨ Generator        │  ← nav item (inactive)
│                      │
│  ─────────────────   │
│  (bottom: status)    │
└──────────────────────┘
```

**Active state:** `bg-accent/10 border-l-2 border-accent text-accent`
**Inactive state:** `text-text-secondary hover:text-text-primary hover:bg-bg-elevated`

### Main Content Area
- Background: `var(--bg-base)`
- Padding: `p-8`
- Max-width: `max-w-6xl mx-auto`

### Page Header (per page)
```
┌─────────────────────────────────────────────────────┐
│  [Page Title — large, font-bold]                    │
│  [subtitle — text-secondary, text-sm]               │
│                                          [Primary CTA] │
└─────────────────────────────────────────────────────┘
```

---

## Component Specifications

### Glass Card (base pattern)
```css
.glass-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: all 0.2s cubic-bezier(0.32, 0.72, 0, 1);
}
.glass-card:hover {
  border-color: var(--border-accent);
  box-shadow: var(--shadow-card), var(--shadow-glow);
  transform: translateY(-2px);
}
```

### FileUpload (dark version)
- Background: `bg-surface`
- Border: `border-2 border-dashed border-border` → on drag: `border-accent shadow-glow`
- Animated: pulsing glow animation khi dragover
- Icon: Phosphor `UploadSimple` (light weight, 48px)
- Progress overlay: dark glassmorphism với spinner

### Toast System
- Position: `fixed bottom-6 right-6 z-[100]`
- Types: `success` (emerald), `error` (red), `info` (indigo)
- Animation: slide-in from right, fade-out
- Auto-dismiss: 4 seconds
- Max 3 toasts visible at once

### TemplateCard (dark glass)
- Shows: name, ID (monospace), layout, section count, top 3 section tags
- Actions: [👁 Chi tiết] + [🗑 Xóa]
- Hover: lift + accent border glow

### CandidateCard (dark glass)
- Shows: Full name (if extracted), source file, email (if extracted), work_exp count
- Status badge: "Đã trích xuất" (green) / "Một phần" (yellow)
- Actions: [👁 Chi tiết] + [🗑 Xóa]

### Generator Page Layout
```
┌──────────────────────────────────────────────────────────┐
│  [Dark Panel 300px]  │  [Preview Area — flex-1]          │
│                      │                                    │
│  CANDIDATE           │   ┌──────────────────────────┐   │
│  [select dropdown]   │   │  CV Preview              │   │
│                      │   │  (white paper on dark bg) │   │
│  TEMPLATE            │   │                          │   │
│  [select dropdown]   │   │                          │   │
│                      │   └──────────────────────────┘   │
│  [Generate CV btn]   │                                    │
│  ─────────────────   │                                    │
│  Export options      │                                    │
│  Zoom slider         │                                    │
└──────────────────────────────────────────────────────────┘
```

**Select dropdown styling (dark):**
```css
.dark-select {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: var(--radius-md);
}
.dark-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-muted);
}
```

---

## Animation Patterns

### Entry Animation (section/card fade-up)
```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-up {
  animation: fadeUp 0.4s cubic-bezier(0.32, 0.72, 0, 1) forwards;
}
```

### Toast Slide-in
```css
@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0); opacity: 1; }
}
```

### Upload Glow Pulse
```css
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 10px var(--accent-glow); }
  50%       { box-shadow: 0 0 25px var(--accent-glow), 0 0 50px rgba(99,102,241,0.1); }
}
```

---

## Icon System

**Library:** `@phosphor-icons/react` — Duotone or Regular weight

| Usage | Icon |
|-------|------|
| Templates nav | `FilePdf` |
| Candidates nav | `Users` |
| Generator nav | `MagicWand` |
| Upload | `UploadSimple` |
| View detail | `Eye` |
| Delete | `Trash` |
| Close | `X` |
| Generate | `Lightning` |
| Export PDF | `FilePdf` |
| Success toast | `CheckCircle` |
| Error toast | `XCircle` |
| Info toast | `Info` |

---

## File Change Map

| File | Action | Notes |
|------|--------|-------|
| `src/index.css` | REWRITE | Design tokens + base styles + animations |
| `src/App.jsx` | REWRITE | Sidebar layout |
| `src/components/Sidebar.jsx` | NEW | Navigation sidebar |
| `src/components/Toast.jsx` | NEW | Toast system + context |
| `src/components/FileUpload.jsx` | REWRITE | Dark version |
| `src/components/TemplateCard.jsx` | REWRITE | Dark glass + modal trigger |
| `src/components/CandidateCard.jsx` | REWRITE | Dark glass + better data display |
| `src/pages/TemplatePage.jsx` | REWRITE | Dark layout |
| `src/pages/CandidatePage.jsx` | REWRITE | Dark + toast integration |
| `src/pages/GeneratorPage.jsx` | REWRITE | Polish dark controls panel |
| `frontend/package.json` | MODIFY | Add @phosphor-icons/react |
