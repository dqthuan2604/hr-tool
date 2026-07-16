from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class CVDraftBase(BaseModel):
    custom_json: Optional[Dict[str, Any]] = None
    rendered_html: Optional[str] = None

class CVDraftCreate(CVDraftBase):
    candidate_id: UUID
    template_id: Optional[UUID] = None

class CVDraftResponse(CVDraftBase):
    id: UUID
    candidate_id: UUID
    template_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CVDraftUpdate(BaseModel):
    custom_json: Optional[Dict[str, Any]] = None
