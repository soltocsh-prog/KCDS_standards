import re
import base64
import io

class Jinja2HmlGenerator:
    def __init__(self, template_path: str):
        self.template_path = template_path

    def _extract_image(self, html_img_str: str, current_bin_id: int, min_width=50, min_height=50):
        match = re.search(r"<img[^>]+src=['\"]([^'\"]+)['\"]", html_img_str, re.IGNORECASE)
        if not match:
            return None
            
        src = match.group(1)
        b64_data = ""
        img_format = "png"
        width_px, height_px = 200, 150
        
        if src.startswith('data:image/'):
            parts = src.split(';base64,')
            if len(parts) == 2:
                img_format = parts[0].replace('data:image/', '').split(';')[0].lower()
                if img_format == 'jpeg': img_format = 'jpg'
                b64_data = parts[1]
                
                try:
                    from PIL import Image
                    image_bytes = base64.b64decode(b64_data)
                    with Image.open(io.BytesIO(image_bytes)) as img:
                        width_px, height_px = img.size
                except Exception:
                    pass
        else:
            # 외부 URL 이미지는 단순화를 위해 생략 또는 fallback (테스트에서는 제외)
            pass
            
        if not b64_data:
            return None
            
        # 초소형 이미지 필터링
        if width_px < min_width and height_px < min_height:
            return None
            
        return {
            "bin_id": current_bin_id,
            "format": img_format,
            "data": b64_data,
            "width": int(width_px * 75),  # 픽셀 -> HWP 단위 (대략 75배)
            "height": int(height_px * 75),
            "original_width": width_px,
            "original_height": height_px
        }

    def build_context(self, items: list, min_width=50, min_height=50) -> dict:
        from bs4 import BeautifulSoup
        import xml.sax.saxutils as saxutils
        
        bin_items = []
        paragraphs = []
        current_bin_id = 1
        
        for item in items:
            level = item.get("level", 4)
            label = item.get("label", "")
            contents = item.get("contents", "")
            
            if item.get("type") == "page_break" or level == "page_break":
                paragraphs.append({
                    "is_page_break": True,
                    "is_table": False,
                    "is_image": False
                })
                continue
                
            if "<table" in contents.lower():
                soup = BeautifulSoup(contents, 'html.parser')
                table = soup.find('table')
                if not table:
                    continue
                
                rows = table.find_all('tr')
                grid_rows = []
                for r_idx, row in enumerate(rows):
                    cells = []
                    for c_idx, cell in enumerate(row.find_all(['td', 'th'])):
                        colspan = int(cell.get('colspan', 1))
                        rowspan = int(cell.get('rowspan', 1))
                        text = saxutils.escape(cell.get_text(strip=True))
                        
                        img_tag = cell.find('img')
                        has_image = False
                        image_ref = None
                        
                        if img_tag:
                            img_str = str(img_tag)
                            img_ctx = self._extract_image(img_str, current_bin_id, min_width, min_height)
                            if img_ctx:
                                bin_items.append(img_ctx)
                                has_image = True
                                image_ref = current_bin_id
                                current_bin_id += 1
                                
                        cells.append({
                            "col": c_idx,
                            "colspan": colspan,
                            "rowspan": rowspan,
                            "text": text,
                            "has_image": has_image,
                            "image_ref": image_ref
                        })
                    grid_rows.append({"cells": cells})
                
                paragraphs.append({
                    "is_page_break": False,
                    "is_table": True,
                    "is_image": False,
                    "label": label,
                    "grid": {"rows": grid_rows}
                })
            else:
                # 일반 텍스트나 그림 처리
                img_ctx = None
                is_image = False
                clean_contents = contents
                
                if "<img" in contents.lower():
                    img_ctx = self._extract_image(contents, current_bin_id, min_width, min_height)
                    if img_ctx:
                        bin_items.append(img_ctx)
                        is_image = True
                        image_ref = current_bin_id
                        current_bin_id += 1
                else:
                    clean_contents = re.sub(r'<[^>]+>', '', contents)
                    clean_contents = saxutils.unescape(clean_contents)
                
                paragraphs.append({
                    "is_page_break": False,
                    "is_table": False,
                    "is_image": is_image,
                    "level": level,
                    "label": label,
                    "contents": clean_contents,
                    "image_ref": image_ref if is_image else None
                })
                
        return {
            "bin_items": bin_items,
            "paragraphs": paragraphs
        }

    def generate(self, items: list, output_path: str):
        from jinja2 import Environment, FileSystemLoader
        import os
        
        context = self.build_context(items)
        
        template_dir = os.path.dirname(self.template_path)
        template_name = os.path.basename(self.template_path)
        
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=False)
        template = env.get_template(template_name)
        
        rendered_hml = template.render(context)
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_hml)
