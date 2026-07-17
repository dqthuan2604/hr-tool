import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from datetime import datetime

from app import database
from app.models.candidate import Candidate, CandidateVersion
from app.schemas.candidate import CandidateResponse, CandidateVersionResponse, CandidateUpdate
from app.services.file_parser import save_upload, parse_file
from app.services.candidate_extractor import extract_candidate_profile
from app.services.llm_fallback import extract_full_profile_with_llm

router = APIRouter(prefix="/candidates", tags=["Candidates"])

import json
from sse_starlette.sse import EventSourceResponse
from app.services.redis_pubsub import redis_client
from app.worker import celery_app

@router.post("/upload")
async def upload_candidate(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
    # Validate file size (<10MB)
    MAX_SIZE = 10 * 1024 * 1024
    if file.size and file.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    job_id = str(uuid.uuid4())
    file_content = await file.read()
    
    file_path = await run_in_threadpool(save_upload, file_content, file.filename)
    
    # Send task to celery
    celery_app.send_task("app.services.tasks.process_candidate", args=[job_id, file.filename, file_path])
    
    return {"job_id": job_id}

@router.get("/upload/{job_id}/stream")
async def stream_progress(job_id: str):
    async def event_generator():
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"job_progress_{job_id}")
        
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data_str = message['data']
                    yield {"event": "message", "data": data_str}
                    
                    try:
                        data = json.loads(data_str)
                        if data.get("status") in ["done", "error"]:
                            break
                    except:
                        pass
        finally:
            await pubsub.unsubscribe()
            
    return EventSourceResponse(event_generator())

@router.get("", response_model=list[CandidateResponse])
def list_candidates(db: Session = Depends(database.get_db)):
    # Lấy danh sách candidate và eager load versions
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    return candidates

@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str, db: Session = Depends(database.get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.post("/{candidate_id}/versions", response_model=CandidateVersionResponse)
def save_version(candidate_id: str, data: CandidateUpdate, db: Session = Depends(database.get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    # Remove is_current from old versions
    db.query(CandidateVersion).filter(CandidateVersion.candidate_id == candidate_id).update({"is_current": False})
    
    # Calculate next version number
    max_version = max([v.version_number for v in candidate.versions] or [0])
    
    new_version = CandidateVersion(
        candidate_id=candidate.id,
        version_number=max_version + 1,
        profile_json=data.profile_json,
        is_current=True
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version

@router.get("/{candidate_id}/versions", response_model=list[CandidateVersionResponse])
def list_versions(candidate_id: str, db: Session = Depends(database.get_db)):
    versions = db.query(CandidateVersion).filter(CandidateVersion.candidate_id == candidate_id).order_by(CandidateVersion.version_number.desc()).all()
    return versions

@router.get("/{candidate_id}/versions/{version_id}", response_model=CandidateVersionResponse)
def get_version(candidate_id: str, version_id: str, db: Session = Depends(database.get_db)):
    version = db.query(CandidateVersion).filter(
        CandidateVersion.id == version_id,
        CandidateVersion.candidate_id == candidate_id
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.post("/{candidate_id}/versions/{version_id}/restore", response_model=CandidateVersionResponse)
def restore_version(candidate_id: str, version_id: str, db: Session = Depends(database.get_db)):
    old_version = db.query(CandidateVersion).filter(
        CandidateVersion.id == version_id,
        CandidateVersion.candidate_id == candidate_id
    ).first()
    if not old_version:
        raise HTTPException(status_code=404, detail="Version not found")
        
    # Unset current
    db.query(CandidateVersion).filter(CandidateVersion.candidate_id == candidate_id).update({"is_current": False})
    
    max_version = max([v.version_number for v in old_version.candidate.versions] or [0])
    
    new_version = CandidateVersion(
        candidate_id=old_version.candidate_id,
        version_number=max_version + 1,
        profile_json=old_version.profile_json,
        is_current=True
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version

@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: str, db: Session = Depends(database.get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    db.delete(candidate)
    db.commit()
    return {"status": "ok"}
