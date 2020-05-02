from typing import Iterable

from batch_allocation.adapters.repositories.abstract import (
    AbstractRepository,
)
from batch_allocation.domain.exceptions import UnknownSkuError
from batch_allocation.domain.model import Product
from batch_allocation.service_layer.unit_of_work.abstract import AbstractUnitOfWork


class MockedRepository(AbstractRepository):

    def __init__(self, products: Iterable[Product] = ()):
        self.products = list(products)

    def get(self, sku: str) -> Product:
        try:
            return next(p for p in self.products if p.sku == sku)
        except StopIteration:
            raise UnknownSkuError()

    def add(self, product: Product):
        self.products.append(product)


class MockedUnitOfWork(AbstractUnitOfWork):
    def __init__(self, mocked_repo: AbstractRepository):
        self.products = mocked_repo
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
