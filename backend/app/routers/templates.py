import uuid
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from app import database
from app.models.template import Template
from app.services.file_parser import save_upload
from app.services.redis_pubsub import redis_client
from app.worker import celery_app

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.post("/upload")
async def upload_template(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    # Validate file size (<10MB)
    MAX_SIZE = 10 * 1024 * 1024
    if file.size and file.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
    job_id = str(uuid.uuid4())
    file_content = await file.read()
    
    from fastapi.concurrency import run_in_threadpool
    file_path = await run_in_threadpool(save_upload, file_content, file.filename)
    
    # Send task to celery
    celery_app.send_task("app.services.tasks.process_template", args=[job_id, file.filename, file_path])
    
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

@router.get("")
def list_templates(db: Session = Depends(database.get_db)):
    templates = db.query(Template).order_by(Template.created_at.desc()).all()
    return templates

@router.get("/{template_id}")
def get_template(template_id: str, db: Session = Depends(database.get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}")
def delete_template(template_id: str, db: Session = Depends(database.get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    db.delete(template)
    db.commit()
    return {"status": "ok"}
