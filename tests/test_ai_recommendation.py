import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pytest_bdd import scenarios, given, when, then
from services.ai_recommender import AIRecommender

# BDD 시나리오 로드
scenarios('features/ai_recommendation.feature')

@given('사용자가 AI 추천 입력창에 "왕복 4차선 교량 신설 공사"라고 입력한다', target_fixture="user_input")
def user_input():
    return "왕복 4차선 교량 신설 공사"

@when('추천 엔진이 Gemini API에 분석을 요청한다', target_fixture="recommendation_result")
def request_recommendation(user_input):
    # 실제 AIRecommender 모듈을 가져와 로직 수행
    recommender = AIRecommender()
    return recommender.get_recommendations(user_input)

@then('응답 결과에 "KDS 24" (교량설계기준) 계열의 코드가 포함되어야 한다')
def verify_recommended_code(recommendation_result):
    assert recommendation_result is not None
    # 임시 반환값 "KDS 24 00 00"에 "KDS 24"가 포함되어 있는지 확인
    assert any("KDS 24" in code for code in recommendation_result), "교량 설계 기준 코드가 반환되지 않았습니다."

@then('결과는 구조화된 리스트(JSON 등) 형태로 파싱 가능해야 한다')
def verify_result_format(recommendation_result):
    assert isinstance(recommendation_result, list), "결과 데이터가 리스트 타입이 아닙니다."
