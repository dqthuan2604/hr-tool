"""
cv_renderer.py
Renders a CV HTML string by merging candidate profile_json with template schema_json.
Uses Jinja2 templates located at backend/app/templates/.
"""
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.models.candidate import Candidate
from app.models.template import Template


def _get_jinja_env() -> Environment:
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    template_dir = os.path.abspath(template_dir)
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"])
    )


def render_cv(candidate: Candidate, template: Template, custom_json: dict = None) -> str:
    """
    Merge candidate profile_json with custom_json overrides and render CV HTML.
    custom_json keys take priority over profile_json.
    """
    # Get current profile from candidate versions
    current_version = None
    for v in candidate.versions:
        if v.is_current:
            current_version = v
            break
    if current_version is None and candidate.versions:
        current_version = candidate.versions[0]

    profile = dict(current_version.profile_json) if current_version else {}

    # Apply custom_json overrides (deep merge at top level)
    if custom_json:
        for key, value in custom_json.items():
            if key in profile and isinstance(profile[key], dict) and isinstance(value, dict):
                profile[key] = {**profile[key], **value}
            else:
                profile[key] = value

    schema = template.schema_json or {}
    sections = schema.get("sections", [])
    layout = schema.get("layout", {"columns": ["100%"]})
    colors = schema.get("colors", {
        "primary": "#1a1a2e",
        "accent": "#4361ee",
        "background": "#ffffff",
        "text": "#333333"
    })
    fonts = schema.get("fonts", {
        "heading": {"family": "Arial", "size": 16, "weight": "bold"},
        "body": {"family": "Arial", "size": 11, "weight": "normal"}
    })

    # Sort sections by order
    sections_sorted = sorted(sections, key=lambda s: s.get("order", 99))

    # Partition sections by column if two-column layout
    columns_count = len(layout.get("columns", ["100%"]))
    sections_col = {}
    for s in sections_sorted:
        col = s.get("column", 0)
        sections_col.setdefault(col, []).append(s)

    env = _get_jinja_env()
    tmpl = env.get_template("cv_full.html")

    html = tmpl.render(
        profile=profile,
        schema=schema,
        sections=sections_sorted,
        sections_col=sections_col,
        layout=layout,
        colors=colors,
        fonts=fonts,
        columns_count=columns_count,
    )
    return html
