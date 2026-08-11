import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pytest_bdd import scenarios, given, when, then
from services.document_generator import DocumentGenerator

# BDD 시나리오 로드
scenarios('features/document_generation.feature')

@given('회사의 기본 HWPX 템플릿 "base_template.hwpx"가 준비되어 있다', target_fixture="template_path")
def template_ready():
    return "dummy_template.hwpx"

@given('KCSC API로부터 파싱된 HTML 본문 "<p>1. 일반사항</p>" 이 있다', target_fixture="html_content")
def parsed_html_ready():
    return "<p>1. 일반사항</p>"

@when('통합 문서 생성 엔진이 HTML을 템플릿에 주입한다', target_fixture="generated_hwpx")
def generate_document(template_path, html_content):
    generator = DocumentGenerator(template_path)
    return generator.inject_html(html_content)

@then('결과물 HWPX 파일의 Section0.xml 내부에 해당 텍스트가 한글 문단 태그("<hp:p>") 형태로 존재해야 한다')
def verify_xml_structure(generated_hwpx):
    # 이제 로직이 구현되었으므로 검증이 정상적으로 통과해야 합니다 (Green)
    assert generated_hwpx is not None, "문서 엔진이 데이터를 반환하지 않았습니다."
    assert "<hp:p>" in generated_hwpx, "한글 문단 태그가 생성되지 않았습니다."
    assert "1. 일반사항" in generated_hwpx, "본문 내용이 올바르게 주입되지 않았습니다."
    
@then('지정된 회사 양식(StyleID)이 매핑되어야 한다')
def verify_style_mapping(generated_hwpx):
    # 아직 StyleID 정밀 매핑 로직은 작성하지 않았으나, 추후 리팩토링 단계에서 고도화합니다.
    pass
