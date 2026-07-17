import os
import json
import logging
import google.generativeai as genai

# Setup Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Use a balanced model
MODEL_NAME = "gemini-1.5-flash"

async def generate_template_html(schema: dict) -> str:
    """
    Sử dụng Gemini API để sinh ra mã HTML/CSS (Jinja2 template)
    dựa trên schema (chứa colors, fonts, sections) đã extract được từ PDF.
    """
    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY not found. Returning simple fallback template.")
        return _get_fallback_template(schema)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""
        Bạn là một chuyên gia Frontend và UI/UX Designer.
        Nhiệm vụ của bạn là tạo ra một bản thiết kế CV bằng HTML/CSS dựa trên cấu trúc đã cho.
        
        Sử dụng cấu trúc JSON sau đây (bao gồm màu sắc chủ đạo, font chữ và các mục có trong CV):
        ```json
        {json.dumps(schema, indent=2, ensure_ascii=False)}
        ```
        
        YÊU CẦU QUAN TRỌNG:
        1. Trả về DUY NHẤT một chuỗi HTML hoàn chỉnh, có chứa thẻ <style> bên trong <head>. Không kèm theo bất kỳ văn bản giải thích nào khác (không bọc trong ```html ... ```).
        2. Bố cục: Tạo layout 2 cột nếu schema có 'left' và 'right' sections, hoặc 1 cột nếu không. Sử dụng CSS Flexbox/Grid hiện đại.
        3. Sử dụng đúng màu sắc và font chữ trong schema.
        4. Đây là một file Jinja2 template. Bạn phải sử dụng các biến Jinja2 để hiển thị dữ liệu:
           - Tên: {{{{ profile.basic_info.full_name }}}}
           - Email: {{{{ profile.basic_info.email }}}}
           - SĐT: {{{{ profile.basic_info.phone }}}}
           - Kinh nghiệm: Dùng vòng lặp `{{% for exp in profile.work_experiences %}} ... {{{{ exp.company }}}}, {{{{ exp.role }}}} ... {{% endfor %}}`
           - Học vấn: Dùng vòng lặp `{{% for ed in profile.educations %}} ... {{{{ ed.school }}}} ... {{% endfor %}}`
           - Kỹ năng: Dùng vòng lặp `{{% for sk in profile.skills %}} ... {{{{ sk.category }}}} ... {{% endfor %}}`
        5. Thiết kế phải mang phong cách hiện đại, thanh lịch (elegant), chuyên nghiệp.
        """

        response = model.generate_content(prompt)
        html_code = response.text.strip()
        
        # Remove markdown codeblocks if AI still includes them
        if html_code.startswith("```html"):
            html_code = html_code[7:]
        elif html_code.startswith("```"):
            html_code = html_code[3:]
        if html_code.endswith("```"):
            html_code = html_code[:-3]
            
        return html_code.strip()

    except Exception as e:
        logging.error(f"Error generating template with Gemini: {e}")
        return _get_fallback_template(schema)


def _get_fallback_template(schema: dict) -> str:
    """Trả về template cơ bản nếu không gọi được AI."""
    primary_color = schema.get("colors", {}).get("primary", "#333")
    
    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>CV</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .cv-container {{ max-width: 800px; margin: 0 auto; background: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 40px; }}
            .header {{ text-align: center; border-bottom: 2px solid {primary_color}; padding-bottom: 20px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; color: {primary_color}; font-size: 2.5em; }}
            .contact-info {{ color: #666; margin-top: 10px; }}
            .section-title {{ color: {primary_color}; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 25px; }}
            .item-title {{ font-weight: bold; font-size: 1.1em; }}
            .item-subtitle {{ font-style: italic; color: #555; }}
            .item-date {{ float: right; color: #888; font-size: 0.9em; }}
            .skills-list {{ list-style-type: none; padding: 0; display: flex; flex-wrap: wrap; gap: 10px; }}
            .skill-tag {{ background: {primary_color}; color: #fff; padding: 5px 10px; border-radius: 4px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="cv-container">
            <div class="header">
                <h1>{{{{ profile.basic_info.full_name }}}}</h1>
                <div class="contact-info">
                    {{{{ profile.basic_info.email }}}} | {{{{ profile.basic_info.phone }}}} | {{{{ profile.basic_info.address }}}}
                </div>
                <p>{{{{ profile.basic_info.summary }}}}</p>
            </div>

            <h2 class="section-title">Kinh nghiệm làm việc</h2>
            {{% for exp in profile.work_experiences %}}
            <div class="item">
                <span class="item-date">{{{{ exp.start_date }}}} - {{{{ exp.end_date }}}}</span>
                <div class="item-title">{{{{ exp.company }}}}</div>
                <div class="item-subtitle">{{{{ exp.role }}}}</div>
                <p>{{{{ exp.description }}}}</p>
            </div>
            {{% endfor %}}

            <h2 class="section-title">Học vấn</h2>
            {{% for ed in profile.educations %}}
            <div class="item">
                <span class="item-date">{{{{ ed.start_date }}}} - {{{{ ed.end_date }}}}</span>
                <div class="item-title">{{{{ ed.school }}}}</div>
                <div class="item-subtitle">{{{{ ed.major }}}} - {{{{ ed.degree }}}} (GPA: {{{{ ed.gpa }}}})</div>
            </div>
            {{% endfor %}}

            <h2 class="section-title">Kỹ năng</h2>
            <ul class="skills-list">
            {{% for sk in profile.skills %}}
                {{% for item in sk.items %}}
                <li class="skill-tag">{{{{ item }}}}</li>
                {{% endfor %}}
            {{% endfor %}}
            </ul>
        </div>
    </body>
    </html>
    """
