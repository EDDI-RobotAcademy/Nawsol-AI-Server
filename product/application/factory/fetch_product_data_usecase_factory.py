from product.adapter.output.product.product_data_api_adapter import ProductDataApiAdapter
from product.application.usecase.product_usecase import FetchProductUseCase
from product.infrastructure.repository.product_repository_impl import ProductRepositoryImpl


class FetchProductDataUsecaseFactory:
    @staticmethod
    def create() -> FetchProductUseCase:
        api_adapter = ProductDataApiAdapter()
        repository= ProductRepositoryImpl.get_instance()
        return FetchProductUseCase(api_adapter, repository)
