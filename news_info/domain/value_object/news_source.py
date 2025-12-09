from dataclasses import dataclass

@dataclass(frozen=True)
class NewsSource:
    name: str