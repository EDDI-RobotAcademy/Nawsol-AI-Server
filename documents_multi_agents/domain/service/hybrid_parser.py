"""
하이브리드 파서: DB 규칙 기반 우선, 실패 시 GPT + 자동 학습
"""

import json
from typing import Dict, Any, Tuple
from documents_multi_agents.domain.service.db_rule_parser import DBRuleBasedParser, ParsedTransaction
from ieinfo.infrastructure.repository.ie_rule_repository_impl import IERuleRepositoryImpl
from ieinfo.infrastructure.orm.ie_info import IEType
from config.database.session import get_db_session
from util.log.log import Log

logger = Log.get_logger()


class HybridParser:
    """
    DB 규칙 기반 파서 + GPT 폴백 + 자동 학습
    
    처리 흐름:
    1. DB에 키워드 있음 → 규칙 기반 성공
    2. DB에 키워드 없음 → GPT 분류 + DB에 새 키워드 저장
    """
    
    def __init__(self):
        self.db_parser = DBRuleBasedParser()
        self.db_session = get_db_session()
        self.rule_repo = IERuleRepositoryImpl(self.db_session)
        
        # 통계 수집용
        self.stats = {
            'total_items': 0,
            'db_rule_success': 0,
            'gpt_fallback': 0,
            'new_keywords_learned': 0
        }
    
    def classify_item(
        self, 
        field_name: str, 
        value: str,
        doc_type_hint: str = None
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        단일 항목 분류
        
        Args:
            field_name: 항목명 (예: "급여")
            value: 금액 (예: "3000000")
            doc_type_hint: 문서 타입 힌트 ('소득', '지출', None)
        
        Returns:
            (classified_type, category, metadata)
        """
        self.stats['total_items'] += 1
        
        # DB 규칙 기반 파싱 시도
        line_text = f"{field_name}: {value}"
        parsed = self.db_parser.parse_line(line_text, doc_type_hint)
        
        if parsed:
            # ✅ DB 규칙 성공
            self.stats['db_rule_success'] += 1
            
            logger.info(f"✅ [DB-RULE] '{field_name}' → {parsed.transaction_type} "
                       f"(키워드: '{parsed.matched_keyword}')")
            
            return parsed.transaction_type, self._get_category(parsed), {
                'method': 'db_rule',
                'confidence': parsed.confidence,
                'matched_keyword': parsed.matched_keyword,
                'original_field': field_name,
                'amount': value
            }
        else:
            # ⚠️ DB에 키워드 없음 → GPT 필요
            self.stats['gpt_fallback'] += 1
            
            logger.warning(f"⚠️  [NEED-GPT] '{field_name}' (DB에 키워드 없음)")
            
            return None, None, {
                'method': 'needs_gpt',
                'confidence': 0.0,
                'reason': 'DB에 키워드 없음',
                'original_field': field_name,
                'amount': value
            }
    
    def learn_from_gpt_result(self, field_name: str, gpt_classified_type: str) -> bool:
        """
        GPT 분류 결과를 DB에 학습
        
        Args:
            field_name: 항목명 (예: "기타수당")
            gpt_classified_type: GPT가 분류한 타입 ('income' or 'expense')
        
        Returns:
            학습 성공 여부
        """
        # 키워드 추출 (항목명에서 핵심 키워드 찾기)
        keyword = self._extract_core_keyword(field_name)
        
        # 이미 DB에 있는지 확인
        if self.rule_repo.keyword_exists(keyword):
            logger.debug(f"[LEARN] 키워드 이미 존재: {keyword}")
            return False
        
        # IEType 변환
        ie_type = IEType.INCOME if gpt_classified_type == 'income' else IEType.EXPENSE
        
        # DB에 저장
        success = self.rule_repo.save_keyword(keyword, ie_type)
        
        if success:
            self.stats['new_keywords_learned'] += 1
            logger.info(f"🎓 [LEARN] 새 키워드 학습: '{keyword}' → {ie_type.value}")
            
            # 파서 키워드 재로드
            self.db_parser.reload_keywords()
        
        return success
    
    def _extract_core_keyword(self, field_name: str) -> str:
        """
        항목명에서 핵심 키워드 추출
        
        예: "기타수당" → "수당"
            "국민연금보험료" → "보험료"
        """
        # 일단 전체 항목명을 키워드로 사용
        # 향후 개선: NLP로 핵심 단어 추출
        return field_name.strip().lower()
    
    def _get_category(self, parsed: ParsedTransaction) -> str:
        """파싱 결과에서 카테고리 추론"""
        # 기본 카테고리 (추후 확장 가능)
        if parsed.transaction_type == 'income':
            return '소득'
        else:
            return '지출'
    
    def get_statistics(self) -> Dict[str, Any]:
        """파싱 통계 반환"""
        if self.stats['total_items'] == 0:
            return {
                'total_items': 0,
                'db_rule_rate': 0.0,
                'gpt_fallback_rate': 0.0,
                'new_keywords_learned': 0,
                'cost_saving_rate': 0.0
            }
        
        return {
            'total_items': self.stats['total_items'],
            'db_rule_success': self.stats['db_rule_success'],
            'gpt_fallback': self.stats['gpt_fallback'],
            'new_keywords_learned': self.stats['new_keywords_learned'],
            'db_rule_rate': self.stats['db_rule_success'] / self.stats['total_items'],
            'gpt_fallback_rate': self.stats['gpt_fallback'] / self.stats['total_items'],
            'cost_saving_rate': self.stats['db_rule_success'] / self.stats['total_items']
        }
    
    def reset_statistics(self):
        """통계 초기화"""
        self.stats = {
            'total_items': 0,
            'db_rule_success': 0,
            'gpt_fallback': 0,
            'new_keywords_learned': 0
        }
    
    def __del__(self):
        """소멸자: DB 세션 종료"""
        if hasattr(self, 'db_session'):
            self.db_session.close()
