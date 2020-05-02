import abc

from batch_allocation.domain.model import Product


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, sku: str) -> Product:
        raise NotImplementedError()

    @abc.abstractmethod
    def add(self, product: Product):
        raise NotImplementedError()
