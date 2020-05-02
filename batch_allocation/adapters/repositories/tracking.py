from typing import Set

from batch_allocation.adapters.repositories.abstract import AbstractRepository
from batch_allocation.domain import model


class TrackingRepository(AbstractRepository):
    seen: Set[model.Product]

    def __init__(self, delegate: AbstractRepository):
        self.seen = set()
        self.delegate = delegate

    def add(self, product: model.Product):  # (1)
        self.delegate.add(product)  # (1)
        self.seen.add(product)

    def get(self, sku) -> model.Product:
        product = self.delegate.get(sku)
        self.seen.add(product)
        return product
