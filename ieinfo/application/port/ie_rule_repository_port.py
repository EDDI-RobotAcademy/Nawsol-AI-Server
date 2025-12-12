"""
IE_RULE Repository Port (인터페이스)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ieinfo.infrastructure.orm.ie_info import IEType


class IERuleRepositoryPort(ABC):
    """소득/지출 규칙 저장소 인터페이스"""
    
    @abstractmethod
    def find_by_keyword(self, keyword: str) -> Optional[IEType]:
        """키워드로 IE 타입 조회"""
        pass
    
    @abstractmethod
    def find_all_keywords_by_type(self, ie_type: IEType) -> List[str]:
        """특정 타입의 모든 키워드 조회"""
        pass
    
    @abstractmethod
    def save_keyword(self, keyword: str, ie_type: IEType) -> bool:
        """새 키워드 저장 (중복 시 무시)"""
        pass
    
    @abstractmethod
    def keyword_exists(self, keyword: str) -> bool:
        """키워드 존재 여부 확인"""
        pass
    
    @abstractmethod
    def get_all_rules(self) -> List[dict]:
        """모든 규칙 조회"""
        pass
