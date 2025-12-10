"""
ETF 추천 Router
로그인 여부에 따라 DB 또는 Redis 데이터 기반 ETF 추천
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from account.adapter.input.web.session_helper import get_current_user
from recommendation.application.usecase.etf_recommendation_usecase import ETFRecommendationUseCase
from util.log.log import Log

logger = Log.get_logger()
etf_recommendation_router = APIRouter(tags=["etf_recommendation"])
usecase = ETFRecommendationUseCase.get_instance()


@etf_recommendation_router.get("/recommend")
async def get_etf_recommendation(
    year: int = Query(None, description="조회 연도 (로그인 사용자용)"),
    month: int = Query(None, description="조회 월 (로그인 사용자용)"),
    investment_goal: str = Query(None, description="투자 목표 (예: 노후 준비, 단기 수익)"),
    risk_tolerance: str = Query(None, description="위험 감수도 (낮음/보통/높음)"),
    session_id: str = Depends(get_current_user)
):
    """
    사용자 재무 정보를 기반으로 ETF 추천
    
    - 로그인 사용자: DB(IE_INFO)의 데이터 기반 추천
    - 비로그인 사용자: Redis 세션 데이터 기반 추천
    
    Args:
        year: 조회 연도 (로그인 사용자, 선택)
        month: 조회 월 (로그인 사용자, 선택)
        investment_goal: 투자 목표
        risk_tolerance: 위험 감수도
        session_id: 세션 ID (자동 주입)
    
    Returns:
        ETF 추천 결과
    """
    try:
        # 연도/월이 지정되지 않은 경우 현재 날짜 사용
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        logger.info(
            f"ETF recommendation request - "
            f"session: {session_id[:8]}..., "
            f"year: {year}, month: {month}"
        )
        
        # ETF 추천 실행
        result = await usecase.get_etf_recommendation(
            session_id=session_id,
            year=year,
            month=month,
            investment_goal=investment_goal,
            risk_tolerance=risk_tolerance
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in ETF recommendation endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"ETF 추천 중 오류가 발생했습니다: {str(e)}"
        }
