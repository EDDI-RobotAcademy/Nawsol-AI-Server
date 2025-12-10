from typing import List

from product.adapter.output.product.product_data_api_adapter import ProductDataApiAdapter
from product.application.port.product_repository_port import ProductRepositoryPort
from product.domain.product_etf import ProductEtf
from product.domain.product_etf_data import ProductEtfData
from product.infrastructure.api.data_go_client import DataGoClient
from product.infrastructure.orm.product_bond import ProductBondORM
from product.infrastructure.orm.product_etf import ProductETFORM
from product.infrastructure.orm.product_fund import ProductFundORM
from util.log.log import Log

logger = Log.get_logger()
class FetchProductUseCase:
    def __init__(self, adapter: ProductDataApiAdapter, repository: ProductRepositoryPort):
        self.adapter = adapter
        self.repository = repository

    async def get_etf_data(self) -> ProductEtfData:
        return await self.adapter.get_etf_data()

    async def get_etf_data_by_date(self, date: str) -> List[ProductETFORM]:
        return await self.repository.get_etf_data_by_date(date)

    async def fetch_and_save_etf_data(self, start:str, end:str) -> List[ProductEtf]:

        client = DataGoClient()
        raw_items = await client.get_etf_data(start, end)
        etf_entities = []
        for item in raw_items:
            # 필드명 매핑 (API 응답 필드명 -> 모델 필드명)
            # itmsNm: 종목명, vs: 대비, fltRt: 등락률, mkp: 시가, hipr: 고가, lopr: 저가
            # clpr: 종가, trqu: 거래량, trPrc: 거래대금, lstgStCnt: 상장주식수, mrktTotAmt: 시가총액
            etfs = ProductEtf(
                fltRt=item.get("fltRt"),  # 등락률
                nav=item.get("nav"),  # NAV (없을 수 있음)
                mkp=item.get("mkp"),  # 시가
                hipr=item.get("hipr"),  # 고가
                lopr=item.get("lopr"),  # 저가
                trqu=item.get("trqu"),  # 거래량
                trPrc=item.get("trPrc"),  # 거래대금
                mrktTotAmt=item.get("mrktTotAmt"),  # 시가총액
                nPptTotAmt=item.get("nPptTotAmt"),  # 순자산총액 (없을 수 있음)
                stLstgCnt=item.get("lstgStCnt") or item.get("stLstgCnt"),  # 상장주식수
                bssIdxIdxNm=item.get("itmsNm"),  # 종목명
                bssIdxClpr=item.get("bssIdxClpr"),  # 기초지수종가 (없을 수 있음)
                basDt=item.get("basDt"),  # 기준일자
                clpr=item.get("clpr"),  # 종가
                vs=item.get("vs")  # 대비
            )
            etf_entities.append(etfs)
        if etf_entities:
            await self.repository.save_etf_batch(etf_entities)

        return etf_entities

    async def get_fund_data_by_date(self, date:str) -> List[ProductFundORM]:
        return await self.repository.get_fund_data_by_date(date)

    async def get_bond_data_by_date(self, date:str) -> List[ProductBondORM]:
        return await self.repository.get_bond_data_by_date(date)