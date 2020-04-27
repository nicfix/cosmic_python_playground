from typing import Tuple

from batch_allocation.adapters.repositories.abstract import (
    OrderLineAbstractRepository,
    BatchAbstractRepository, AbstractProductRepository,
)
from batch_allocation.domain.model import OrderLine, Batch, Product
from batch_allocation.service_layer.unit_of_work.abstract import AbstractUnitOfWork


class MockedOrderLineRepository(OrderLineAbstractRepository):
    """
    A mocked repository to test the interface behavior, useful to test the related services.
    """

    def __init__(self, order_lines: (OrderLine,)):
        """
        :param order_lines: (OrderLine,), the initial order_lines, this parameter has to be immutable!
        """
        self.order_lines = list(order_lines)

    def get(self, order_reference: str) -> [OrderLine]:
        return [ol for ol in self.order_lines if ol.order_ref == order_reference]

    def add(self, order_line: OrderLine):
        self.order_lines.append(order_line)


class MockedBatchRepository(BatchAbstractRepository):
    """
    A mocked repository to test the interface behavior, useful to test the related services.
    """

    def update(self, batch: Batch):
        pass

    def __init__(self, batches: (Batch,)):
        """
        :param batches: (Batch,), the initial order_lines, this parameter has to be immutable!
        """
        self.batches = list(batches)

    def get(self, reference: str) -> Batch:
        return next(b for b in self.batches if b.ref == reference)

    def get_by_sku(self, sku: str) -> [Batch]:
        return [b for b in self.batches if b.sku == sku]

    def add(self, batch: Batch):
        self.batches.append(batch)


class MockedProductRepository(AbstractProductRepository):

    def __init__(self, products: Tuple[Product] = ()):
        self.products = list(products)

    def get(self, sku: str) -> Product:
        return next(p for p in self.products if p.sku == sku)

    def add(self, product: Product):
        self.products.append(product)


class MockedUnitOfWork(AbstractUnitOfWork):

    def __init__(self, mocked_repo: BatchAbstractRepository):
        self.batches = mocked_repo
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
