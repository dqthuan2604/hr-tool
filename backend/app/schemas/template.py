from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    layout_json: Dict[str, Any] = Field(..., alias="schema_json")

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: UUID
    source_file: Optional[str] = None
    preview_html: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
