from abc import ABC, abstractmethod

from product.domain.product_etf import ProductEtf


class ProductDataApiPort(ABC):
    @abstractmethod
    async def get_etf_data(self) -> list[ProductEtf]:
        pass