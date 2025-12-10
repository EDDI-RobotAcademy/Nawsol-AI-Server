from fastapi import APIRouter, Depends
from datetime import datetime
from account.adapter.input.web.session_helper import get_current_user
from recommendation.application.usecase.etf_recommendation_usecase import ETFRecommendationUseCase
from product.application.factory.fetch_product_data_usecase_factory import FetchProductDataUsecaseFactory
from util.log.log import Log

logger = Log.get_logger()

product_data_router = APIRouter(tags=["product"])
@product_data_router.get("/etf")
async def get_etf_info(session_id: str = Depends(get_current_user)):
    """
    사용자 맞춤 ETF 추천 API
    - 로그인 사용자: DB 소득/지출 기반 추천
    - 비로그인 사용자: Redis 세션 소득/지출 기반 추천
    """
    try:
        # ETF 추천 UseCase 호출
        usecase = ETFRecommendationUseCase.get_instance()
        result = await usecase.get_etf_recommendation(
            session_id=session_id,
            year=datetime.now().year,
            month=datetime.now().month,
            investment_goal=None,
            risk_tolerance=None
        )

        # 기존 프론트엔드 인터페이스에 맞춰 응답 형식 변환
        return {
            "source": "recommendation",
            "fetched_at": datetime.utcnow().isoformat(),
            "total_income": result.get("total_income", 0),
            "total_expense": result.get("total_expense", 0),
            "available_amount": result.get("available_amount", 0),
            "recommendation_reason": result.get("recommendation_reason", ""),
            "items": result.get("recommended_etfs", [])
        }
    except Exception as e:
        logger.error(f"Error in ETF recommendation: {str(e)}")
        # 에러 발생 시 외부 API에서 데이터 가져오기 (fallback)
        try:
            usecase = FetchProductDataUsecaseFactory.create()
            result = await usecase.get_etf_data()
            return {
                "source": result.source,
                "fetched_at": result.fetched_at.timestamp.isoformat(),
                "total_income": 0,
                "total_expense": 0,
                "available_amount": 0,
                "recommendation_reason": "소득/지출 정보가 없어 전체 ETF 목록을 보여드립니다.",
                "items": [
                    {
                        "fltRt": item.fltRt,
                        "nav": item.nav,
                        "mkp": item.mkp,
                        "hipr": item.hipr,
                        "lopr": item.lopr,
                        "trqu": item.trqu,
                        "trPrc": item.trPrc,
                        "mrktTotAmt": item.mrktTotAmt,
                        "nPptTotAmt": item.nPptTotAmt,
                        "stLstgCnt": item.stLstgCnt,
                        "bssIdxIdxNm": item.bssIdxIdxNm,
                        "bssIdxClpr": item.bssIdxClpr,
                        "basDt": item.basDt,
                        "clpr": item.clpr,
                        "vs": item.vs
                    } for item in result.items
                ]
            }
        except:
            return {
                "source": "error",
                "fetched_at": datetime.utcnow().isoformat(),
                "total_income": 0,
                "total_expense": 0,
                "available_amount": 0,
                "recommendation_reason": "ETF 데이터를 불러올 수 없습니다.",
                "items": []
            }

@product_data_router.get("/etf/{date}")
async def get_etf_info(date:str):
    usecase = FetchProductDataUsecaseFactory.create()
    result = await usecase.get_etf_data_by_date(date)
    return result


@product_data_router.post("/etf/save")
async def fetch_and_save_etf():

    usecase = FetchProductDataUsecaseFactory.create()
    saved_entities = await usecase.fetch_and_save_etf_data()

    return {
        "massage": "ETF 정보가 성공적으로 저장되었습니다.",
        "saved_count": len(saved_entities),
        "items": [
            {
                "fltRt": entity.fltRt,
                "nav": entity.nav,
                "mkp": entity.mkp,
                "hipr": entity.hipr,
                "lopr": entity.lopr,
                "trqu": entity.trqu,
                "trPrc": entity.trPrc,
                "mrktTotAmt": entity.mrktTotAmt,
                "nPptTotAmt": entity.nPptTotAmt,
                "stLstgCnt": entity.stLstgCnt,
                "bssIdxIdxNm": entity.bssIdxIdxNm,
                "bssIdxClpr": entity.bssIdxClpr,
                "basDt": entity.basDt,
                "clpr": entity.clpr,
                "vs": entity.vs,

            } for entity in saved_entities
        ]
    }

@product_data_router.get("/fund/{date}")
async def get_fund_info(date:str):
    usecase = FetchProductDataUsecaseFactory.create()
    result = await usecase.get_fund_data_by_date(date)
    return result

@product_data_router.get("/bond/{date}")
async def get_bond_info(date:str):
    usecase = FetchProductDataUsecaseFactory.create()
    result = await usecase.get_bond_data_by_date(date)
    return result