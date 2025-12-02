from abc import ABC, abstractmethod
from typing import List

from ecos.domain.ecos import Ecos


class EcosRepositoryPort(ABC):

    @abstractmethod
    async def save_exchange_rate(self, ecos: Ecos) -> Ecos:
        pass

    @abstractmethod
    async def save_exchange_rates_batch(self, ecos_list: List[Ecos]) -> List[Ecos]:
        pass