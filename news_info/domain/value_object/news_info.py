from dataclasses import dataclass
from typing import List

from news_info.domain.value_object.news_item import NewsItem
from news_info.domain.value_object.news_source import NewsSource
from news_info.domain.value_object.timestamp import Timestamp

@dataclass(frozen=True)
class NewsInfo:
    items: List[NewsItem]
    source: NewsSource
    fetched_at: Timestamp