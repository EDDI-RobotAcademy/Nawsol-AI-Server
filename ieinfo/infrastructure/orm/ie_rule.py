"""
IE_RULE ORM 모델
소득/지출 키워드 규칙 저장
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func

from config.database.session import Base
from ieinfo.infrastructure.orm.ie_info import IEType
from sqlalchemy import Enum as SAEnum


class IERule(Base):
    """
    소득/지출 키워드 규칙 테이블
    GPT가 학습한 키워드를 자동으로 저장하여 규칙 기반 파싱 정확도 향상
    """
    __tablename__ = "ie_rule"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ie_type = Column(SAEnum(IEType, native_enum=True), nullable=False, index=True)
    keyword = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # 복합 인덱스: 타입 + 키워드 조회 최적화
    __table_args__ = (
        Index('idx_ie_type_keyword', 'ie_type', 'keyword'),
    )
    
    def __repr__(self):
        return f"<IERule(id={self.id}, type={self.ie_type.value}, keyword='{self.keyword}')>"
