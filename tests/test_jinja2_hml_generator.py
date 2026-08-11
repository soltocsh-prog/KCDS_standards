import pytest
import os
from services.jinja2_generator.jinja2_hml_generator import Jinja2HmlGenerator

def test_jinja2_hml_generator_init():
    # Given
    template_path = "dummy_path.hml.j2"
    
    # When
    generator = Jinja2HmlGenerator(template_path)
    
    # Then
    assert generator.template_path == template_path

def test_extract_images():
    # Given
    html_content = '<p>Test</p><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=">'
    generator = Jinja2HmlGenerator("dummy.j2")
    
    # When
    img_context = generator._extract_image(html_content, current_bin_id=1, min_width=0, min_height=0)
    
    # Then
    assert img_context is not None
    assert img_context["bin_id"] == 1
    assert img_context["format"] == "png"
    assert "iVBORw0KGgo" in img_context["data"]
    assert img_context["width"] > 0
    assert img_context["height"] > 0

def test_build_context():
    # Given
    flat_items = [
        {"level": 0, "label": "", "contents": "KCS 1234 Test"},
        {"level": 4, "label": "표 1", "contents": '<table><tr><td><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="></td></tr></table>'}
    ]
    generator = Jinja2HmlGenerator("dummy.j2")
    
    # When
    context = generator.build_context(flat_items, min_width=0, min_height=0)
    
    # Then
    assert "bin_items" in context
    assert len(context["bin_items"]) == 1
    assert "paragraphs" in context
    assert len(context["paragraphs"]) == 2
    
    # Table paragraph check
    table_p = context["paragraphs"][1]
    assert table_p["is_table"] is True
    assert "grid" in table_p
    assert len(table_p["grid"]["rows"]) == 1
    
    cell = table_p["grid"]["rows"][0]["cells"][0]
    assert cell["has_image"] is True
    assert cell["image_ref"] == context["bin_items"][0]["bin_id"]
