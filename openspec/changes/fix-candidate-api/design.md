# Design: Fix Candidate API & Add Template Detail View

## Backend — Thêm cột `raw_text` vào Candidate

### Model Change (`app/models/candidate.py`)
Thêm cột:
```python
raw_text = Column(Text, nullable=True)
```

### Alembic Migration
Tạo file `alembic/versions/xxxx_add_raw_text_to_candidates.py`:
```python
def upgrade():
    op.add_column('candidates', sa.Column('raw_text', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('candidates', 'raw_text')
```

Chạy trong container: `docker compose exec backend alembic upgrade head`

### Router (`app/routers/candidates.py`)
Không cần thay đổi — constructor Candidate đã đúng sau khi thêm cột model.

---

## Frontend — TemplateDetailModal

### Component mới: `src/components/TemplateDetailModal.jsx`

**Data từ `template.schema_json`:**
```json
{
  "sections": [
    { "label": "A. PERSONAL INFORMATION", "type": "header", ... },
    ...
  ],
  "layout": {
    "columns": ["100%"]
  }
}
```

**Hiển thị:**
- Header: Tên template + ngày tạo + nút đóng [×]
- Grid 2 cột:
  - Trái: Layout info (columns), metadata
  - Phải: Danh sách sections (scroll, tất cả sections)
- Collapsible raw JSON schema (dành cho debug)

### TemplateCard update
Thêm button "Xem chi tiết" bên cạnh nút Delete, với state `isDetailOpen` quản lý modal.

### Props interface
```jsx
<TemplateDetailModal
  template={template}       // full template object
  onClose={() => ...}       // close handler
/>
```

---

## Migration Command Sequence
```bash
# Trong container backend
docker compose exec backend alembic revision --autogenerate -m "add_raw_text_to_candidates"
docker compose exec backend alembic upgrade head
```
