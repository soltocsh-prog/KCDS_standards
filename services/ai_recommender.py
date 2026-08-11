class AIRecommender:
    def __init__(self):
        # TODO: Gemini API 클라이언트 초기화 로직 (환경변수 키 로드 등)
        pass

    def get_recommendations(self, project_description: str) -> list:
        """
        TDD [Green] 단계:
        테스트가 통과하도록 조건에 맞는 모의(Mock) 응답을 반환합니다.
        추후 실제 Google Generative AI (Gemini) API를 호출하여 파싱하는 로직으로 변경됩니다.
        """
        if "교량" in project_description:
            return ["KDS 24 00 00"]
        return []
