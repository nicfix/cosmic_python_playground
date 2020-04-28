from unittest import TestCase

from batch_allocation.service_layer import services
from batch_allocation.service_layer.services import (
    OutOfStock,
    UnknownSku,
    OrderLineAlreadyAllocatedConflict,
)
from batch_allocation.tests.unit.fixtures import MockedBatchRepository, MockedBatchesUnitOfWork
from batch_allocation.tests.unit.test_domain import create_batch, create_order_line


def init_repository(sku, purchased_quantity, batches_number) -> MockedBatchRepository:
    batches = [create_batch(sku, purchased_quantity) for i in range(0, batches_number)]
    return MockedBatchRepository(tuple(batches))


class ServiceLayerTestCase(TestCase):
    def setUp(self) -> None:
        self.sku = "Red Socks"
        self.purchased_quantity = 10

    def test_allocate(self) -> None:
        desired_quantity = 5
        order_line = create_order_line(self.sku, desired_quantity)

        batches_repository = init_repository(self.sku, self.purchased_quantity, 1)

        uow = MockedBatchesUnitOfWork(batches_repository)

        batchref = services.allocate(order_line.order_ref, order_line.sku, order_line.quantity, uow)

        batch = next(batch for batch in batches_repository.batches if batch.ref == batchref)

        self.assertEqual(
            self.purchased_quantity - desired_quantity, batch.available_quantity
        )

    def test_allocate_out_of_stock(self) -> None:
        desired_quantity = 20
        order_line = create_order_line(self.sku, desired_quantity)

        batches_repository = init_repository(self.sku, self.purchased_quantity, 1)

        uow = MockedBatchesUnitOfWork(batches_repository)

        with self.assertRaises(OutOfStock):
            services.allocate(order_line.order_ref, order_line.sku, order_line.quantity, uow)

    def test_allocate_unknown_sku(self) -> None:
        desired_quantity = 10
        order_line = create_order_line("Unknown Sku", desired_quantity)

        batches_repository = init_repository(self.sku, self.purchased_quantity, 1)

        uow = MockedBatchesUnitOfWork(batches_repository)

        with self.assertRaises(UnknownSku):
            services.allocate(order_line.order_ref, order_line.sku, order_line.quantity, uow)

    def test_allocate_duplicated_order_line(self) -> None:
        desired_quantity = 10
        order_line = create_order_line(self.sku, desired_quantity)

        batches_repository = init_repository(self.sku, self.purchased_quantity, 1)

        uow = MockedBatchesUnitOfWork(batches_repository)

        services.allocate(order_line.order_ref, order_line.sku, order_line.quantity, uow)

        with self.assertRaises(OrderLineAlreadyAllocatedConflict):
            services.allocate(order_line.order_ref, order_line.sku, order_line.quantity, uow)
