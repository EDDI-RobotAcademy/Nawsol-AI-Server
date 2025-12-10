import os
from datetime import datetime

import aiohttp


class DataGoClient:

    def __init__(self):
        self.data_go_key = os.getenv("DATA_GO_KEY")
        self.data_go_etf_end_point = os.getenv("DATA_GO_ETF_END_POINT")

    async def get_etf_data(self) -> list[dict]:
        from datetime import timedelta

        results = []

        # 오늘부터 최대 7일 전까지 시도
        for days_ago in range(8):
            target_date = (datetime.today() - timedelta(days=days_ago)).strftime("%Y%m%d")

            async with aiohttp.ClientSession() as session:
                base_url = (
                    f"{self.data_go_etf_end_point}?serviceKey={self.data_go_key}&"
                    f"numOfRows=10000&pageNo=1&resultType=json&basDt={target_date}"
                )

                async with session.get(f"{base_url}") as response:
                    if response.status == 200:
                        data = await response.json()
                        # API 응답 구조 확인
                        if (data.get("response") and
                            data["response"].get("body") and
                            data["response"]["body"].get("items") and
                            data["response"]["body"]["items"].get("item")):
                            items = data["response"]["body"]["items"]["item"]
                            results.extend(items)
                            print(f"✓ ETF 데이터 조회 성공: {target_date} ({len(results)}건)")
                            # 첫 번째 아이템의 필드 확인 (디버깅용)
                            if items and len(items) > 0:
                                print(f"샘플 데이터 필드: {list(items[0].keys())}")
                            return results
                        else:
                            print(f"✗ {target_date}: 데이터 없음 - API 응답: {data}")
                    else:
                        # 에러 응답 내용 확인
                        error_text = await response.text()
                        print(f"✗ {target_date}: API Error {response.status}")
                        print(f"   URL: {base_url}")
                        print(f"   Response: {error_text[:200]}")

        # 모든 날짜에서 데이터를 찾지 못한 경우
        raise Exception(f"DataGo API Error: No data available for the last 7 days")

        return results
