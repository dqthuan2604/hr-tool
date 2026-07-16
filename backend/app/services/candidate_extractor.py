"""
candidate_extractor.py
Column-aware CV extraction using the structured parsed output from file_parser.py.
Supports both single-column and multi-column PDF layouts.
"""
import re

# ─────────────────────────────────────────────
# Vietnamese + English section keyword sets
# ─────────────────────────────────────────────
SECTION_KEYWORDS = {
    "basic_info": [
        "thông tin cá nhân", "thông tin liên hệ", "personal information",
        "contact", "contact information", "profile",
    ],
    "objective": [
        "mục tiêu nghề nghiệp", "mục tiêu", "career objective", "objective",
        "career goal", "summary", "tóm tắt", "summary of qualifications",
        "professional summary", "executive summary", "profile summary"
    ],
    "skills": [
        "kỹ năng", "các kỹ năng", "kĩ năng", "kỹ năng chuyên môn",
        "technical skills", "skills", "skill set", "core competencies",
        "công nghệ", "ngôn ngữ lập trình", "areas of expertise", "key skills"
    ],
    "work_experiences": [
        "kinh nghiệm làm việc", "kinh nghiệm", "work experience",
        "experience", "employment", "work history",
        "professional experience", "career experience",
    ],
    "educations": [
        "học vấn", "trình độ học vấn", "trình độ", "education",
        "educational background", "academic background", "academics",
    ],
    "projects": [
        "dự án", "dự án cá nhân", "projects", "personal projects",
        "project experience", "nghiên cứu khoa học",
    ],
    "activities": [
        "hoạt động", "hoạt động ngoại khóa", "activities",
        "extracurricular", "volunteer", "thành viên", "câu lạc bộ",
        "cuộc thi", "giải thưởng", "danh hiệu",
    ],
    "certifications": [
        "chứng chỉ", "certifications", "certificates",
        "awards", "giải thưởng",
    ],
    "languages": [
        "ngoại ngữ", "languages", "ngôn ngữ",
    ],
    "interests": [
        "sở thích", "interests", "hobbies",
    ],
    "additional": [
        "thông tin thêm", "additional information", "other information",
        "thông tin khác",
    ],
}

# Build flat lookup: keyword → section_key
_KW_MAP: dict[str, str] = {}
for key, kws in SECTION_KEYWORDS.items():
    for kw in kws:
        _KW_MAP[kw.lower()] = key


def _detect_section(line: str) -> str | None:
    """Return section key if the line matches a known section header, else None.
    Uses strict matching: line must BE the keyword (exact or very close).
    Avoids false positives like 'Python: Flask...' triggering 'skills'.
    """
    stripped = line.strip()
    stripped_lower = stripped.lower()

    # Must be short to be a header
    if len(stripped) > 55 or len(stripped) < 2:
        return None

    # Skip lines that are clearly content (bullets, sentences with many words)
    if stripped.startswith(("•", "-", "*")) or stripped.count(" ") > 6:
        return None

    # Skip lines with dates (they're content lines like "SMART-HOME-WEBSITE 02/2024...")
    if re.search(r"\d{1,2}/\d{4}|\d{4}\s*[-–—]\s*(\d{4}|nay)", stripped, re.IGNORECASE):
        return None

    # Strip common list prefixes like "A. ", "1. ", "I. ", "1/ "
    clean_lower = re.sub(r'^(?:[ivxlcdm]+|[a-z]|\d{1,2})[\.\/\)]\s+', '', stripped_lower).strip()

    # Exact match
    if clean_lower in _KW_MAP:
        return _KW_MAP[clean_lower]

    # Starts with keyword — only if line is NOT significantly longer (max 4 extra chars for colon/space)
    for kw, key in sorted(_KW_MAP.items(), key=lambda x: -len(x[0])):
        if clean_lower.startswith(kw) and len(clean_lower) <= len(kw) + 4:
            return key

    return None


def _split_into_sections(text: str) -> dict[str, list[str]]:
    """
    Split raw text into sections based on keyword detection.
    Returns dict mapping section_key → list of content lines.
    """
    lines = [l for l in text.split("\n")]
    sections: dict[str, list[str]] = {}
    current_section = "header"
    sections[current_section] = []

    for line in lines:
        key = _detect_section(line)
        if key and len(line.strip()) < 55:
            current_section = key
            if current_section not in sections:
                sections[current_section] = []
        else:
            if line.strip():
                sections.setdefault(current_section, []).append(line)

    return sections


def extract_candidate_profile(parsed: dict) -> dict:
    """
    Trích xuất thông tin ứng viên từ dữ liệu PDF đã parse.
    Sử dụng column_texts nếu có (multi-column PDF).
    """
    raw_text = parsed.get("raw_text", "")
    has_columns = parsed.get("has_columns", False)
    column_texts = parsed.get("column_texts", [])

    # Build per-column text for smarter extraction
    left_text = ""
    right_text = ""

    if has_columns and column_texts:
        for ct in column_texts:
            left_text += (ct.get("left") or "") + "\n"
            right_text += (ct.get("right") or "") + "\n"
        # Combined text in logical reading order: left col + right col
        combined_text = left_text.strip() + "\n\n" + right_text.strip()
    else:
        combined_text = raw_text
        left_text = raw_text
        right_text = raw_text

    # Split into named sections (per source)
    all_sections = _split_into_sections(combined_text)
    left_sections = _split_into_sections(left_text) if has_columns else all_sections
    right_sections = _split_into_sections(right_text) if has_columns else all_sections

    profile = {
        "basic_info": _extract_basic_info(combined_text, left_text, parsed),
        "objective": _extract_objective(right_sections, all_sections),
        # Skills are in the sidebar (left column)
        "skills": _extract_skills(left_sections, all_sections),
        # Main content sections are in the right column (or full text for single-col)
        "work_experiences": _extract_work_experiences(right_sections, all_sections),
        "educations": _extract_educations(right_sections, all_sections),
        "certifications": _extract_certifications(all_sections),
        "languages": _extract_languages(all_sections),
        "projects": _extract_projects(right_sections, all_sections),
        "activities": _extract_activities(right_sections, all_sections),
    }
    return profile


def _extract_basic_info(combined_text: str, left_text: str, parsed: dict) -> dict:
    info = {
        "full_name": "",
        "email": "",
        "phone": "",
        "address": "",
        "linkedin": "",
        "website": "",
        "summary": "",
    }

    # 1. Email
    email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", combined_text)
    if email_match:
        info["email"] = email_match.group(0)

    # 2. Phone (VN patterns)
    phone_match = re.search(
        r"(?:^|\s)(0[3-9]\d{8}|\+84[3-9]\d{8}|84[3-9]\d{8}|0\d{2}[\s.\-]?\d{3}[\s.\-]?\d{4})",
        combined_text, re.MULTILINE
    )
    if phone_match:
        raw_phone = re.sub(r"[\s.\-]", "", phone_match.group(1))
        if raw_phone.startswith("84"):
            raw_phone = "+" + raw_phone
        elif raw_phone.startswith("0"):
            raw_phone = "+84" + raw_phone[1:]
        info["phone"] = raw_phone

    # 3. LinkedIn
    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+", combined_text, re.IGNORECASE
    )
    if linkedin_match:
        info["linkedin"] = linkedin_match.group(0)

    # 4. GitHub / Website
    github_match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+", combined_text, re.IGNORECASE
    )
    if github_match:
        info["website"] = github_match.group(0)

    # 5. Address (Vietnamese city/street patterns)
    addr_match = re.search(
        r"(?:TP\.|Thành phố|Quận|Huyện|Đường|P\.|Phường)[^\n]{3,50}",
        combined_text, re.IGNORECASE
    )
    if addr_match:
        info["address"] = addr_match.group(0).strip()

    # 6. Full name — prefer chars with largest font size
    chars = parsed.get("raw_chars", [])
    if chars:
        size_groups: dict[float, list[str]] = {}
        for c in chars:
            t = c.get("text", "")
            if t and (t.isalpha() or t.isspace() or re.match(r"[\w\u00C0-\u024F\u1EA0-\u1EF9\s]", t)):
                size = round(c.get("size", 10), 1)
                size_groups.setdefault(size, []).append(t)
        if size_groups:
            max_size = max(size_groups.keys())
            if max_size > 13:
                candidate_name = "".join(size_groups[max_size]).strip()
                # Clean up multiple spaces
                candidate_name = re.sub(r'\s+', ' ', candidate_name)
                # Validate: name should look like a person name (2-5 words, not all digits)
                if candidate_name and not candidate_name.isdigit() and len(candidate_name) > 3:
                    info["full_name"] = candidate_name

    # Fallback: first line of left_text that looks like a name
    if not info["full_name"] and left_text:
        for line in left_text.splitlines():
            line = line.strip()
            # Name: 2-4 words, each starting with uppercase, total < 50 chars
            words = line.split()
            if (2 <= len(words) <= 5 and len(line) < 50
                    and all(w[0].isupper() or ord(w[0]) > 127 for w in words if w)
                    and not any(c.isdigit() for c in line)):
                info["full_name"] = line
                break

    return info


def _extract_objective(sections: dict, right_sections: dict) -> str:
    """Extract career objective/summary as a string."""
    content = sections.get("objective") or right_sections.get("objective") or []
    return " ".join(l.strip() for l in content if l.strip())


def _get_section_lines(sections: dict, *fallbacks: dict) -> list[str]:
    """Return lines for a section, searching through section dicts."""
    for sec_dict in (sections, *fallbacks):
        for key, lines in sec_dict.items():
            if lines:
                return lines
    return []


def _extract_skills(sections: dict, left_sections: dict) -> list[dict]:
    """
    Extract skills as [{category, items}].
    Handles format:
        PYTHON:
          flask, flask-sqlalchemy
        C#
          Tìm hiểu về .Net Core...
    """
    lines = sections.get("skills") or left_sections.get("skills") or []
    if not lines:
        return []

    results = []
    current_category = "General"
    current_items: list[str] = []

    def flush():
        if current_items:
            # Clean up items: split by comma if there are embedded commas
            final_items = []
            for item in current_items:
                if "," in item or ";" in item:
                    final_items.extend([s.strip().lstrip("•-").strip() for s in re.split(r"[,;]", item) if s.strip()])
                else:
                    item_clean = item.strip().lstrip("•-").strip()
                    if item_clean:
                        final_items.append(item_clean)
            if final_items:
                results.append({"category": current_category, "items": final_items})

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Category line: short, optionally ends with ":"
        is_category = (
            len(line) < 35
            and not line.startswith("•")
            and not line.startswith("-")
            and (line.endswith(":") or (line.isupper() and len(line.split()) <= 4)
                 or re.match(r"^[A-ZÀ-Ỹa-zà-ỹ#+\.]{1,25}:$", line))
        )

        if is_category:
            flush()
            current_category = line.rstrip(":")
            current_items = []
        else:
            # Check for continuation of previous item
            is_continuation = False
            if current_items and not line.startswith(("•", "-")):
                last_item = current_items[-1]
                # If line starts with lowercase, or previous line ended with comma
                if line[0].islower() or last_item.endswith(",") or last_item.endswith(";"):
                    is_continuation = True
                # Or if last item is a long sentence and this line doesn't look like a short keyword
                elif len(last_item) > 25 and " " in last_item and len(line) > 15 and " " in line:
                    is_continuation = True

            if is_continuation:
                # Remove trailing comma if it's there just for line wrapping
                if current_items[-1].endswith(",") or current_items[-1].endswith(";"):
                    current_items[-1] += " " + line
                else:
                    current_items[-1] += " " + line
            else:
                current_items.append(line)

    flush()
    return results


def _parse_date_range(text: str) -> tuple[str, str]:
    """Extract start and end date from strings like '02/2024 - 12/2024' or '09/2023 - nay'."""
    match = re.search(
        r"(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\d{4}|nay|present|now|hiện tại)",
        text, re.IGNORECASE
    )
    if match:
        return match.group(1), match.group(2)
    # Single year
    year_match = re.search(r"\b(20\d{2})\b", text)
    if year_match:
        return year_match.group(1), ""
    return "", ""

def _strip_date_range(text: str) -> str:
    """Remove date range pattern from a line."""
    return re.sub(
        r"(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\d{4}|nay|present|now|hiện tại)",
        "", text, flags=re.IGNORECASE
    ).strip()

def _parse_candidate_subcontents(lines: list[str]) -> list[dict]:
    """Parse raw lines into structured blocks (Title, Date, Bullets)."""
    blocks = []
    current_block = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        is_bullet = line.startswith(('-', '*', '•', '·', '▪', 'v', '✓', '>', '+'))
        
        if is_bullet:
            if current_block is None:
                current_block = {"title": "", "date": "", "bullets": [], "raw_text": ""}
                blocks.append(current_block)
            current_block["bullets"].append(line.lstrip('-*•·▪v✓>+ ').strip())
            current_block["raw_text"] += line + "\n"
        else:
            if current_block is None or len(current_block.get("bullets", [])) > 0:
                current_block = {"title": line, "date": "", "bullets": [], "raw_text": line + "\n"}
                blocks.append(current_block)
            else:
                if not current_block["title"]:
                    current_block["title"] = line
                elif not current_block["date"] and (re.search(r'\d{4}', line) or 'hiện tại' in line.lower() or 'nay' in line.lower()):
                    current_block["date"] = line
                else:
                    if not current_block["date"]:
                        current_block["title"] += " - " + line
                current_block["raw_text"] += line + "\n"
                
    return blocks


def _extract_work_experiences(sections: dict, right_sections: dict, all_projects: list) -> list[dict]:
    lines = sections.get("work_experiences") or right_sections.get("work_experiences") or []
    if not lines:
        return []

    blocks = _parse_candidate_subcontents(lines)
    experiences = []
    
    company_kws = ["công ty", "tnhh", "jsc", "corp", "inc", "cổ phần", "ltd", "group", "holdings", "company"]
    project_kws = ["mục tiêu:", "công nghệ:", "link", "github", "website"]
    
    for b in blocks:
        start, end = _parse_date_range(b["date"]) if b["date"] else ("", "")
        desc = "\n".join(b["bullets"])
        title = b["title"]
        
        # Check if it's actually a project
        is_project = False
        desc_lower = desc.lower()
        if any(kw in desc_lower for kw in project_kws):
            # If title has no company keywords
            if not any(kw in title.lower() for kw in company_kws):
                is_project = True
                
        if is_project:
            title_parts = title.split(" - ", 1)
            proj_name = title_parts[0].strip() if len(title_parts) > 0 else ""
            proj_role = title_parts[1].strip() if len(title_parts) > 1 else ""
            
            # Find URLs
            url = ""
            urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', desc)
            if urls:
                url = urls[0]
                
            all_projects.append({
                "name": proj_name,
                "role": proj_role,
                "start_date": start,
                "end_date": end,
                "url": url,
                "description": desc
            })
            continue

        title_parts = title.split(" - ", 1)
        company = ""
        role = ""
        
        # Split heuristic based on keywords or multiple lines combined as title
        title_lines = title.split("\n")
        if len(title_lines) >= 2:
            company = title_lines[0].strip()
            role = title_lines[1].strip()
        else:
            # Check for space separated company and role (e.g., "Công ty TNHH Tenomad Intern Python Developer")
            words = title.split()
            role_start = -1
            role_kws = ["developer", "engineer", "intern", "manager", "staff", "chuyên viên", "nhân viên"]
            for i, w in enumerate(words):
                if w.lower() in role_kws:
                    # found role keyword, usually role starts 1 or 2 words before this
                    role_start = max(0, i - 1)
                    if words[role_start].lower() in ["python", "java", "frontend", "backend", "fullstack", "web", "ai", "data"]:
                        # Adjust back if it's like "Python Developer"
                        pass
                    break
            
            if role_start > 1 and any(kw in " ".join(words[:role_start]).lower() for kw in company_kws):
                company = " ".join(words[:role_start])
                role = " ".join(words[role_start:])
            elif len(title_parts) > 1:
                company = title_parts[0].strip()
                role = title_parts[1].strip()
            else:
                company = title
                role = ""
        
        experiences.append({
            "company": company,
            "role": role,
            "start_date": start,
            "end_date": end,
            "description": desc
        })
    return experiences


def _extract_educations(sections: dict, right_sections: dict) -> list[dict]:
    lines = sections.get("educations") or right_sections.get("educations") or []
    if not lines:
        return []

    blocks = _parse_candidate_subcontents(lines)
    educations = []
    
    school_kws = ["đại học", "university", "trường", "college", "academy", "viện"]
    
    for b in blocks:
        start, end = _parse_date_range(b["date"]) if b["date"] else ("", "")
        title = b["title"]
        
        school = ""
        major = ""
        degree = "Cử nhân"
        
        # Multiple line title usually means "Major\nSchool"
        title_lines = title.split("\n")
        if len(title_lines) >= 2:
            if any(kw in title_lines[1].lower() for kw in school_kws):
                school = title_lines[1].strip()
                major = title_lines[0].strip()
            elif any(kw in title_lines[0].lower() for kw in school_kws):
                school = title_lines[0].strip()
                major = title_lines[1].strip()
            else:
                school = title_lines[0].strip()
                major = title_lines[1].strip()
        else:
            title_parts = title.split(" - ", 1)
            if len(title_parts) > 1:
                if any(kw in title_parts[1].lower() for kw in school_kws):
                    school = title_parts[1].strip()
                    major = title_parts[0].strip()
                else:
                    school = title_parts[0].strip()
                    major = title_parts[1].strip()
            else:
                school = title
                
        # Remove degree from major if present
        degree_kws = ["cử nhân", "kỹ sư", "thạc sĩ", "tiến sĩ", "bachelor", "master", "phd", "engineer"]
        for dk in degree_kws:
            if dk in major.lower():
                degree = major[:len(dk)].title()
                major = major[len(dk):].strip(" -:")
                break
        
        gpa = ""
        desc = "\n".join(b["bullets"])
        gpa_match = re.search(r"(?:GPA|Điểm|điểm)[:\s]*([\d.]+)", desc, re.IGNORECASE)
        if gpa_match:
            gpa = gpa_match.group(1)

        educations.append({
            "school": school,
            "degree": degree,
            "major": major,
            "start_date": start,
            "end_date": end,
            "gpa": gpa,
        })
    return educations


def _extract_projects(sections: dict, right_sections: dict) -> list[dict]:
    lines = sections.get("projects") or right_sections.get("projects") or []
    if not lines:
        return []

    blocks = _parse_candidate_subcontents(lines)
    projects = []
    for b in blocks:
        start, end = _parse_date_range(b["date"]) if b["date"] else ("", "")
        title = b["title"]
        desc = "\n".join(b["bullets"])
        
        # Clean up title if it contains dates or 'Duration:'
        title = re.sub(r'duration:\s*\d{1,2}/\d{4}.*', '', title, flags=re.IGNORECASE).strip()
        
        title_parts = title.split(" - ", 1)
        name = title_parts[0].strip() if len(title_parts) > 0 else ""
        role = title_parts[1].strip() if len(title_parts) > 1 else ""
        
        # Find URLs
        url = ""
        urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', desc)
        if urls:
            url = urls[0]

        projects.append({
            "name": name,
            "description": desc,
            "tech_stack": [],
            "url": url,
            "start_date": start,
            "end_date": end
        })
    return projects

def _extract_skills(sections: dict, right_sections: dict) -> list[dict]:
    lines = sections.get("skills") or right_sections.get("skills") or []
    if not lines:
        return []
    
    blocks = _parse_candidate_subcontents(lines)
    skills = []
    
    if len(blocks) == 0:
        items = [line.lstrip('-*•·▪v✓>+ ').strip() for line in lines if line.strip()]
        if items:
            skills.append({
                "category": "General",
                "items": items
            })
    else:
        for b in blocks:
            cat = b["title"]
            items = b["bullets"]
            if not items and b["raw_text"]:
                items = [x.strip() for x in b["raw_text"].split('\n') if x.strip() and x.strip() != cat]
            
            skills.append({
                "category": cat or "General",
                "items": items
            })
    return skills

def _extract_certifications(sections: dict, right_sections: dict) -> list[dict]:
    lines = sections.get("certifications") or right_sections.get("certifications") or []
    if not lines:
        return []
    blocks = _parse_candidate_subcontents(lines)
    certs = []
    for b in blocks:
        start, end = _parse_date_range(b["date"]) if b["date"] else ("", "")
        certs.append({
            "name": b["title"],
            "organization": "",
            "issue_date": end or start,
            "url": ""
        })
    return certs

def _extract_languages(sections: dict, right_sections: dict) -> list[dict]:
    lines = sections.get("languages") or right_sections.get("languages") or []
    if not lines:
        return []
    blocks = _parse_candidate_subcontents(lines)
    langs = []
    for b in blocks:
        langs.append({
            "language": b["title"],
            "proficiency": "\n".join(b["bullets"])
        })
    return langs

def _extract_activities(sections: dict, right_sections: dict) -> list[dict]:
    lines = sections.get("activities") or right_sections.get("activities") or []
    if not lines:
        return []
    blocks = _parse_candidate_subcontents(lines)
    acts = []
    for b in blocks:
        start, end = _parse_date_range(b["date"]) if b["date"] else ("", "")
        acts.append({
            "organization": b["title"],
            "role": "",
            "start_date": start,
            "end_date": end,
            "description": "\n".join(b["bullets"])
        })
    return acts

def extract_candidate_profile(parsed: dict) -> dict:
    """
    Trích xuất thông tin ứng viên từ dữ liệu PDF đã parse.
    Sử dụng column_texts nếu có (multi-column PDF).
    """
    raw_text = parsed.get("raw_text", "")
    has_columns = parsed.get("has_columns", False)
    column_texts = parsed.get("column_texts", [])

    # Build per-column text for smarter extraction
    left_text = ""
    right_text = ""

    if has_columns and column_texts:
        for ct in column_texts:
            left_text += (ct.get("left") or "") + "\n"
            right_text += (ct.get("right") or "") + "\n"
        # Combined text in logical reading order: left col + right col
        combined_text = left_text.strip() + "\n\n" + right_text.strip()
    else:
        combined_text = raw_text
        left_text = raw_text
        right_text = raw_text

    # Split into named sections (per source)
    all_sections = _split_into_sections(combined_text)
    left_sections = _split_into_sections(left_text) if has_columns else all_sections
    right_sections = _split_into_sections(right_text) if has_columns else all_sections
    
    projects = []
    try:
        projects = _extract_projects(right_sections, all_sections)
    except Exception as e:
        print("Error extracting projects:", e)

    basic_info = _extract_basic_info(combined_text, left_text, parsed)
    # Map objective to basic_info.summary
    objective_text = _extract_objective(right_sections, all_sections)
    if objective_text and not basic_info.get("summary"):
        basic_info["summary"] = objective_text

    profile = {
        "basic_info": basic_info,
        # Skills are in the sidebar (left column)
        "skills": _extract_skills(left_sections, all_sections),
        # Main content sections are in the right column (or full text for single-col)
        "work_experiences": _extract_work_experiences(right_sections, all_sections, projects),
        "educations": _extract_educations(right_sections, all_sections),
        "certifications": _extract_certifications(right_sections, all_sections),
        "languages": _extract_languages(right_sections, all_sections),
        "projects": projects,
        "activities": _extract_activities(right_sections, all_sections),
    }
    return profile
