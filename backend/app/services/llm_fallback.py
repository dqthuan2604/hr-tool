import json
import httpx
from app import config

async def detect_sections_with_llm(raw_text: str) -> list:
    prompt = f"""
    You are an AI that extracts CV sections. Look at the following CV text.
    Return a valid JSON array of sections. Each section must have:
    - "key": internal key (e.g., basic_info, work_experiences, educations, skills, certifications, projects)
    - "label": exactly as written in the CV
    - "order": integer order
    - "column": 0
    - "content": the full text content belonging to this section
    
    CV Text:
    {raw_text[:3000]}
    
    Return ONLY JSON ARRAY.
    """
    
    for attempt in range(3):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.OLLAMA_URL}/api/generate",
                    json={
                        "model": "qwen2.5:1.5b",
                        "prompt": prompt,
                        "format": "json",
                        "stream": False
                    },
                    timeout=30.0
                )
            result = response.json()
            response_text = result.get("response", "[]")
            
            sections = json.loads(response_text)
            if isinstance(sections, list):
                return sections
        except Exception:
            continue
            
    return []

async def extract_full_profile_with_llm(raw_text: str) -> dict:
    prompt = f"""
    You are an AI that extracts candidate profiles from CV text.
    Return a valid JSON object matching this schema:
    {{
      "basic_info": {{"full_name": "", "email": "", "phone": "", "address": "", "linkedin": "", "website": "", "summary": ""}},
      "skills": [{{"category": "General", "items": ["skill1", "skill2"]}}],
      "work_experiences": [{{"company": "", "role": "", "start_date": "", "end_date": "", "description": ""}}],
      "educations": [{{"school": "", "degree": "", "major": "", "start_date": "", "end_date": "", "gpa": ""}}],
      "certifications": [{{"name": "", "issuer": "", "date": ""}}],
      "languages": [{{"language": "", "level": ""}}],
      "projects": [{{"name": "", "description": "", "tech_stack": [], "url": ""}}]
    }}
    
    CV Text:
    {raw_text[:3000]}
    
    Return ONLY JSON OBJECT. Do not include markdown formatting or other text.
    """
    
    empty_profile = {
        "basic_info": {"full_name": "", "email": "", "phone": "", "address": "", "linkedin": "", "website": "", "summary": ""},
        "skills": [],
        "work_experiences": [],
        "educations": [],
        "certifications": [],
        "languages": [],
        "projects": []
    }
    
    for attempt in range(3):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.OLLAMA_URL}/api/generate",
                    json={
                        "model": "qwen2.5:1.5b",
                        "prompt": prompt,
                        "format": "json",
                        "stream": False
                    },
                    timeout=45.0
                )
            result = response.json()
            response_text = result.get("response", "{}")
            
            profile = json.loads(response_text)
            if isinstance(profile, dict) and "basic_info" in profile:
                return profile
        except Exception:
            continue
            
    return empty_profile

