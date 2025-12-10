from typing import List

from product.domain.product_fund import ProductFund
from product.domain.value_object.product_source import ProductSource
from product.domain.value_object.timestamp import Timestamp


class ProductFundData:
    def __init__(self, items: List[ProductFund], source: ProductSource, fetched_at: Timestamp):
        self.items = items
        self.source = source
        self.fetched_at = fetched_at

    def add_item(self, item: ProductFund):
        self.items.append(item)