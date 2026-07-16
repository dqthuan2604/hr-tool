from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class CandidateVersionBase(BaseModel):
    profile_json: Dict[str, Any]

class CandidateVersionResponse(CandidateVersionBase):
    id: UUID
    candidate_id: UUID
    version_number: int
    is_current: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CandidateBase(BaseModel):
    pass

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: UUID
    source_file: Optional[str] = None
    created_at: datetime
    versions: List[CandidateVersionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class CandidateUpdate(BaseModel):
    profile_json: Dict[str, Any]
