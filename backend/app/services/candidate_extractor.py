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
        "tóm tắt", "tóm tắt bản thân", "mục tiêu", "mục tiêu nghề nghiệp", "về bản thân", "giới thiệu", "giới thiệu bản thân", "tổng quan", "định hướng nghề nghiệp",
        "summary", "professional summary", "executive summary", "objective", "career objective", "personal statement", "about me", "profile", "brief", "introduction", "personal summary", "career profile"
    ],
    "skills": [
        "kỹ năng", "các kỹ năng", "kĩ năng", "kỹ năng chuyên môn", "điểm mạnh", "sở trường", "kỹ năng mềm", "năng lực cốt lõi", "kỹ năng kỹ thuật",
        "skills", "core competencies", "expertise", "technical skills", "soft skills", "professional skills", "key skills", "it skills", "computer skills", "competencies", "proficiencies", "skill set", "areas of expertise"
    ],
    "work_experiences": [
        "kinh nghiệm làm việc", "kinh nghiệm", "lịch sử làm việc", "quá trình công tác", "kinh nghiệm chuyên môn", "quá trình làm việc",
        "experience", "work experience", "professional experience", "employment", "employment history", "work history", "career history", "professional background", "relevant experience", "career experience"
    ],
    "educations": [
        "học vấn", "trình độ học vấn", "trình độ", "đào tạo", "quá trình học tập", "quá trình đào tạo", "bằng cấp", "nền tảng học vấn",
        "education", "educational background", "academic background", "academics", "studies", "qualifications", "academic history"
    ],
    "projects": [
        "dự án", "dự án cá nhân", "sản phẩm", "các dự án đã tham gia", "dự án nổi bật", "nghiên cứu khoa học",
        "projects", "personal projects", "academic projects", "open source", "portfolio", "key projects", "selected projects", "project experience"
    ],
    "activities": [
        "hoạt động", "hoạt động ngoại khóa", "tình nguyện", "hoạt động xã hội", "sở thích", "thành viên", "câu lạc bộ",
        "activities", "extracurricular", "volunteering", "volunteer experience", "hobbies", "interests", "community service", "leadership"
    ],
    "certifications": [
        "chứng chỉ", "giấy chứng nhận", "bằng cấp phụ", "chứng nhận chuyên môn",
        "certifications", "certificates", "licenses", "accreditations", "professional development"
    ],
    "awards": [
        "giải thưởng", "thành tích", "danh hiệu", "thành tựu", "khen thưởng", "cuộc thi",
        "awards", "honors", "achievements", "recognitions", "accomplishments", "scholarships"
    ],
    "languages": [
        "ngoại ngữ", "languages", "ngôn ngữ",
    ],
    "interests": [
        "sở thích", "interests", "hobbies",
    ],
    "references": [
        "người tham chiếu", "tham chiếu", "người giới thiệu",
        "references", "referees"
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

    # Strip common list prefixes like "A. ", "1. ", "I. ", "1/ " and trailing colons/dashes
    clean_lower = re.sub(r'^(?:[ivxlcdm]+|[a-z]|\d{1,2})[\.\/\)]\s+', '', stripped_lower)
    clean_lower = re.sub(r'[:\-]+$', '', clean_lower).strip()

    # Exact match
    if clean_lower in _KW_MAP:
        return _KW_MAP[clean_lower]

    # Starts with or contains keyword
    for kw, key in sorted(_KW_MAP.items(), key=lambda x: -len(x[0])):
        if kw in clean_lower and len(clean_lower) <= len(kw) + 20:
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



def _extract_basic_info(combined_text: str, left_text: str, parsed: dict, all_sections: dict) -> dict:
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
    # Reconstruct from raw_chars to preserve Vietnamese diacritics perfectly,
    # adding spaces based on bounding box distance.
    chars = parsed.get("raw_chars", [])
    if chars:
        size_groups: dict[float, list[dict]] = {}
        for c in chars:
            t = c.get("text", "")
            if t and (t.isalpha() or t.isspace() or re.match(r"[\w\u00C0-\u024F\u1EA0-\u1EF9\s]", t)):
                size = round(c.get("size", 10), 1)
                size_groups.setdefault(size, []).append(c)
        if size_groups:
            max_size = max(size_groups.keys())
            if max_size > 13:
                max_chars = size_groups[max_size]
                # Sort by approximate line (y0), then x0
                max_chars.sort(key=lambda c: (round(c.get("top", 0) / 5) * 5, c.get("x0", 0)))
                
                candidate_name = ""
                last_x1 = -1
                for c in max_chars:
                    t = c.get("text", "")
                    if not t.strip(): continue
                    # Add space if gap > 2.5px (heuristic for missing space char)
                    if last_x1 != -1 and c.get("x0", 0) - last_x1 > 2.5:
                        candidate_name += " "
                    candidate_name += t
                    last_x1 = c.get("x1", 0)
                
                candidate_name = re.sub(r'\s+', ' ', candidate_name).strip()
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


    # 7. Orphan text fallback for Summary
    header_lines = all_sections.get("header", [])
    orphan_text = []
    
    # Build set of name words for filtering (prevent name from leaking into summary)
    full_name = info.get("full_name", "")
    name_words = set(w.lower() for w in full_name.split() if len(w) > 1) if full_name else set()
    
    for line in header_lines:
        line_clean = re.sub(r'\s+', ' ', line).strip()  # normalize multiple spaces
        if not line_clean: continue
        # Skip if it's too short (likely name or title)
        if len(line_clean) < 15: continue
        # Skip if it contains email or phone
        if info["email"] and info["email"] in line_clean: continue
        if info["phone"] and info["phone"] in line_clean.replace(" ", ""): continue
        # Skip if it looks like an address or url
        if info["address"] and info["address"] in line_clean: continue
        if info["linkedin"] and info["linkedin"] in line_clean: continue
        if info["website"] and info["website"] in line_clean: continue
        # Skip lines that are predominantly the candidate's name
        # (e.g., "Đào Quang Thuận Backend Engineer" starts with the name)
        if name_words:
            line_words = set(w.lower() for w in line_clean.split() if len(w) > 1)
            name_overlap = len(name_words & line_words)
            if name_overlap >= len(name_words) * 0.6:  # >60% of name words present
                continue
        
        orphan_text.append(line_clean)
        
    info["summary"] = " ".join(orphan_text).strip()
    
    # Fallback: if still no summary, find the first long paragraph in header
    # (handles CVs where summary has no section header at all)
    if not info["summary"]:
        for line in header_lines:
            line_clean = line.strip()
            if len(line_clean) > 60 and ' ' in line_clean:
                # Must not be contact info, URL, or date
                if not re.search(r'https?://|@|\+84|0[3-9]\d{8}|\d{4}\s*[-–—]\s*\d{4}', line_clean):
                    # Must not be predominantly the candidate's name
                    if name_words:
                        line_words = set(w.lower() for w in line_clean.split() if len(w) > 1)
                        if len(name_words & line_words) >= len(name_words) * 0.6:
                            continue
                    info["summary"] = line_clean
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

def _is_pure_date_line(line: str) -> bool:
    """True nếu line CHỈ chứa date range, không có text khác.
    Dùng để phát hiện các CV tiếng Anh có format: Date → School → Major.
    Ví dụ: '2022 - 2026' → True, 'ABC University 2022-2026' → False.
    """
    stripped = line.strip()
    # Remove date range pattern
    without_date = re.sub(
        r'(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\d{4}|nay|present|now|hiện tại)',
        '', stripped, flags=re.IGNORECASE
    ).strip(' -–—|•·')
    # Also handle single year lines like "2022" or "(2022 - 2026)"
    without_year = re.sub(r'[()\s\d\-–—/]', '', without_date).strip()
    return len(without_year) < 3  # Còn lại < 3 ký tự không phải số/dấu → thuần date

def _parse_candidate_subcontents(lines: list[str]) -> list[dict]:
    """Parse raw lines into structured blocks (Title, Date, Bullets).
    
    Fix: Handles 'date-first' format common in English CVs:
        2022 - 2026              ← date line (buffered, not used as title)
        Ho Chi Minh University   ← actual title
        Computer Science         ← major/subtitle
    """
    blocks = []
    current_block = None
    pending_date = ""  # Buffer for date-first lines (CV EN format)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        is_bullet = line.startswith(('-', '*', '•', '·', '▪', 'v', '✓', '>', '+'))
        has_date = bool(re.search(r'(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\d{4}|nay|present|now|hiện tại)', line, re.IGNORECASE))
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', line))
        
        is_property = line.lower().startswith(("gpa", "điểm", "kết quả", "mô tả", "description", "achievements", "thành tựu"))
        
        # "Link repository:", "GitHub:", "URL:" etc. are metadata labels, not block titles
        is_link_label = bool(re.match(
            r'^(link|github|url|repo|repository|website|xem thêm|dự án|project link)',
            line.lower()
        ))
        is_new_entry = False
        if not is_bullet and not is_property and not is_link_label:
            if current_block is None:
                is_new_entry = True
            else:
                if has_date or has_year:
                    if current_block.get("date"):
                        is_new_entry = True
                    else:
                        is_new_entry = False
                else:
                    if len(current_block.get("bullets", [])) > 0:
                        if len(line) < 50 and not line.endswith('.') and not line[0].islower():
                            is_new_entry = True
                        else:
                            is_new_entry = False
                    else:
                        is_new_entry = False
                
        if is_new_entry:
            # Buffer trailing dates or standalone dates for blocks
            if (has_date or has_year) and _is_pure_date_line(line):
                if current_block is not None and not current_block["date"]:
                    current_block["date"] = line
                else:
                    pending_date = line
                continue
            
            current_block = {
                "title": line,
                "date": pending_date,  # Attach buffered date (if any) to the new block
                "bullets": [],
                "raw_text": line + "\n"
            }
            pending_date = ""  # Reset buffer
            blocks.append(current_block)
            # If current line also has a date (and no pending_date was used), set it
            if (has_date or has_year) and not current_block["date"]:
                current_block["date"] = line
        elif is_bullet or is_link_label:
            if current_block is None:
                # Bullet before any block — create anonymous block
                current_block = {"title": "", "date": pending_date, "bullets": [], "raw_text": ""}
                pending_date = ""
                blocks.append(current_block)
            current_block["bullets"].append(line.lstrip('-*•·▪v✓>+ ').strip())
            current_block["raw_text"] += line + "\n"
        else:
            if current_block is None:
                continue
            if not current_block["title"]:
                current_block["title"] = line
            elif not current_block["date"] and (has_date or has_year):
                current_block["date"] = line
            else:
                if not current_block["date"] and len(current_block["bullets"]) == 0 and len(line) < 50:
                    current_block["title"] += " - " + line
                else:
                    current_block["bullets"].append(line)
            current_block["raw_text"] += line + "\n"
                
    return blocks


def _extract_work_experiences(sections: dict, right_sections: dict, all_projects: list) -> list[dict]:
    lines = sections.get("work_experiences") or right_sections.get("work_experiences") or []
    if not lines:
        return []

    blocks = _parse_candidate_subcontents(lines)
    experiences = []
    last_company = ""
    
    company_kws = ["công ty", "tnhh", "jsc", "corp", "inc", "cổ phần", "ltd", "group", "holdings", "company"]
    project_kws = ["mục tiêu:", "công nghệ:", "link", "github", "website"]
    role_kws = ["developer", "engineer", "intern", "manager", "staff", "chuyên viên", "nhân viên", "lead", "head", "director", "designer", "tester", "qa", "qc", "thực tập", "phát triển"]
    
    for b in blocks:
        start, end = _parse_date_range(b["date"]) if b["date"] else ("", "")
        desc = "\n".join(b["bullets"])
        title = b["title"]
        
        is_project = False
        desc_lower = desc.lower()
        if any(kw in desc_lower for kw in project_kws):
            if not any(kw in title.lower() for kw in company_kws):
                is_project = True
                
        if is_project:
            # Replace multiple spaces with ' - ' for better splitting if columns merged
            title_clean = re.sub(r'\s{2,}', ' - ', title)
            title_parts = [p.strip() for p in title_clean.split(" - ") if p.strip()]
            proj_name = title_parts[0] if len(title_parts) > 0 else ""
            proj_role = title_parts[1] if len(title_parts) > 1 else ""
            
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

        title_clean = re.sub(r'\s{2,}', ' - ', title)
        title_parts = [p.strip() for p in title_clean.split(" - ") if p.strip()]
        company = ""
        role = ""
        
        for part in title_parts:
            part_lower = part.lower()
            if any(kw in part_lower for kw in company_kws):
                company = part
            elif any(kw in part_lower for kw in role_kws):
                role = part
        
        if not company and not role:
            if len(title_parts) >= 2:
                company = title_parts[0]
                role = title_parts[1]
            elif len(title_parts) == 1:
                part = title_parts[0]
                # Inherit last_company if it looks like a sub-role/project under the same company
                if last_company and not any(kw in part.lower() for kw in company_kws):
                    company = last_company
                    role = part
                else:
                    company = part
        elif company and not role:
            for p in title_parts:
                if p != company:
                    role = p
                    break
        elif role and not company:
            for p in title_parts:
                if p != role:
                    company = p
                    break
                    
        if company:
            last_company = company
        
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
        title = re.sub(r'\s{2,}', ' - ', title)
        
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

        # Filter out clearly invalid education blocks:
        # User request: "chỉ cần detect dòng University hoặc các cụm từ liên quan đến trường"
        # Must contain at least one school keyword in the entire block (title + bullets)
        block_text = b["title"].lower() + " " + " ".join(b["bullets"]).lower()
        if not any(kw in block_text for kw in school_kws):
            continue
            
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


def _extract_awards(sections: dict, right_sections: dict) -> list[dict]:
    lines = sections.get("awards") or right_sections.get("awards") or []
    if not lines:
        return []
        
    blocks = _parse_candidate_subcontents(lines)
    results = []
    for b in blocks:
        results.append({
            "name": b["title"],
            "organization": "",
            "date": b["date"]
        })
    return results


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

    basic_info = _extract_basic_info(combined_text, left_text, parsed, all_sections)
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
        "awards": _extract_awards(right_sections, all_sections),
        "languages": _extract_languages(right_sections, all_sections),
        "projects": projects,
        "activities": _extract_activities(right_sections, all_sections),
    }

    # ── Post-processing: Move certs/awards accidentally caught in educations ──
    filtered_educations = []
    for edu in profile["educations"]:
        text_content = f"{edu.get('school', '')} {edu.get('major', '')} {edu.get('description', '')}".lower()
        # Màng lọc chứng chỉ
        if any(kw in text_content for kw in ["chứng chỉ", "certificate", "ielts", "toeic", "toefl", "aws", "ccna", "gcp", "azure"]):
            title = edu.get("school", "")
            if edu.get("major"): title += f" - {edu.get('major')}"
            profile["certifications"].append({"name": title.strip(" -"), "organization": ""})
            continue
        # Màng lọc giải thưởng
        if any(kw in text_content for kw in ["giải nhất", "giải nhì", "giải ba", "giải khuyến khích", "champion", "olympic", "hackathon", "award"]):
            title = edu.get("school", "")
            if edu.get("major"): title += f" - {edu.get('major')}"
            profile["awards"].append({"name": title.strip(" -"), "organization": "", "date": ""})
            continue
            
        filtered_educations.append(edu)
        
    profile["educations"] = filtered_educations

    return profile
