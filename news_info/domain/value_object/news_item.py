from dataclasses import dataclass
from typing import Optional

from news_info.domain.value_object.timestamp import Timestamp

@dataclass(frozen=True)
class NewsItem:
    title: str
    description: str
    content: Optional[str]
    link: str
    originallink: str
    published_at: Timestamp