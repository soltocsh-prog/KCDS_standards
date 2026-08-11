from bs4 import BeautifulSoup

class DocumentGenerator:
    def __init__(self, template_path: str):
        self.template_path = template_path

    def inject_html(self, html_content: str) -> str:
        """
        TDD [Green] 단계:
        HTML을 파싱하여 한글 문서(HWPX)의 XML(Section0.xml) 노드로 변환하는 최소 로직.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # HWPX의 Section XML 구조 시작
        section_xml = "<hp:sec xmlns:hp='http://www.hancom.co.kr/hwpml/2011/paragraph'>"
        
        for element in soup.find_all(['p', 'h1', 'h2', 'h3']):
            text = element.get_text()
            # HWPX 문단 태그 구조 적용: <hp:p> -> <hp:run> -> <hp:t> 텍스트 </hp:t>
            section_xml += f"<hp:p><hp:run><hp:t>{text}</hp:t></hp:run></hp:p>"
            
        section_xml += "</hp:sec>"
        
        # 실제 파일 압축 조작 전, 테스트 통과를 위해 생성된 XML 구조 반환
        return section_xml
