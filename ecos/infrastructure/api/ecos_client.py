import os
from datetime import datetime, timedelta
import aiohttp

from ecos.infrastructure.orm.exchange_rate import ExchangeType

class EcosClient:

    def __init__(self):
        self.base_url = os.getenv("ECOS_BASE_URL")
        self.rate_url = os.getenv("ECOS_RATE_URL")
        self.api_key = os.getenv("ECOS_API_KEY")
        self.exchange_key = os.getenv("ECOS_EXCHANGE_SERVICE_KEY")
        self.interest_key = os.getenv("ECOS_INTEREST_SERVICE_KEY")

    ## 환율
    async def get_exchange_rate(self, start: str = None, end: str = None) -> list[dict]:
        if start and end:
            yesterday = datetime.strptime(start, "%Y%m%d").strftime("%Y%m%d")
            today = datetime.strptime(end, "%Y%m%d").strftime("%Y%m%d")
        else:
            yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
            today = datetime.today().strftime("%Y%m%d")

        results = []

        async with aiohttp.ClientSession() as session:
            base_url = (
                f"{self.base_url}/{self.rate_url}/"
                f"{self.api_key}/json/kr/1/100000/"
                f"{self.exchange_key}/D/"
                f"{yesterday}/{today}"
            )

            for ex_type in [ExchangeType.DOLLAR, ExchangeType.YEN, ExchangeType.EURO]:
                url = f"{base_url}/{ex_type.value}"
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Ecos API {ex_type.name} Error {response.status}")
                    data = await response.json()
                    stat = data.get("StatisticSearch", {})
                    rows = stat.get("row", [])
                    results.extend(rows)

        return results

    ## 금리
    async def get_interest_rate(self, start:str = None, end:str = None) -> list[dict]:
        if start is not None and end is not None:
            yesterday = datetime.strptime(start, "%Y%m%d").strftime("%Y%m%d")
            today = datetime.strptime(end, "%Y%m%d").strftime("%Y%m%d")
        else:
            yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
            today = datetime.today().strftime("%Y%m%d")

        results = []

        async with aiohttp.ClientSession() as session:
            url = (
                f"{self.base_url}/{self.rate_url}/"
                f"{self.api_key}/json/kr/1/100000/"
                f"{self.interest_key}/D/"
                f"{yesterday}/{today}"
            )

            async with session.get(f"{url}") as response:
                if response.status != 200:
                    raise Exception(f"Ecos API Interest Error {response.status}")
                data = await response.json()
                stat = data.get("StatisticSearch", {})
                rows = stat.get("row", [])
                results.extend(rows)


        return results