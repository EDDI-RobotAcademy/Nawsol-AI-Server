"""
DB 기반 규칙 파서
IE_RULE 테이블에서 키워드를 동적으로 로드하여 분류
"""

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass

from ieinfo.infrastructure.repository.ie_rule_repository_impl import IERuleRepositoryImpl
from ieinfo.infrastructure.orm.ie_info import IEType
from config.database.session import get_db_session
from util.log.log import Log

logger = Log.get_logger()


@dataclass
class ParsedTransaction:
    """파싱된 거래 정보"""
    field_name: str  # 항목명
    amount: str  # 금액
    transaction_type: str  # 'income' or 'expense'
    confidence: float  # 신뢰도 (0.0 ~ 1.0)
    matched_keyword: str  # 매칭된 키워드


class DBRuleBasedParser:
    """DB 기반 소득/지출 분류 파서"""
    
    def __init__(self):
        self.db_session = get_db_session()
        self.rule_repo = IERuleRepositoryImpl(self.db_session)
        
        # DB에서 키워드 로드
        self._load_keywords_from_db()
        
        # 금액 패턴
        self.amount_patterns = [
            r'(\d{1,3}(?:,\d{3})+)\s*원',  # 1,000,000원
            r'(\d+)\s*원',                  # 1000000원
            r'₩\s*(\d{1,3}(?:,\d{3})+)',   # ₩1,000,000
            r'KRW\s*(\d{1,3}(?:,\d{3})+)', # KRW 1,000,000
        ]
    
    def _load_keywords_from_db(self):
        """DB에서 키워드 로드"""
        try:
            self.income_keywords = self.rule_repo.find_all_keywords_by_type(IEType.INCOME)
            self.expense_keywords = self.rule_repo.find_all_keywords_by_type(IEType.EXPENSE)
            
            logger.info(f"📚 [DB] 규칙 로드 완료: 소득 {len(self.income_keywords)}개, 지출 {len(self.expense_keywords)}개")
            
        except Exception as e:
            logger.error(f"[DB] 규칙 로드 실패: {str(e)}")
            self.income_keywords = []
            self.expense_keywords = []
    
    def reload_keywords(self):
        """키워드 재로드 (GPT가 새 키워드 추가 후 호출)"""
        logger.info("🔄 [DB] 규칙 재로드 중...")
        self._load_keywords_from_db()
    
    def parse_line(self, line: str, doc_type: str = None) -> Optional[ParsedTransaction]:
        """
        한 줄의 텍스트에서 거래 정보 파싱
        
        Args:
            line: "급여: 3000000" 같은 형식의 텍스트
            doc_type: 문서 타입 힌트 ('소득', '지출', None)
        
        Returns:
            ParsedTransaction 또는 None
        """
        # 1. 금액 추출
        amount = self._extract_amount(line)
        if not amount:
            return None
        
        # 2. 항목명 추출 (콜론 앞부분)
        field_name = self._extract_field_name(line)
        if not field_name:
            return None
        
        # 3. DB 기반 분류
        trans_type, confidence, matched_keyword = self._classify_with_db(
            field_name, 
            doc_type
        )
        
        if not trans_type:
            return None
        
        return ParsedTransaction(
            field_name=field_name,
            amount=amount,
            transaction_type=trans_type,
            confidence=confidence,
            matched_keyword=matched_keyword
        )
    
    def _extract_amount(self, text: str) -> Optional[str]:
        """텍스트에서 금액 추출"""
        for pattern in self.amount_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '').strip()
                    amount_int = int(amount_str)
                    
                    # 비정상적인 금액 필터링
                    if 1 <= amount_int <= 1000000000:
                        return amount_str
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_field_name(self, text: str) -> Optional[str]:
        """텍스트에서 항목명 추출"""
        match = re.match(r'^([^:]+):', text)
        if match:
            field_name = match.group(1).strip()
            field_name = field_name.replace('_', ' ')
            return field_name
        return None
    
    def _classify_with_db(
        self, 
        field_name: str, 
        doc_type_hint: Optional[str] = None
    ) -> Tuple[Optional[str], float, str]:
        """
        DB 키워드 기반 분류
        
        Returns:
            (transaction_type, confidence, matched_keyword)
        """
        field_lower = field_name.lower()
        
        # === 소득 키워드 매칭 ===
        for keyword in self.income_keywords:
            if keyword.lower() in field_lower:
                confidence = 1.0  # DB에 있는 키워드는 100% 신뢰
                logger.debug(f"✅ [DB-RULE] 소득 매칭: '{keyword}' in '{field_name}' (신뢰도: 1.0)")
                return 'income', confidence, keyword
        
        # === 지출 키워드 매칭 ===
        for keyword in self.expense_keywords:
            if keyword.lower() in field_lower:
                confidence = 1.0
                logger.debug(f"✅ [DB-RULE] 지출 매칭: '{keyword}' in '{field_name}' (신뢰도: 1.0)")
                return 'expense', confidence, keyword
        
        # === 매칭 실패 ===
        logger.debug(f"❌ [DB-RULE] 키워드 없음: '{field_name}' → GPT 필요")
        return None, 0.0, ""
    
    def get_statistics(self) -> dict:
        """현재 규칙 통계"""
        return {
            'income_keywords': len(self.income_keywords),
            'expense_keywords': len(self.expense_keywords),
            'total_keywords': len(self.income_keywords) + len(self.expense_keywords)
        }
    
    def __del__(self):
        """소멸자: DB 세션 종료"""
        if hasattr(self, 'db_session'):
            self.db_session.close()
