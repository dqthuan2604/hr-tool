from app.models.template import Template
from app.models.candidate import Candidate, CandidateVersion
from app.models.cv_draft import CVDraft

# Ensure Base is available for Alembic to import
from app.database import Base
