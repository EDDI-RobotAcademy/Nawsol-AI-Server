from ecos.adapter.output.ecos.ecos_data_api_adapter import EcosDataApiAdapter
from ecos.application.usecase.ecos_usecase import FetchEcosUseCase
from ecos.infrastructure.repository.ecos_repository_impl import EcosRepositoryImpl


class FetchEcosDataUsecaseFactory:
    @staticmethod
    def create() -> FetchEcosUseCase:
        api_adapter = EcosDataApiAdapter()
        repository = EcosRepositoryImpl.get_instance()
        return FetchEcosUseCase(api_adapter, repository)