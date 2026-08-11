Feature: HWPX 문서 자동 병합 및 스타일 일관화
  사용자가 선택한 KCSC API의 문서(HTML)들이 
  회사의 일관된 HWPX 템플릿 양식에 맞춰 병합되어야 한다.

  Scenario: HTML 본문을 HWPX 양식에 삽입
    Given 회사의 기본 HWPX 템플릿 "base_template.hwpx"가 준비되어 있다
    And KCSC API로부터 파싱된 HTML 본문 "<p>1. 일반사항</p>" 이 있다
    When 통합 문서 생성 엔진이 HTML을 템플릿에 주입한다
    Then 결과물 HWPX 파일의 Section0.xml 내부에 해당 텍스트가 한글 문단 태그("<hp:p>") 형태로 존재해야 한다
    And 지정된 회사 양식(StyleID)이 매핑되어야 한다
