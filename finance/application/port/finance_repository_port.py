from abc import ABC, abstractmethod
from typing import List

from finance.infrastructure.orm.finance_orm import FinanceORM


class FinanceRepositoryPort(ABC):

    @abstractmethod
    def save_finance_data(self, finance_data: List[FinanceORM]):
        pass
