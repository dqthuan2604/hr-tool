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
                
        # Generate HTML/CSS template using AI
        if DISABLE_LLM:
            publish_job_progress_sync(job_id, "ai_generating", "Sử dụng template mặc định (AI bị vô hiệu hóa)...")
            from app.services.ai_template_generator import _get_fallback_template
            html_content = _get_fallback_template(schema)
        else:
            publish_job_progress_sync(job_id, "ai_generating", "Đang sử dụng AI tạo mã HTML/CSS Template...")
            from app.services.ai_template_generator import generate_template_html
            html_content = run_async(generate_template_html(schema))

        # Generate Dummy Preview
        from app.services.cv_renderer import render_cv_html
        dummy_profile = {
            "basic_info": {
                "full_name": "Nguyễn Văn A",
                "email": "nguyenvana@example.com",
                "phone": "+84 123 456 789",
                "address": "TP. Hồ Chí Minh",
                "summary": "Mục tiêu nghề nghiệp: Trở thành một lập trình viên Fullstack giỏi, mang lại nhiều giá trị cho công ty."
            },
            "work_experiences": [
                {
                    "company": "Công ty TNHH Phần Mềm X",
                    "role": "Frontend Developer",
                    "start_date": "01/2022",
                    "end_date": "Hiện tại",
                    "description": "- Phát triển các tính năng UI/UX với ReactJS.\n- Tối ưu hóa hiệu năng trang web."
                }
            ],
            "educations": [
                {
                    "school": "Đại học Công Nghệ Thông Tin",
                    "degree": "Cử nhân",
                    "major": "Kỹ thuật phần mềm",
                    "start_date": "2018",
                    "end_date": "2022",
                    "gpa": "3.5/4.0"
                }
            ],
            "skills": [
                {
                    "category": "Ngôn ngữ & Framework",
                    "items": ["HTML/CSS", "JavaScript", "ReactJS", "NodeJS"]
                }
            ]
        }
        
        # Render the dummy profile into the AI generated template
        # Need to use Jinja directly here because cv_renderer might load from file
        from jinja2 import Template as JinjaTemplate
        try:
            jinja_template = JinjaTemplate(html_content)
            preview_html = jinja_template.render(profile=dummy_profile)
        except Exception as jinja_err:
            print("Jinja Error:", jinja_err)
            preview_html = html_content # fallback to raw

        from app.database import SessionLocal
        from app.models.template import Template
        
        db = SessionLocal()
        try:
            template_name = os.path.splitext(filename)[0]
            new_template = Template(
                name=template_name,
                source_file=file_path,
                schema_json=schema,
                html_content=html_content,
                preview_html=preview_html
            )
            db.add(new_template)
            db.commit()
            db.refresh(new_template)
            
            payload = {
                "template_id": str(new_template.id),
                "name": template_name,
                "schema": schema
            }
            publish_job_progress_sync(job_id, "done", "Phân tích và tạo Template thành công!", payload)
        finally:
            db.close()
            
    except Exception as e:
        # traceback.print_exc()  # User requested to remove print log for backend
        publish_job_progress_sync(job_id, "error", "Lỗi hệ thống trong quá trình phân tích file. Vui lòng thử lại sau hoặc liên hệ Admin.")


@celery_app.task(name="app.services.tasks.process_candidate")
def process_candidate(job_id: str, filename: str, file_path: str):
    try:
        publish_job_progress_sync(job_id, "parsing", "Đang đọc file tài liệu...")
        parsed_data = parse_file(file_path)
        
        publish_job_progress_sync(job_id, "extracting", "Đang trích xuất thông tin ứng viên...")
        from app.services.candidate_extractor import extract_candidate_profile
        profile_json = extract_candidate_profile(parsed_data)
        
        profile_json = sanitize_null_bytes(profile_json)
        
        from app.database import SessionLocal
        from app.models.candidate import Candidate, CandidateVersion
        
        db = SessionLocal()
        try:
            candidate = Candidate(
                source_file=filename,
                raw_text=sanitize_null_bytes(parsed_data.get("raw_text", ""))
            )
            db.add(candidate)
            db.flush()
            
            version = CandidateVersion(
                candidate_id=candidate.id,
                version_number=1,
                profile_json=profile_json,
                is_current=True
            )
            db.add(version)
            db.commit()
            db.refresh(candidate)
            
            payload = {
                "candidate_id": str(candidate.id),
                "source_file": filename
            }
            publish_job_progress_sync(job_id, "done", "Trích xuất thành công!", payload)
        finally:
            db.close()
            
    except Exception as e:
        publish_job_progress_sync(job_id, "error", f"Lỗi hệ thống trong quá trình trích xuất file: {str(e)}")
