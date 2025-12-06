from abc import ABC, abstractmethod
from typing import List

from product.domain.product_etf import ProductEtf


class ProductRepositoryPort(ABC):

    @abstractmethod
    async def save_etf_batch(self, etf_list: List[ProductEtf]) -> List[ProductEtf]:
        pass

