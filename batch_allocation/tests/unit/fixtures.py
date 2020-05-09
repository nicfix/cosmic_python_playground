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
    def collect_new_events(self):
        products = [product for product in self.products.products]
        events = []
        for product in products:
            events += product.events
            product.events = []  # Cleanup events that have been collected, I should find a better way/place to
            # store the events, let's see if they propose something further in the book
        return events

    def __init__(self, mocked_repo: MockedRepository):
        self.products = mocked_repo
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
