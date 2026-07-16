"""
generator.py — Router for CV Generator
POST /api/generator/render       → render CV HTML
POST /api/generator/export/pdf   → export PDF
POST /api/generator/export/docx  → export DOCX
PUT  /api/generator/drafts/{id}  → update custom_json + re-render
GET  /api/generator/drafts/{id}  → get draft
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime

from app import database
from app.models.candidate import Candidate
from app.models.template import Template
from app.models.cv_draft import CVDraft
from app.schemas.generator import RenderRequest, ExportRequest
from app.services.cv_renderer import render_cv
from app.services.cv_exporter import export_pdf, export_docx

router = APIRouter(prefix="/generator", tags=["Generator"])


@router.post("/render")
def render(data: RenderRequest, db: Session = Depends(database.get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    template = db.query(Template).filter(Template.id == data.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    html = render_cv(candidate, template, data.custom_json)

    # Upsert draft (one draft per candidate+template pair for simplicity)
    draft = db.query(CVDraft).filter(
        CVDraft.candidate_id == data.candidate_id,
        CVDraft.template_id == data.template_id
    ).first()

    if draft:
        draft.custom_json = data.custom_json
        draft.rendered_html = html
        draft.updated_at = datetime.utcnow()
    else:
        draft = CVDraft(
            candidate_id=data.candidate_id,
            template_id=data.template_id,
            custom_json=data.custom_json,
            rendered_html=html
        )
        db.add(draft)

    db.commit()
    db.refresh(draft)

    return {"draft_id": str(draft.id), "html": html}


@router.post("/export/pdf")
def export_pdf_endpoint(data: ExportRequest, db: Session = Depends(database.get_db)):
    draft = db.query(CVDraft).filter(CVDraft.id == data.draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if not draft.rendered_html:
        raise HTTPException(status_code=400, detail="Draft has no rendered HTML")

    pdf_bytes = export_pdf(draft.rendered_html)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=cv_export.pdf",
            "Content-Length": str(len(pdf_bytes))
        }
    )


@router.post("/export/docx")
def export_docx_endpoint(data: ExportRequest, db: Session = Depends(database.get_db)):
    draft = db.query(CVDraft).filter(CVDraft.id == data.draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    # Need candidate profile + template schema for docx generation
    candidate = draft.candidate
    template = draft.template

    # Get current profile
    current_version = None
    for v in candidate.versions:
        if v.is_current:
            current_version = v
            break
    if current_version is None and candidate.versions:
        current_version = candidate.versions[0]

    profile_json = current_version.profile_json if current_version else {}
    schema_json = template.schema_json if template else {}

    # Apply overrides
    if draft.custom_json:
        for k, v in draft.custom_json.items():
            if k in profile_json and isinstance(profile_json[k], dict) and isinstance(v, dict):
                profile_json[k] = {**profile_json[k], **v}
            else:
                profile_json[k] = v

    docx_bytes = export_docx(profile_json, schema_json)

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": "attachment; filename=cv_export.docx",
            "Content-Length": str(len(docx_bytes))
        }
    )


@router.get("/drafts/{draft_id}")
def get_draft(draft_id: str, db: Session = Depends(database.get_db)):
    draft = db.query(CVDraft).filter(CVDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return {
        "id": str(draft.id),
        "candidate_id": str(draft.candidate_id),
        "template_id": str(draft.template_id),
        "custom_json": draft.custom_json,
        "rendered_html": draft.rendered_html,
        "created_at": draft.created_at,
        "updated_at": draft.updated_at
    }


@router.put("/drafts/{draft_id}")
def update_draft(draft_id: str, data: dict, db: Session = Depends(database.get_db)):
    draft = db.query(CVDraft).filter(CVDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    custom_json = data.get("custom_json")
    draft.custom_json = custom_json
    draft.updated_at = datetime.utcnow()

    # Re-render
    candidate = draft.candidate
    template = draft.template
    if candidate and template:
        draft.rendered_html = render_cv(candidate, template, custom_json)

    db.commit()
    db.refresh(draft)

    return {"draft_id": str(draft.id), "html": draft.rendered_html}
