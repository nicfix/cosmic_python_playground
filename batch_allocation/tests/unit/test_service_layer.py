from unittest import TestCase

from batch_allocation.service_layer import services
from batch_allocation.service_layer.services import OutOfStock
from batch_allocation.tests.unit.fixtures import MockedBatchRepository
from batch_allocation.tests.unit.test_domain import create_batch, create_order_line


def init_repository(sku, purchased_quantity, batches_number) -> MockedBatchRepository:
    batches = [create_batch(sku, purchased_quantity) for i in range(0, batches_number)]
    return MockedBatchRepository(
        tuple(batches)
    )


class ServiceLayerTestCase(TestCase):

    def setUp(self) -> None:
        self.sku = "Red Socks"
        self.purchased_quantity = 10

    def test_allocate(self) -> None:
        desired_quantity = 5
        order_line = create_order_line(self.sku, desired_quantity)

        batches_repository = init_repository(self.sku, self.purchased_quantity, 1)

        batch = services.allocate(order_line, batches_repository)

        self.assertEqual(self.purchased_quantity - desired_quantity, batch.available_quantity)

    def test_allocate_out_of_stock(self) -> None:
        desired_quantity = 20
        order_line = create_order_line(self.sku, desired_quantity)

        batches_repository = init_repository(self.sku, self.purchased_quantity, 1)

        with self.assertRaises(OutOfStock):
            services.allocate(order_line, batches_repository)
