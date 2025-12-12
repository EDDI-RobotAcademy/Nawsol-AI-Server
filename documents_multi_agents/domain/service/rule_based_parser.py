"""
규칙 기반 소득/지출 파서
GPT 없이 키워드 매칭과 정규식으로 거래 분류
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from util.log.log import Log

logger = Log.get_logger()


@dataclass
class ParsedTransaction:
    """파싱된 거래 정보"""
    field_name: str  # 항목명
    amount: str  # 금액
    transaction_type: str  # 'income' or 'expense'
    confidence: float  # 신뢰도 (0.0 ~ 1.0)
    matched_keywords: list  # 매칭된 키워드들


class RuleBasedParser:
    """규칙 기반 소득/지출 분류 파서"""
    
    def __init__(self):
        # 소득 키워드 (강도별 분류 - 높을수록 확실)
        self.income_keywords = {
            'very_high': {
                'keywords': ['급여입금', '월급', '연봉', '봉급', '총급여'],
                'weight': 0.50,
                'category': '급여'
            },
            'high': {
                'keywords': ['급여', '상여금', '보너스', '성과급', '인센티브', '수당'],
                'weight': 0.35,
                'category': '급여'
            },
            'medium': {
                'keywords': ['입금', '수입', '매출', '판매대금', '환급', '세금환급'],
                'weight': 0.25,
                'category': '기타소득'
            },
            'low': {
                'keywords': ['이자', '배당', '캐시백', '포인트', '리워드'],
                'weight': 0.15,
                'category': '금융소득'
            }
        }
        
        # 지출 키워드 (강도별 분류)
        self.expense_keywords = {
            'very_high': {
                'keywords': ['카드결제', '체크카드', '신용카드', '공제액', '보험료'],
                'weight': 0.50
            },
            'high': {
                'keywords': ['출금', '지출', '이체', '송금', '납부', '세금', '소득세', '지방소득세'],
                'weight': 0.35
            },
            'medium': {
                'keywords': ['결제', '구매', '요금', '비용', '사용액'],
                'weight': 0.25
            },
            'low': {
                'keywords': ['차감', '공제'],
                'weight': 0.15
            }
        }
        
        # 금액 패턴 (다양한 형식 대응)
        self.amount_patterns = [
            r'(\d{1,3}(?:,\d{3})+)\s*원',  # 1,000,000원
            r'(\d+)\s*원',                  # 1000000원
            r'₩\s*(\d{1,3}(?:,\d{3})+)',   # ₩1,000,000
            r'KRW\s*(\d{1,3}(?:,\d{3})+)', # KRW 1,000,000
        ]
    
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
        
        # 3. 소득/지출 분류 및 신뢰도 계산
        trans_type, confidence, matched_keywords = self._classify_transaction(
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
            matched_keywords=matched_keywords
        )
    
    def _extract_amount(self, text: str) -> Optional[str]:
        """텍스트에서 금액 추출"""
        for pattern in self.amount_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '').strip()
                    amount_int = int(amount_str)
                    
                    # 비정상적인 금액 필터링 (1원 ~ 10억원)
                    if 1 <= amount_int <= 1000000000:
                        return amount_str
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_field_name(self, text: str) -> Optional[str]:
        """텍스트에서 항목명 추출 (콜론 앞부분)"""
        # "급여: 3000000" 형식에서 "급여" 추출
        match = re.match(r'^([^:]+):', text)
        if match:
            field_name = match.group(1).strip()
            # 언더스코어를 공백으로 변환
            field_name = field_name.replace('_', ' ')
            return field_name
        return None
    
    def _classify_transaction(
        self, 
        field_name: str, 
        doc_type_hint: Optional[str] = None
    ) -> Tuple[Optional[str], float, list]:
        """
        항목명을 기반으로 소득/지출 분류 및 신뢰도 계산
        
        Returns:
            (transaction_type, confidence, matched_keywords)
            - transaction_type: 'income' or 'expense' or None
            - confidence: 0.0 ~ 1.0
            - matched_keywords: 매칭된 키워드 리스트
        """
        income_score = 0.0
        expense_score = 0.0
        income_matches = []
        expense_matches = []
        
        field_lower = field_name.lower()
        
        # === 소득 키워드 매칭 ===
        for strength, info in self.income_keywords.items():
            for keyword in info['keywords']:
                if keyword in field_lower:
                    income_score += info['weight']
                    income_matches.append(keyword)
                    logger.debug(f"[RULE] 소득 키워드 매칭: '{keyword}' in '{field_name}' (강도: {strength}, +{info['weight']})")
                    break  # 같은 강도에서 중복 점수 방지
        
        # === 지출 키워드 매칭 ===
        for strength, info in self.expense_keywords.items():
            for keyword in info['keywords']:
                if keyword in field_lower:
                    expense_score += info['weight']
                    expense_matches.append(keyword)
                    logger.debug(f"[RULE] 지출 키워드 매칭: '{keyword}' in '{field_name}' (강도: {strength}, +{info['weight']})")
                    break
        
        # === doc_type 힌트 보너스 (PDF 타입 정보) ===
        if doc_type_hint:
            if "소득" in doc_type_hint or "income" in doc_type_hint.lower():
                income_score += 0.20
                logger.debug(f"[RULE] 문서 타입 힌트: 소득 (+0.20)")
            elif "지출" in doc_type_hint or "expense" in doc_type_hint.lower():
                expense_score += 0.20
                logger.debug(f"[RULE] 문서 타입 힌트: 지출 (+0.20)")
        
        # === 특정 항목 강제 분류 규칙 ===
        # 보험료, 세금 등은 소득 명세서에 있어도 실제론 지출
        forced_expense_keywords = ['보험료', '보험', '세금', '소득세', '지방소득세', '공제액']
        for keyword in forced_expense_keywords:
            if keyword in field_lower and "공제대상" not in field_lower:
                expense_score += 0.40
                expense_matches.append(f"강제분류:{keyword}")
                logger.debug(f"[RULE] 강제 지출 분류: '{keyword}' in '{field_name}' (+0.40)")
        
        # === 최종 판단 ===
        # 신뢰도 임계값: 0.4 이상이어야 분류
        confidence_threshold = 0.40
        
        if income_score > expense_score and income_score >= confidence_threshold:
            final_type = 'income'
            final_confidence = min(income_score, 1.0)
            final_matches = income_matches
        elif expense_score > income_score and expense_score >= confidence_threshold:
            final_type = 'expense'
            final_confidence = min(expense_score, 1.0)
            final_matches = expense_matches
        else:
            # 신뢰도 부족 - GPT로 넘김
            final_type = None
            final_confidence = max(income_score, expense_score)
            final_matches = []
            logger.debug(f"[RULE] 신뢰도 부족: income={income_score:.2f}, expense={expense_score:.2f}")
        
        logger.debug(f"[RULE] 최종 분류: {final_type}, 신뢰도={final_confidence:.2f}")
        
        return final_type, final_confidence, final_matches
