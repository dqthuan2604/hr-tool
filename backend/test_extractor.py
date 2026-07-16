import os
import sys
sys.path.append("/app")

from app.services.file_parser import parse_file
from app.services.candidate_extractor import extract_candidate_profile

pdf_path = "/app/uploads/bbc5a4bd-ad85-4488-a3ed-2c4b4af17c68.pdf"
parsed = parse_file(pdf_path)
profile = extract_candidate_profile(parsed)

import json
print(json.dumps(profile, indent=2, ensure_ascii=False))
