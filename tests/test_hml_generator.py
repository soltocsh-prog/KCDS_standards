import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.hml_generator import HmlGenerator

def test_load_template():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    assert os.path.exists(template_path), "Template file should exist"
    
    # Act
    generator = HmlGenerator(template_path)
    
    # Assert
    assert generator.tree is not None, "XML Tree should be loaded"
    assert generator.root is not None, "XML Root should be loaded"
    assert generator.root.tag == 'HWPML', "Root tag should be HWPML"

def test_replace_placeholders():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # Act
    generator.replace_placeholders("41 10 00", "건축공사 일반사항")
    
    # Assert
    # Convert tree back to string to check for replaced text
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    assert "[코드]" not in xml_str, "[코드] placeholder should be removed"
    assert "[공종]" not in xml_str, "[공종] placeholder should be removed"
    assert "41 10 00" in xml_str, "Code value should be injected"
    assert "건축공사 일반사항" in xml_str, "Name value should be injected"

def test_map_kcsc_to_style():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # Act & Assert
    assert generator.map_kcsc_to_style(1, "1.") == "KCSC_중분류_[1.]"
    assert generator.map_kcsc_to_style(2, "1.1") == "KCSC_소분류_[1.1]"
    assert generator.map_kcsc_to_style(3, "1.1.1") == "KCSC_초소분류_[1.1.1]"
    assert generator.map_kcsc_to_style(4, "본문") == "KCSC_본문1"
    assert generator.map_kcsc_to_style(4, "①") == "KCSC_리스트2"
    assert generator.map_kcsc_to_style(5, "가.") == "KCSC_리스트3"
    assert generator.map_kcsc_to_style(6, "(가)") == "KCSC_리스트4"
    assert generator.map_kcsc_to_style(7, "본문") == "KCSC_본문4"

def test_insert_content():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    mock_data = [
        {"level": 1, "label": "1.", "contents": "1. 일반사항"},
        {"level": 2, "label": "1.1", "contents": "1.1 적용범위"},
        {"level": 4, "label": "본문", "contents": "이 기준은 대한민국 내에서 수행되는 건축공사에 적용한다."}
    ]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    assert "[본문 시작]" not in xml_str, "[본문 시작] placeholder should be removed"
    assert "1. 일반사항" in xml_str, "Content 1 should be injected"
    assert "1.1 적용범위" in xml_str, "Content 2 should be injected"
    assert "이 기준은 대한민국 내에서" in xml_str, "Content 3 should be injected"

def test_insert_content_with_html_table_should_generate_hml_table_node():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    mock_data = [{
        "level": 4, 
        "label": "표 1.1", 
        "contents": "<table><tr><td>Header1</td><td>Header2</td></tr><tr><td>Data1</td><td>Data2</td></tr></table>"
    }]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    assert "<TABLE" in xml_str, "HML <TABLE> node should be generated"
    assert "<ROW" in xml_str, "HML <ROW> node should be generated"
    assert "<CELL" in xml_str, "HML <CELL> node should be generated"
    assert "Header1" in xml_str, "Table content should be preserved"
    assert "Data2" in xml_str, "Table content should be preserved"

def test_insert_content_with_empty_table_should_handle_gracefully():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    mock_data = [{"level": 4, "label": "빈 표", "contents": "<table></table>"}]
    
    # Act
    try:
        generator.insert_content(mock_data)
    except Exception as e:
        pytest.fail(f"insert_content raised Exception unexpectedly: {e}")
        
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    assert "빈 표" in xml_str, "Label should still be inserted even if table is empty"

def test_insert_content_with_html_image_should_generate_hml_picture_node():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64_large = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    mock_data = [{
        "level": 4, 
        "label": "그림 1.1", 
        "contents": f"<img src='data:image/png;base64,{b64_large}' alt='테스트 이미지'>"
    }]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    assert "<PICTURE" in xml_str, "HML <PICTURE> node should be generated for large image"
    assert "<BINITEM" in xml_str, "HML <BINITEM> should be registered in BINITEMLIST"

def test_insert_content_with_invalid_image_src_should_skip_or_handle_gracefully():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    mock_data = [{"level": 4, "label": "그림 1.2", "contents": "일반 텍스트입니다<img src=''>"}]
    
    # Act
    try:
        generator.insert_content(mock_data)
    except Exception as e:
        pytest.fail(f"insert_content raised Exception for invalid img src: {e}")
        
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    assert "일반 텍스트입니다" in xml_str, "Text should be preserved when image fails or is skipped"

def test_create_hml_table_with_jinja2_template():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    html = "<table><tr><td colspan='2'>Header</td></tr><tr><td>A</td><td>B</td></tr></table>"
    mock_data = [{"level": 4, "label": "표", "contents": html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    # The table should contain the exact structure from the Jinja2 snippet.
    assert "<TABLE" in xml_str
    # Check if colspan is correctly mapped
    assert "ColSpan=\"2\"" in xml_str

def test_create_hml_table_with_malformed_html_should_parse_all_rows_and_cells():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    malformed_html = (
        "<p><table>"
        "  <tr><td>Row 0, Cell 0</td></tr>"
        "  <tr>"
        "    <td>"
        "      옹이<p><span>(긴지름이</p>10mm미만</p>의 것제외)</span></p>"
        "    </td>"
        "  </tr>"
        "  <tr><td>Row 2, Cell 0</td></tr>"
        "</table></p>"
    )
    mock_data = [{"level": 4, "label": "표", "contents": malformed_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    # The table should contain RowCount="3" because there are 3 rows,
    # despite the malformed HTML in row 1.
    assert 'RowCount="3"' in xml_str, "Should parse all 3 rows in malformed HTML"
    assert 'Row 2, Cell 0' in xml_str, "Should not truncate rows after malformed tags"

def test_create_hml_picture_with_base64_gif_should_parse_dimensions():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # 60x60 픽셀 GIF의 Base64 동적 생성
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='GIF')
    b64_gif = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html = f'<img src="data:image/gif;base64,{b64_gif}">'
    mock_data = [{"level": 4, "label": "그림 1.1", "contents": img_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    # 1. BINITEM 태그가 올바른 Format으로 생성되었는지 확인
    assert 'Format="gif"' in xml_str, "BINITEM should have Format='gif'"
    # 2. 실제 Base64 데이터가 들어갔는지 확인
    assert b64_gif in xml_str, "Base64 data should be injected into BINITEMDATA"
    # 3. PICTURE 태그가 생성되었는지 확인
    assert '<PICTURE' in xml_str, "PICTURE element should be generated"
    # 4. 해상도 검증: 60x60 픽셀 -> 60 * 75 = 4500 HWP Unit
    assert 'Width="4500"' in xml_str, "Width should be correctly scaled to 4500 HWP Units"
    assert 'Height="4500"' in xml_str, "Height should be correctly scaled to 4500 HWP Units"

def test_insert_content_with_tiny_image_should_preserve_text():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # 1x1 픽셀 (50x50 미만)
    b64_tiny = "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
    img_html = f'<img src="data:image/gif;base64,{b64_tiny}">'
    content_html = f"이 글자는 살아남아야 합니다. {img_html}"
    mock_data = [{"level": 4, "label": "테스트", "contents": content_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    assert "이 글자는 살아남아야 합니다." in xml_str, "Text should not be deleted for tiny images"
    # Wait, the tiny image is currently filtered? Yes, our test checks if the text survives.

def test_create_hml_table_with_image_should_render_picture_inside_cell():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # 60x60 픽셀 이미지 동적 생성 (50x50 초과)
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64_large = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html = f'<img src="data:image/png;base64,{b64_large}">'
    table_html = f"<table><tr><td>셀텍스트{img_html}</td></tr></table>"
    mock_data = [{"level": 4, "label": "표", "contents": table_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    assert "셀텍스트" in xml_str, "Table cell text should be rendered"
    assert "<PICTURE" in xml_str, "Large image inside table cell should generate a PICTURE element"


def test_body_picture_should_use_absolute_width_rel_to_when_not_in_table():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # 60x60 픽셀 이미지
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64_large = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html = f'<img src="data:image/png;base64,{b64_large}">'
    mock_data = [{"level": 4, "label": "그림 테스트", "contents": img_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    assert 'WidthRelTo="Absolute"' in xml_str, "WidthRelTo should be Absolute for body images"
    assert 'HeightRelTo="Absolute"' in xml_str, "HeightRelTo should be Absolute for body images"


def test_body_picture_should_scale_height_when_exceeding_max_height():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # 60x1000 픽셀 이미지 (60*75 = 4500, 1000*75 = 75000 -> 세로가 55000 초과)
    # 55000으로 조정되면 가로는 4500 * (55000 / 75000) = 3300 이 되어야 함.
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 1000), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64_tall = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html = f'<img src="data:image/png;base64,{b64_tall}">'
    mock_data = [{"level": 4, "label": "세로가 긴 그림 테스트", "contents": img_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    # Width="3300" Height="55000" 인지 검증
    assert 'Width="3300"' in xml_str, "Width should be scaled proportionally to 3300"
    assert 'Height="55000"' in xml_str, "Height should be capped at 55000"


def test_body_picture_should_infer_height_when_only_width_specified():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # 60x60 이미지 생성
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # width만 지정 (width="120")
    img_html = f'<img src="data:image/png;base64,{b64}" width="120">'
    mock_data = [{"level": 4, "label": "가로만 지정", "contents": img_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    # 120 * 75 = 9000
    assert 'Width="9000"' in xml_str, "Width should be parsed as 9000 (120px)"
    assert 'Height="9000"' in xml_str, "Height should be inferred as 9000 (120px) keeping aspect ratio"


def test_body_picture_should_infer_width_when_only_height_specified():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # 60x60 이미지 생성
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # height만 지정 (height="30")
    img_html = f'<img src="data:image/png;base64,{b64}" height="30">'
    mock_data = [{"level": 4, "label": "세로만 지정", "contents": img_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    # 30 * 75 = 2250
    assert 'Height="2250"' in xml_str, "Height should be parsed as 2250 (30px)"
    assert 'Width="2250"' in xml_str, "Width should be inferred as 2250 (30px) keeping aspect ratio"


def test_body_picture_should_parse_dimensions_from_css_style_attribute():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # 60x60 이미지 생성
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # style 속성으로 크기 지정
    img_html = f'<img src="data:image/png;base64,{b64}" style="width: 120px; height: 180px;">'
    mock_data = [{"level": 4, "label": "CSS 스타일 지정", "contents": img_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    # 120 * 75 = 9000
    # 180 * 75 = 13500
    assert 'Width="9000"' in xml_str, "Width should be parsed from style as 9000 (120px)"
    assert 'Height="13500"' in xml_str, "Height should be parsed from style as 13500 (180px)"


def test_image_deduplication_should_reuse_bin_id():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html = f'<img src="data:image/png;base64,{b64}">'
    mock_data = [
        {"level": 4, "label": "첫번째그림", "contents": img_html},
        {"level": 4, "label": "두번째그림(동일내용)", "contents": img_html}
    ]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    import xml.etree.ElementTree as ET
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    # BINITEM count should be 1
    assert xml_str.count("<BINITEM") == 1, "Should only create one BINITEM for duplicate images"
    # BINDATA count should be 1
    assert xml_str.count("<BINDATA ") == 1, "Should only store one base64 data stream in BINDATASTORAGE"


def test_table_cell_with_img_and_text_generates_single_p_tag():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # Generate 60x60 base64 image
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html = f'<img src="data:image/png;base64,{b64}">'
    table_html = f"<table><tr><td>이것은 텍스트입니다.{img_html}</td></tr></table>"
    mock_data = [{"level": 4, "label": "테이블 혼합", "contents": table_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    cell = generator.root.find(".//CELL")
    assert cell is not None, "CELL element should exist"
    
    paralist = cell.find("PARALIST")
    assert paralist is not None, "PARALIST element should exist"
    
    p_elements = paralist.findall("P")
    assert len(p_elements) == 1, "There should be exactly one P element inside PARALIST for text+image cell"
    
    p = p_elements[0]
    text_elements = p.findall("TEXT")
    assert len(text_elements) == 1, "There should be exactly one TEXT element inside P"
    
    text_el = text_elements[0]
    char_elements = text_el.findall("CHAR")
    assert len(char_elements) >= 2, "Should contain at least 2 CHAR elements"
    
    pic_elements = text_el.findall("PICTURE")
    assert len(pic_elements) == 1, "Should contain exactly one PICTURE element"


def test_table_cell_height_includes_both_text_and_image_height():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # Generate 60x60 base64 image (60*75 = 4500 HWP Units height)
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html = f'<img src="data:image/png;base64,{b64}">'
    table_html = f"<table><tr><td>라인1\n라인2{img_html}</td></tr></table>"
    mock_data = [{"level": 4, "label": "높이 검증", "contents": table_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    cell = generator.root.find(".//CELL")
    assert cell is not None
    
    cell_height = int(cell.get("Height", "0"))
    # Expected height calculation:
    # Base: 282 + 500 = 782
    # Text (2 lines): 282 * 2 = 564
    # Image: 4500 + 500 = 5000
    # Total = 782 + 564 + 5000 = 6346
    assert cell_height == 6346, f"Expected cell height to be 6346, got {cell_height}"


def test_table_cell_with_multiple_images():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    # Generate two 60x60 base64 images
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html1 = f'<img src="data:image/png;base64,{b64}">'
    img_html2 = f'<img src="data:image/png;base64,{b64}">'
    table_html = f"<table><tr><td>텍스트 {img_html1} 중간텍스트 {img_html2} 끝텍스트</td></tr></table>"
    mock_data = [{"level": 4, "label": "다중 이미지", "contents": table_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    cell = generator.root.find(".//CELL")
    assert cell is not None
    
    paralist = cell.find("PARALIST")
    assert paralist is not None
    
    p_elements = paralist.findall("P")
    assert len(p_elements) == 1, "There should be exactly one P element inside PARALIST"
    
    p = p_elements[0]
    pic_elements = p.findall(".//PICTURE")
    # Verify that multiple images are generated inside the cell
    assert len(pic_elements) == 2, "Should contain exactly two PICTURE elements inside the cell"


def test_table_cell_height_with_multiple_images():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    from PIL import Image
    import io, base64
    img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    img_html1 = f'<img src="data:image/png;base64,{b64}">'
    img_html2 = f'<img src="data:image/png;base64,{b64}">'
    # Text has 3 lines (2 newlines)
    table_html = f"<table><tr><td>라인1\n라인2\n라인3{img_html1}{img_html2}</td></tr></table>"
    mock_data = [{"level": 4, "label": "다중 이미지 높이", "contents": table_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    cell = generator.root.find(".//CELL")
    assert cell is not None
    
    cell_height = int(cell.get("Height", "0"))
    # Base: 782
    # Text (3 lines): 282 * 3 = 846
    # Image 1: 4500 + 500 = 5000
    # Image 2: 4500 + 500 = 5000
    # Total: 782 + 846 + 5000 + 5000 = 11628
    assert cell_height == 11628


def test_table_cell_preserves_newlines_from_br_and_p_tags():
    # Arrange
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    table_html = (
        "<table><tr><td>"
        "<p>라인1</p>"
        "라인2<br/>라인3"
        "<div>라인4</div>"
        "</td></tr></table>"
    )
    mock_data = [{"level": 4, "label": "개행 보존", "contents": table_html}]
    
    # Act
    generator.insert_content(mock_data)
    
    # Assert
    cell = generator.root.find(".//CELL")
    assert cell is not None
    
    paralist = cell.find("PARALIST")
    p_elements = paralist.findall("P")
    assert len(p_elements) == 1
    
    # Reconstruct text with newlines from all TEXT/CHAR elements
    texts = []
    for text_el in p_elements[0].findall("TEXT"):
        for child in text_el:
            if child.tag == "CHAR":
                if child.get("Type") == "LineBreak":
                    texts.append("\n")
                elif child.text:
                    texts.append(child.text)
    cell_text = "".join(texts)
    
    # Check that newlines exist in the cell text
    # HTML structure:
    # <p>라인1</p>라인2<br/>라인3<div>라인4</div>
    # Should be parsed to:
    # 라인1\n라인2\n라인3\n라인4
    assert "라인1\n라인2\n라인3\n라인4" in cell_text, f"Text should preserve newlines, got: {repr(cell_text)}"


def test_table_note_formatting_logic():
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    note_text = " 주] 1) 풍하중을 산정 할 때의 면적은 외곽면적에 충실률 를 곱한 것으로 한다.      2) 충실률 의 정의는 표 5.7-9와 같다.      3) 표에 나타낸 충실률 의 중간값에 대해서는 직선보간하여 사용할 수 있다.  기호] ：펜스의 정상부 높이(m) "
    formatted = generator._format_table_note_text(note_text)
    
    expected = (
        "주] 1) 풍하중을 산정 할 때의 면적은 외곽면적에 충실률 를 곱한 것으로 한다.\n"
        "2) 충실률 의 정의는 표 5.7-9와 같다.\n"
        "3) 표에 나타낸 충실률 의 중간값에 대해서는 직선보간하여 사용할 수 있다.\n"
        "기호] ：펜스의 정상부 높이(m)"
    )
    assert formatted == expected


def test_table_note_styling_and_paragraph_splitting():
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    table_html = (
        "<table>"
        "<tr><td>일반 데이터 셀</td></tr>"
        "<tr><td>주] 1) 첫번째 항목. 2) 두번째 항목. 기호] x: 변수</td></tr>"
        "</table>"
    )
    mock_data = [{"level": 4, "label": "주기 스타일 및 분할", "contents": table_html}]
    
    generator.insert_content(mock_data)
    
    cells = generator.root.findall(".//CELL")
    assert len(cells) == 2
    
    # First cell (regular data cell)
    cell_regular = cells[0]
    p_regular = cell_regular.find("PARALIST").findall("P")
    assert len(p_regular) == 1
    assert p_regular[0].get("Style") == "11"  # KCSC_표_본문 (or default style id)
    
    # Second cell (note cell)
    cell_note = cells[1]
    p_note = cell_note.find("PARALIST").findall("P")
    # It has:
    # 1. "주] 1) 첫번째 항목."
    # 2. "2) 두번째 항목."
    # 3. "기호] x: 변수"
    # So 3 paragraphs!
    assert len(p_note) == 3
    for p in p_note:
        assert p.get("Style") == "12"  # KCSC_주기 style ID












