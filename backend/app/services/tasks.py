import os
import asyncio
from app.worker import celery_app
from app.services.redis_pubsub import publish_job_progress_sync
from app.services.file_parser import parse_file
from app.services.template_extractor import extract_template_schema
from app.services.llm_fallback import detect_sections_with_llm

DISABLE_LLM = os.getenv("DISABLE_LLM", "false").lower() == "true"

# We need to run async llm_fallback in sync Celery task
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def sanitize_null_bytes(data):
    if isinstance(data, str):
        return data.replace('\x00', '')
    elif isinstance(data, dict):
        return {k: sanitize_null_bytes(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_null_bytes(item) for item in data]
    return data

@celery_app.task(name="app.services.tasks.process_template")
def process_template(job_id: str, filename: str, file_path: str):
    try:
        publish_job_progress_sync(job_id, "parsing", "Đang đọc file tài liệu...")
        parsed_data = parse_file(file_path)
        
        publish_job_progress_sync(job_id, "extracting", "Đang phân tích layout grid và trích xuất sections...")
        schema = extract_template_schema(parsed_data)
        
        # If heuristics failed (< 2 sections), use LLM (only when LLM is enabled)
        if len(schema.get("sections", [])) < 2 and not DISABLE_LLM:
            publish_job_progress_sync(job_id, "llm_fallback", "Phân tích nâng cao bằng AI...")
            sections = run_async(detect_sections_with_llm(parsed_data.get("raw_text", "")))
            if sections:
                schema["sections"] = sections
                
        # Sanitize null bytes before inserting to PostgreSQL
        schema = sanitize_null_bytes(schema)
                
        from app.database import SessionLocal
        from app.models.template import Template
        
        db = SessionLocal()
        try:
            template_name = os.path.splitext(filename)[0]
            new_template = Template(
                name=template_name,
                source_file=file_path,
                schema_json=schema
            )
            db.add(new_template)
            db.commit()
            db.refresh(new_template)
            
            payload = {
                "template_id": str(new_template.id),
                "name": template_name,
                "schema": schema
            }
            publish_job_progress_sync(job_id, "done", "Phân tích thành công!", payload)
        finally:
            db.close()
            
    except Exception as e:
        # traceback.print_exc()  # User requested to remove print log for backend
        publish_job_progress_sync(job_id, "error", "Lỗi hệ thống trong quá trình phân tích file. Vui lòng thử lại sau hoặc liên hệ Admin.")

