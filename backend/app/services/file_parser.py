import os
import uuid
import collections
import pdfplumber
import docx
from fastapi import UploadFile

os.makedirs(os.getenv("UPLOAD_DIR", "./uploads"), exist_ok=True)

from app.utils.storage import upload_file_to_minio, download_file_from_minio

def save_upload(file_content: bytes, filename: str) -> str:
    """Save an uploaded file to MinIO and return its minio:// URI."""
    ext = filename.split(".")[-1].lower()
    file_id = str(uuid.uuid4())
    minio_filename = f"{file_id}.{ext}"
    
    content_type = "application/pdf" if ext == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    # Upload to minio
    return upload_file_to_minio(file_content, minio_filename, content_type)

def parse_file(file_path: str) -> dict:
    """Parse a PDF or DOCX file and return structured text/char blocks."""
    # Download from minio if needed
    if file_path.startswith("minio://"):
        local_path = os.path.join("/tmp", file_path.split("/")[-1])
        download_file_from_minio(file_path, local_path)
        actual_path = local_path
    else:
        actual_path = file_path
        
    ext = actual_path.split(".")[-1].lower()
    
    try:
        if ext == "pdf":
            result = _parse_pdf(actual_path)
        elif ext == "docx":
            result = _parse_docx(actual_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
            
        return _remove_nul(result)
    finally:
        if file_path.startswith("minio://") and os.path.exists(actual_path):
            try:
                os.remove(actual_path)
            except Exception:
                pass

def _remove_nul(obj):
    if isinstance(obj, str):
        return obj.replace("\x00", "")
    elif isinstance(obj, list):
        return [_remove_nul(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: _remove_nul(v) for k, v in obj.items()}
    return obj


import re

def _normalize_text(text: str) -> str:
    """Fix word-boundary issues from PDF extraction.
    
    Some PDFs (especially English CVs) lose spaces between words during extraction.
    This applies conservative heuristics to restore word boundaries:
    - 'designedAsync' → 'designed Async' (lowercase→uppercase boundary)
    - Does NOT change Vietnamese text (diacritics protect against false splits)
    """
    if not text:
        return text
    # Split at lowercase→uppercase boundary (camelCase merge artifact)
    text = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', text)
    # Multiple spaces → single space (per line to preserve newlines)
    lines = [re.sub(r' {2,}', ' ', line) for line in text.split('\n')]
    return '\n'.join(lines)

def _reconstruct_text_from_words(page) -> str:
    """Reconstruct text from word bounding boxes instead of character encoding.
    
    Why: pdfplumber's extract_text() relies on char spacing to detect word boundaries.
    Some PDFs store no explicit space characters — spaces are implied by advance widths.
    extract_words() uses VISUAL bounding box gaps, which is encoding-independent.
    
    Result: 'samplingandbuilta500MB' -> 'sampling and built a 500MB' (proper words)
    """
    try:
        words = page.extract_words(x_tolerance=3, y_tolerance=3, keep_blank_chars=False)
    except Exception:
        return ""
    if not words:
        return ""
    
    lines = []
    current_y = None
    current_line = []
    Y_THRESHOLD = 5  # pixels: tolerance for grouping chars onto same line
    
    for word in words:
        word_top = word.get('top', 0)
        if current_y is None or abs(word_top - current_y) > Y_THRESHOLD:
            if current_line:
                # Sort words left-to-right before joining
                sorted_line = sorted(current_line, key=lambda w: w.get('x0', 0))
                lines.append(' '.join(w['text'] for w in sorted_line))
            current_line = [word]
            current_y = word_top
        else:
            current_line.append(word)
    
    if current_line:
        sorted_line = sorted(current_line, key=lambda w: w.get('x0', 0))
        lines.append(' '.join(w['text'] for w in sorted_line))
    
    return '\n'.join(lines)


def _extract_text_column_aware(page) -> tuple[str, str, str, float | None]:
    """
    Returns (raw_text, left_text, right_text, split_x).
    Uses standard extraction first, falls back to word bounding boxes if stuck words detected.
    """
    # Primary: pdfplumber standard extraction (best for Vietnamese diacritics)
    raw_text = page.extract_text(x_tolerance=1.5, y_tolerance=3) or ""
    
    # Heuristic: Detect stuck words (English CVs lacking spaces)
    # If we see multiple unusually long alphabetic tokens, fallback to reconstruction
    long_words = [w for w in raw_text.split() if len(w) > 25 and not w.startswith('http')]
    if len(long_words) > 1:
        reconstructed = _reconstruct_text_from_words(page)
        if reconstructed:
            raw_text = reconstructed
    
    # Column detection: layout=True adds positional spaces (structural analysis)
    layout_text = page.extract_text(layout=True)
    
    if not layout_text:
        return raw_text, raw_text, "", None
        
    left_lines = []
    right_lines = []
    has_columns = False
    
    for line in layout_text.splitlines():
        if not line.strip():
            continue
            
        leading_spaces = len(line) - len(line.lstrip(' '))
        parts = re.split(r'\s{5,}', line.strip())
        
        if len(parts) == 1:
            # Check if this single line is physically on the right half
            if leading_spaces > 35:
                has_columns = True
                left_lines.append('')
                right_lines.append(line.strip())
            else:
                left_lines.append(line.strip())
                right_lines.append('')
        elif len(parts) >= 2:
            has_columns = True
            # Check if the entire group starts on the right
            if leading_spaces > 35:
                left_lines.append('')
                right_lines.append(' '.join(parts).strip())
            else:
                left_lines.append(parts[0].strip())
                right_lines.append(' '.join(parts[1:]).strip())
                
    split_indicator = 1.0 if has_columns else None
    return raw_text, '\n'.join(left_lines), '\n'.join(right_lines), split_indicator



def _parse_pdf(file_path: str) -> dict:
    pages_data = []
    all_chars = []
    column_split_xs = []
    column_texts = []
    
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            chars = page.chars
            # Mark bold chars
            for c in chars:
                c["bold"] = "bold" in c.get("fontname", "").lower()
            
            words = page.extract_words(extra_attrs=["fontname", "size"])
            raw_t, left_t, right_t, split_x = _extract_text_column_aware(page)
            
            column_split_xs.append(split_x)
            
            pages_data.append({
                "page_num": page.page_number,
                "text": raw_t,
                "words": words,
                "split_x": split_x,
                "page_width": page.width,
            })
            all_chars.extend(chars)
            
            # Store column texts per page
            if split_x is not None:
                column_texts.append({"left": left_t, "right": right_t, "split_x": split_x})
            else:
                column_texts.append({"left": left_t, "right": None, "split_x": None})
                
    raw_text = "\n".join([p["text"] for p in pages_data if p["text"]])
    raw_text = _normalize_text(raw_text)

    return {
        "type": "pdf",
        "pages": pages_data,
        "raw_chars": all_chars,
        "raw_text": raw_text,
        "column_texts": column_texts,
        "has_columns": any(x is not None for x in column_split_xs),
    }


def _parse_docx(file_path: str) -> dict:
    doc = docx.Document(file_path)
    paragraphs = []
    for p in doc.paragraphs:
        paragraphs.append({
            "text": p.text,
            "style": p.style.name if p.style else "Normal"
        })
        
    text = "\n".join([p["text"] for p in paragraphs])
    
    return {
        "type": "docx",
        "raw_text": text,
        "pages": [{"text": text}],
        "paragraphs": paragraphs,
        "raw_chars": [],
        "column_texts": [{"left": text, "right": None, "split_x": None}],
        "has_columns": False,
    }
