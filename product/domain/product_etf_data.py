from typing import List

from product.domain.product_etf import ProductEtf
from product.domain.value_object.product_source import ProductSource
from product.domain.value_object.timestamp import Timestamp


class ProductEtfData:
    def __init__(self, items: List[ProductEtf], source: ProductSource, fetched_at: Timestamp):
        self.items = items
        self.source = source
        self.fetched_at = fetched_at

    def add_item(self, item: ProductEtf):
        self.items.append(item)