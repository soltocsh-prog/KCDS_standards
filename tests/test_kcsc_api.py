import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pytest_bdd import scenarios, given, when, then
from services.kcsc_api_client import KcscApiClient

scenarios('features/kcsc_api.feature')

@given('KCSC API 클라이언트가 설정되어 있다', target_fixture="api_client")
def api_client():
    return KcscApiClient()

@when('"114010" 코드에 대한 조회를 요청한다', target_fixture="api_response")
def request_api(api_client):
    return api_client.get_kcs_document("114010")

@then('응답에 "파형강판 암거"라는 문서 제목이 포함되어야 한다')
def verify_document_title(api_response):
    assert api_response is not None, "응답이 없습니다."
    assert api_response.get("name") == "파형강판 암거", f"문서 제목 불일치: {api_response.get('name')}"

@then('문서 본문(HTML)이 포함된 리스트 구조가 반환되어야 한다')
def verify_document_content(api_response):
    assert "list" in api_response, "list 속성이 없습니다."
    assert len(api_response["list"]) > 0, "본문 내용이 비어있습니다."
    assert "contents" in api_response["list"][0], "HTML 콘텐츠가 포함되어 있지 않습니다."


def test_api_key_rotation():
    """
    TDD Test: Verify that the API client rotates keys using a Round-Robin strategy.
    """
    client = KcscApiClient()
    # Mock some keys for testing
    client.api_keys = ["key1", "key2", "key3", "key4"]
    client.current_key_index = 0
    
    # Check that keys are returned in round-robin order
    assert client.get_next_api_key() == "key1"
    assert client.get_next_api_key() == "key2"
    assert client.get_next_api_key() == "key3"
    assert client.get_next_api_key() == "key4"
    assert client.get_next_api_key() == "key1"  # Back to first key

