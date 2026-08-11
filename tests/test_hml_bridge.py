import os
import sys
import pytest
import xml.etree.ElementTree as ET

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.hml_bridge import HmlOrchestrationBridge
from db.database import get_db_connection

def test_hml_bridge_generation():
    """
    Test that HmlOrchestrationBridge takes merged document data,
    drives HmlGenerator to produce a valid HML file with page breaks,
    and replaces template placeholders.
    """
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template.hml')
    output_path = os.path.join(os.path.dirname(__file__), '..', 'test_merged_output.hwp')
    
    # Clean up any leftover file
    if os.path.exists(output_path):
        os.remove(output_path)
        
    # Mock data from DocumentOrchestrator
    mock_merged_document = [
        {
            "code": "40 10 00",
            "name": "가설공사 일반",
            "version": "2025",
            "content_sections": [
                {
                    "title": "1. 일반사항",
                    "content": "<p>1. 일반사항 본문</p>",
                    "level": 1,
                    "label": "1."
                }
            ]
        },
        {
            "type": "page_break"
        },
        {
            "code": "40 20 00",
            "name": "비계 및 안전시설물",
            "version": "2025",
            "content_sections": [
                {
                    "title": "1. 일반사항 (비계)",
                    "content": "<p>1. 비계 본문</p>",
                    "level": 1,
                    "label": "1."
                }
            ]
        }
    ]

    # Act
    bridge = HmlOrchestrationBridge(template_path)
    bridge.generate_hml(mock_merged_document, output_path)
    
    # Assert: File is generated
    assert os.path.exists(output_path), "Merged output file should be generated"
    
    # Parse generated XML to verify contents
    tree = ET.parse(output_path)
    root = tree.getroot()
    xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
    
    # 1. Placeholders are replaced (guided by first document)
    assert "[코드]" not in xml_str
    assert "[공종]" not in xml_str
    assert "40 10 00" in xml_str
    assert "가설공사 일반" in xml_str
    
    # 2. Document titles are injected as level=0 headers
    assert "KCS 40 10 00 가설공사 일반" in xml_str
    assert "KCS 40 20 00 비계 및 안전시설물" in xml_str
    
    # 3. Document contents are injected
    assert "1. 일반사항 본문" in xml_str
    assert "1. 비계 본문" in xml_str
    
    # 4. Merged total sections should be 4 (Cover=0, TOC=1, Doc1=2, Doc2=3)
    sections = root.findall('.//SECTION')
    assert len(sections) == 4, f"Merged HML should have 4 sections, got {len(sections)}"
    
    # Section 2 header should contain metadata of the first document
    sec2_header = "".join(sections[2].find('.//HEADER').itertext()).strip()
    assert "40 10 00" in sec2_header
    assert "가설공사 일반" in sec2_header
    
    # Section 3 header should contain metadata of the second document
    sec3_header = "".join(sections[3].find('.//HEADER').itertext()).strip()
    assert "40 20 00" in sec3_header
    assert "비계 및 안전시설물" in sec3_header
    
    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)

def test_hml_bridge_use_jinja_flag():
    # Given
    bridge = HmlOrchestrationBridge("dummy.hml", use_jinja=True)
    
    # Then
    assert getattr(bridge, "use_jinja", False) is True

def test_hml_bridge_image_id_remapping_multiple_images(tmp_path):
    # Tests that when merging a document with multiple images, 
    # progressive rewriting of BinItems is prevented.
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'base_template2.hml')
    output_path = str(tmp_path / "output.hml")
    
    # Let's mock a merged document with two documents:
    # First document has 1 image (Count=1, ID=1)
    # Second document has 2 images (Count=2, IDs 1 and 2)
    mock_data = [
        {
            "code": "11 11 11",
            "name": "Doc1",
            "content_sections": [
                {
                    "level": 4,
                    "label": "그림1",
                    "content": '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==">' # 1x1 image
                }
            ]
        },
        {
            "type": "page_break"
        },
        {
            "code": "22 22 22",
            "name": "Doc2",
            "content_sections": [
                {
                    "level": 4,
                    "label": "그림2",
                    "content": (
                        '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==">' # same image
                        '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=">' # different image
                    )
                }
            ]
        }
    ]
    
    bridge = HmlOrchestrationBridge(template_path)
    bridge.generate_hml(mock_data, output_path)
    
    # Parse generated HML
    tree = ET.parse(output_path)
    root = tree.getroot()
    
    # Check that BINDATALIST count and BINDATA elements match
    bindatalist = root.find(".//BINDATALIST")
    binitems = bindatalist.findall("BINITEM")
    # First doc has 1 unique image (ID 1)
    # Second doc has 2 unique images, but one is a duplicate in the same generator context (which is cached and reused as ID 1, 
    # but the second one is new and gets ID 2)
    # So Doc 2 has BINDATALIST with Count=2 (IDs 1, 2).
    # When merged:
    # Doc 1 adds 1 image -> count is 1. (primary_count = 1)
    # Doc 2 adds its BINITEMS:
    #   - BinData="1" (first image) -> new_id = 2.
    #   - BinData="2" (second image) -> new_id = 3.
    # In the final merged document, we expect a total of 3 BINITEM elements.
    assert len(binitems) == 3
    
    # Now check the IMAGE elements inside Section 3 (corresponds to Doc 2)
    sections = root.findall(".//SECTION")
    doc2_section = sections[3]
    
    images = doc2_section.findall(".//IMAGE")
    assert len(images) == 2
    
    # Under the old buggy code:
    # 1. First image (ID 1) -> new_id = 2. First image becomes 2.
    # 2. Second image (ID 2) -> new_id = 3. Second image (ID 2) and First image (which is now 2) BOTH become 3.
    # So BOTH images would have BinItem="3".
    #
    # Under the fixed code, the first image must remain BinItem="2", and the second image must be BinItem="3".
    bin_items_in_doc2 = [img.get("BinItem") for img in images]
    assert bin_items_in_doc2 == ["2", "3"], f"Expected ['2', '3'], got {bin_items_in_doc2}"

