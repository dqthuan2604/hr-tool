"""
template_extractor.py
Extracts CV template schema (layout, fonts, colors, sections) from a parsed PDF.
Uses column-aware parsing data from file_parser.py and a keyword whitelist to
correctly identify only real CV section headers.
"""
import collections
import re
import statistics


# ─────────────────────────────────────────────
# Whitelist of known CV section headers
# Only lines matching these are considered sections
# ─────────────────────────────────────────────
KNOWN_SECTION_KEYWORDS = [
    # Vietnamese
    "thông tin cá nhân", "thông tin liên hệ", "thông tin thêm",
    "mục tiêu nghề nghiệp", "mục tiêu", "tóm tắt",
    "học vấn", "trình độ học vấn", "trình độ",
    "kinh nghiệm làm việc", "kinh nghiệm",
    "kỹ năng", "các kỹ năng", "kĩ năng", "kỹ năng chuyên môn",
    "dự án", "dự án cá nhân",
    "hoạt động", "hoạt động ngoại khóa",
    "chứng chỉ", "giải thưởng", "danh hiệu",
    "ngoại ngữ",
    "sở thích",
    "tham khảo", "người tham khảo",
    "thành tích",
    # English
    "personal information", "contact", "contact information", "profile",
    "career objective", "objective", "summary", "career goal",
    "education", "educational background", "academics",
    "work experience", "experience", "employment", "professional experience",
    "skills", "technical skills", "skill set", "core competencies",
    "projects", "personal projects",
    "activities", "extracurricular",
    "certifications", "certificates", "awards",
    "languages",
    "interests", "hobbies",
    "references",
]

# Section key mapping
_KEY_MAP = {
    "thông tin cá nhân": "basic_info", "thông tin liên hệ": "basic_info",
    "thông tin thêm": "basic_info", "contact": "basic_info",
    "personal information": "basic_info", "profile": "basic_info",
    "contact information": "basic_info",
    "mục tiêu nghề nghiệp": "objective", "mục tiêu": "objective",
    "career objective": "objective", "objective": "objective",
    "summary": "objective", "career goal": "objective", "tóm tắt": "objective",
    "học vấn": "educations", "trình độ học vấn": "educations", "trình độ": "educations",
    "education": "educations", "educational background": "educations",
    "academics": "educations",
    "kinh nghiệm làm việc": "work_experiences", "kinh nghiệm": "work_experiences",
    "work experience": "work_experiences", "experience": "work_experiences",
    "employment": "work_experiences", "professional experience": "work_experiences",
    "kỹ năng": "skills", "các kỹ năng": "skills", "kĩ năng": "skills",
    "kỹ năng chuyên môn": "skills", "skills": "skills",
    "technical skills": "skills", "skill set": "skills",
    "core competencies": "skills",
    "dự án": "projects", "dự án cá nhân": "projects",
    "projects": "projects", "personal projects": "projects",
    "hoạt động": "activities", "hoạt động ngoại khóa": "activities",
    "activities": "activities", "extracurricular": "activities",
    "chứng chỉ": "certifications", "certifications": "certifications",
    "certificates": "certifications", "awards": "awards",
    "giải thưởng": "awards", "danh hiệu": "awards",
    "ngoại ngữ": "languages", "languages": "languages",
    "sở thích": "interests", "interests": "interests", "hobbies": "interests",
    "tham khảo": "references", "references": "references",
    "thành tích": "achievements",
}


def _is_cv_section_header(text: str) -> str | None:
    """
    Returns the section key if text matches a known CV section header, else None.
    Requires:
    - text is short (< 55 chars)
    - text starts with or equals a known keyword
    - text is not a bullet point or sentence
    """
    text_lower = text.strip().lower()

    # Skip bullet points and long sentences
    if text_lower.startswith(("•", "-", "*", "nguồn", "http")):
        return None
    if len(text_lower) > 55:
        return None

    # Exact match
    if text_lower in _KEY_MAP:
        return _KEY_MAP[text_lower]

    # Must START with or BE a known keyword (not contain it mid-sentence)
    for keyword in sorted(KNOWN_SECTION_KEYWORDS, key=len, reverse=True):
        kw_lower = keyword.lower()
        if text_lower == kw_lower:
            return _KEY_MAP.get(kw_lower, "basic_info")
        # Allow starting with keyword + colon or nothing
        if text_lower.startswith(kw_lower) and len(text_lower) <= len(kw_lower) + 5:
            return _KEY_MAP.get(kw_lower, "basic_info")

    return None


def _looks_like_date(text: str) -> bool:
    """Return True if text looks like a date or date range (not a section header)."""
    return bool(re.search(
        r"\b\d{2}/\d{4}\b|\b\d{4}\s*[-–]\s*\d{4}\b|\bnay\b|\bpresent\b",
        text, re.IGNORECASE
    ))


def extract_template_schema(parsed: dict) -> dict:
    schema = {
        "layout": {"type": "grid", "columns": ["100%"]},
        "colors": {
            "primary": "#000000",
            "accent": "#000000",
            "background": "#ffffff",
            "text": "#000000",
        },
        "fonts": {
            "heading": {"family": "Arial", "size": 14, "weight": "bold"},
            "body": {"family": "Arial", "size": 11, "weight": "normal"},
        },
        "sections": [],
    }

    if parsed["type"] != "pdf":
        return schema

    chars = parsed.get("raw_chars", [])
    if not chars:
        return schema

    # 1. Colors
    def _rgb_to_hex(color):
        if not color: return None
        if isinstance(color, (tuple, list)):
            if len(color) >= 3:
                r, g, b = color[:3]
                if isinstance(r, float) and r <= 1.0 and g <= 1.0 and b <= 1.0:
                    r, g, b = int(r * 255), int(g * 255), int(b * 255)
                elif isinstance(r, (int, float)):
                    r, g, b = int(r), int(g), int(b)
                return f"#{r:02x}{g:02x}{b:02x}".lower()
            elif len(color) == 1:
                v = color[0]
                if isinstance(v, float) and v <= 1.0:
                    v = int(v * 255)
                elif isinstance(v, (int, float)):
                    v = int(v)
                return f"#{v:02x}{v:02x}{v:02x}".lower()
        elif isinstance(color, (int, float)):
            v = color
            if isinstance(v, float) and v <= 1.0:
                v = int(v * 255)
            else:
                v = int(v)
            return f"#{v:02x}{v:02x}{v:02x}".lower()
        return None

    colors_list = [_rgb_to_hex(c.get("non_stroking_color")) for c in chars]
    colors = collections.Counter(c for c in colors_list if c)
    
    if colors:
        # Ignore white and black occasionally if there are other colors, but for simplicity:
        most_common = colors.most_common(4)
        schema["colors"]["text"] = most_common[0][0]
        if len(most_common) > 1:
            schema["colors"]["primary"] = most_common[1][0]

    # 2. Font size statistics
    sizes = [c.get("size", 11) for c in chars]
    median_size = statistics.median(sizes) if sizes else 11
    schema["fonts"]["body"]["size"] = median_size

    # 3. Column layout — use file_parser's column detection if available
    has_columns = parsed.get("has_columns", False)
    column_texts = parsed.get("column_texts", [])

    # If column split was detected, use that for layout %
    if has_columns and column_texts and column_texts[0].get("split_x"):
        split_x = column_texts[0]["split_x"]
        pages = parsed.get("pages", [])
        page_width = pages[0].get("page_width", 595) if pages else 595
        col1_pct = int((split_x / page_width) * 100)
        schema["layout"]["columns"] = [f"{col1_pct}%", f"{100 - col1_pct}%"]
    else:
        # Fallback: derive from raw_chars x0 distribution
        split_x = _detect_layout_split(chars)
        if split_x:
            page_width = max((c.get("x1", 600) for c in chars), default=600)
            col1_pct = int((split_x / page_width) * 100)
            schema["layout"]["columns"] = [f"{col1_pct}%", f"{100 - col1_pct}%"]

    # 4. Section detection
    has_columns = parsed.get("has_columns", False)
    column_texts = parsed.get("column_texts", [])

    if has_columns and column_texts:
        # Detect sections from column-aware text (avoids interleaving issues)
        sections = _detect_sections_from_text(parsed, schema)
    else:
        # Single column: use raw_chars visual scoring
        sections = _detect_sections(chars, median_size, schema)

    # 5. Assign column to each section
    # Sections from _detect_sections_from_text already have column set correctly.
    # Sections from _detect_sections use _x0 as temp column indicator.
    for s in sections:
        if "_x0" in s:
            # raw_chars based detection: compute column from _x0
            if has_columns and column_texts and column_texts[0].get("split_x"):
                split_x_val = column_texts[0]["split_x"]
            elif len(schema["layout"]["columns"]) >= 2:
                split_x_val = _detect_layout_split(chars) or 999
            else:
                split_x_val = 999
            s["column"] = 0 if s["_x0"] < split_x_val else 1
            s.pop("_x0")
            
        # Clean up content as Template shouldn't hold candidate data
        if "content" in s:
            s.pop("content")

    schema["sections"] = sections
    return schema



def _detect_layout_split(chars: list) -> float | None:
    """Detect column split x from raw chars using gap algorithm."""
    x0_vals = sorted(set(round(c.get("x0", 0)) for c in chars if c.get("text", "").strip()))
    if len(x0_vals) < 2:
        return None

    page_width = max((c.get("x1", 600) for c in chars), default=600)
    gaps = []
    for i in range(1, len(x0_vals)):
        gap = x0_vals[i] - x0_vals[i - 1]
        gap_center = (x0_vals[i - 1] + x0_vals[i]) / 2
        if page_width * 0.10 < gap_center < page_width * 0.70:
            gaps.append((gap, x0_vals[i - 1], x0_vals[i]))

    if not gaps:
        return None

    gaps.sort(reverse=True)
    largest_gap, x_left, x_right = gaps[0]
    if largest_gap < 30:
        return None

    left_count = sum(1 for c in chars if c.get("x0", 0) <= x_left + 5 and c.get("text", "").strip())
    right_count = sum(1 for c in chars if c.get("x0", 0) >= x_right - 5 and c.get("text", "").strip())
    if left_count < 5 or right_count < 5:
        return None

    return (x_left + x_right) / 2


def _detect_sections(chars: list, median_size: float, schema: dict) -> list[dict]:
    """
    Detect section headers from chars using:
    1. Bold/larger font detection (visual cues)
    2. Keyword whitelist validation (must be a known CV section)
    """
    # Group chars by Y position
    lines: dict[float, list] = {}
    for c in chars:
        y = round(c.get("top", 0), 0)
        lines.setdefault(y, []).append(c)

    sections = []
    order = 1
    current_section = None

    for y in sorted(lines.keys()):
        line_chars = sorted(lines[y], key=lambda c: c.get("x0", 0))
        if not line_chars:
            continue

        line_text = "".join(c.get("text", "") for c in line_chars).strip()
        if not line_text or len(line_text) < 2:
            continue

        is_header = False
        if not _looks_like_date(line_text):
            first_char = line_chars[0]
            size = first_char.get("size", 11)
            is_bold = first_char.get("bold", False)
            x0 = first_char.get("x0", 0)

            # Visual scoring: must be bold or larger font
            visual_score = 0
            if is_bold:
                visual_score += 1
            if size > median_size * 1.05:
                visual_score += 1

            if visual_score >= 1 and len(line_text) <= 55:
                # WHITELIST CHECK: only accept known CV section labels
                section_key = _is_cv_section_header(line_text)
                if section_key is None and (": " in line_text or " - " in line_text):
                    # Sometimes headers have colon, but _is_cv_section_header handles it mostly
                    pass

                if section_key is not None:
                    new_sec = {
                        "key": section_key,
                        "label": line_text,
                        "order": order,
                        "_x0": x0,  # Temp, will be replaced with column index
                        "visible": True,
                        "style": {},
                        "content": ""
                    }
                    sections.append(new_sec)
                    current_section = new_sec
                    order += 1
                    is_header = True

        if not is_header and current_section is not None:
            current_section["content"] += line_text + "\n"

    return sections


def _detect_sections_from_text(parsed: dict, schema: dict) -> list[dict]:
    """
    Detect sections by scanning column-aware plain text lines for known CV section keywords.
    This avoids the raw_chars interleaving issue in multi-column PDFs.
    Each section is assigned a column index based on which column's text it appeared in.
    """
    column_texts = parsed.get("column_texts", [])
    sections = []
    order = 1

    for ct in column_texts:
        left = ct.get("left") or ""
        right = ct.get("right") or ""

        for col_idx, text in [(0, left), (1, right)]:
            if not text:
                continue
            
            current_section = None
            for line in text.splitlines():
                line = line.strip()
                if not line or len(line) < 2:
                    continue
                
                is_header = False
                if len(line) <= 55 and not _looks_like_date(line):
                    section_key = _is_cv_section_header(line)
                    if section_key is not None:
                        # Avoid exact duplicates
                        if not any(s["label"].lower() == line.lower() for s in sections):
                            new_sec = {
                                "key": section_key,
                                "label": line,
                                "order": order,
                                "column": col_idx,
                                "visible": True,
                                "style": {},
                                "content": ""
                            }
                            sections.append(new_sec)
                            current_section = new_sec
                            order += 1
                            is_header = True

                if not is_header and current_section is not None:
                    current_section["content"] += line + "\n"

    return sections
