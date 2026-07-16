from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID

class RenderRequest(BaseModel):
    candidate_id: UUID
    template_id: UUID
    custom_json: Optional[Dict[str, Any]] = None

class ExportRequest(BaseModel):
    draft_id: UUID
