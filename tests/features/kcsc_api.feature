Feature: KCSC OpenAPI 클라이언트 연동
  사용자가 특정 시방서를 요청하면
  KCSC OpenAPI를 호출하여 JSON 응답을 파싱하고 애플리케이션에서 사용 가능한 형태로 변환해야 한다.

  Scenario: 특정 KCS 코드의 세부 내용 조회
    Given KCSC API 클라이언트가 설정되어 있다
    When "114010" 코드에 대한 조회를 요청한다
    Then 응답에 "파형강판 암거"라는 문서 제목이 포함되어야 한다
    And 문서 본문(HTML)이 포함된 리스트 구조가 반환되어야 한다
