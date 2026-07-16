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

@router.post("/upload", response_model=CandidateResponse)
async def upload_candidate(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
    # Validate file size (<10MB)
    MAX_SIZE = 10 * 1024 * 1024
    if file.size and file.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    try:
        # Read file
        file_content = await file.read()
        file_path = await run_in_threadpool(save_upload, file_content, file.filename)
        
        # Parse file
        parsed_data = await run_in_threadpool(parse_file, file_path)
        
        # --- LOG RAW TEXT FOR DEBUGGING ---
        # print("\n" + "="*50)
        # print(f"RAW TEXT EXTRACTED FROM {file.filename}:")
        # print("="*50)
        # print(parsed_data.get("raw_text", ""))
        # print("="*50 + "\n")
        
        # Heuristic Extraction
        profile_json = await run_in_threadpool(extract_candidate_profile, parsed_data)
        
        # AI Fallback check
        email = profile_json.get("basic_info", {}).get("email", "")
        work_exp = profile_json.get("work_experiences", [])
        
        if not email and not work_exp:
            import os
            disable_llm = os.getenv("DISABLE_LLM", "false").lower() == "true"
            if not disable_llm:
                # Try LLM fallback if heuristic failed heavily
                llm_profile = await extract_full_profile_with_llm(parsed_data.get("raw_text", ""))
                if llm_profile.get("basic_info", {}).get("email") or llm_profile.get("work_experiences"):
                    profile_json = llm_profile
                
        # Save to DB
        candidate = Candidate(
            source_file=file.filename,
            raw_text=parsed_data.get("raw_text", "")
        )
        db.add(candidate)
        db.flush() # to get ID
        
        # Save version 1
        version = CandidateVersion(
            candidate_id=candidate.id,
            version_number=1,
            profile_json=profile_json,
            is_current=True
        )
        db.add(version)
        db.commit()
        db.refresh(candidate)
        
        return candidate
        
    except Exception as e:
        print(f"Error processing candidate: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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
