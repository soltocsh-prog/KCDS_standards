import pytest
import os
import xml.etree.ElementTree as ET
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.hml_generator import HmlGenerator
from PIL import Image
import io, base64

def get_large_b64():
    img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def test_picture_requires_char_anchor_in_cell():
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    b64_large = get_large_b64()
    img_html = f'<img src="data:image/png;base64,{b64_large}">'
    table_html = f"<table><tr><td>셀텍스트{img_html}</td></tr></table>"
    
    # Act
    generator.insert_content([{"level": 4, "label": "표", "contents": table_html}])
    
    # Assert
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    assert "<PICTURE" in xml_str
    
    # Verify the structure inside PARALIST
    # It should have a separate <P> for the picture, and an empty <CHAR/> anchor.
    root = generator.root
    paralists = root.findall('.//PARALIST')
    
    found_picture_in_cell = False
    for paralist in paralists:
        pics = paralist.findall('.//PICTURE')
        if pics:
            found_picture_in_cell = True
            # The PICTURE should be inside a <TEXT> tag which is inside a single <P> tag
            p_tags = paralist.findall('.//P')
            assert len(p_tags) == 1, "PARALIST should have a single P tag for text and picture combined"
            
            pic_p = p_tags[0]
            text_tag = pic_p.find('.//TEXT')
            assert text_tag is not None, "PICTURE must be wrapped in a TEXT tag"
            
            # Find the PICTURE element inside TEXT
            pic = text_tag.find('.//PICTURE')
            assert pic is not None, "PICTURE should be present inside TEXT tag"
            
            # Verify a CHAR anchor exists next to the PICTURE (HML requirement)
            char_tags = text_tag.findall('.//CHAR')
            assert len(char_tags) >= 2, "A <CHAR> anchor must exist next to the PICTURE"
            # The last CHAR is the anchor created for PICTURE
            anchor_char = char_tags[-1]
            assert anchor_char.text is None or anchor_char.text in ["", " "], "The anchor <CHAR> should be empty"
            
    assert found_picture_in_cell, "PICTURE must be inside the table's PARALIST"

def test_picture_template_structures_for_tables():
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    b64_large = get_large_b64()
    img_html = f'<img src="data:image/png;base64,{b64_large}">'
    table_html = f"<table><tr><td>셀텍스트{img_html}</td></tr></table>"
    
    # Act
    generator.insert_content([{"level": 4, "label": "표", "contents": table_html}])
    
    # Assert
    xml_str = ET.tostring(generator.root, encoding='utf-8').decode('utf-8')
    
    # These elements must be present for Hancom HWP to render the image inside tables
    assert "SHAPECOMPONENT" in xml_str
    assert "ROTATIONINFO" in xml_str
    assert "RENDERINGINFO" in xml_str
    assert "SCAMATRIX" in xml_str
    assert "IMAGECLIP" in xml_str
    assert 'TreatAsChar="true"' in xml_str
    assert 'FlowWithText="false"' in xml_str

def test_image_binary_data_stored_in_bindatastorage():
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    generator = HmlGenerator(template_path)
    
    b64_large = get_large_b64()
    img_html = f'<img src="data:image/png;base64,{b64_large}">'
    
    # Act
    generator.insert_content([{"level": 4, "label": "본문그림", "contents": img_html}])
    
    # Assert
    root = generator.root
    mapping_table = root.find('.//MAPPINGTABLE')
    assert mapping_table is not None
    
    bindatalist = mapping_table.find('BINDATALIST')
    assert bindatalist is not None, "BINDATALIST must exist under MAPPINGTABLE"
    assert list(mapping_table)[0] == bindatalist, "BINDATALIST must be the first child of MAPPINGTABLE"
    
    binitem = bindatalist.find('BINITEM')
    assert binitem is not None
    assert binitem.get('BinData') == '1'
    assert binitem.get('Format') == 'png'
    assert binitem.get('Type') == 'Embedding'
    
    tail = root.find('.//TAIL')
    assert tail is not None
    
    bindatastorage = tail.find('BINDATASTORAGE')
    assert bindatastorage is not None, "BINDATASTORAGE must exist under TAIL"
    assert list(tail)[0] == bindatastorage, "BINDATASTORAGE must be the first child of TAIL"
    
    bindata = bindatastorage.find('BINDATA')
    assert bindata is not None
    assert bindata.get('Id') == '1'
    assert bindata.get('Encoding') == 'Base64'
    assert bindata.text == b64_large


