from unittest import TestCase

from batch_allocation.service_layer import services
from batch_allocation.tests.unit.fixtures import MockedBatchRepository
from batch_allocation.tests.unit.test_domain import create_batch, create_order_line


class ServiceLayerTestCase(TestCase):

    def setUp(self) -> None:
        self.sku = "Red Socks"
        self.purchased_quantity = 10
        batch = create_batch(self.sku, self.purchased_quantity)

        self.batch_ref = batch.ref
        self.batches_repository = MockedBatchRepository(
            (batch,)
        )

    def test_allocate(self) -> None:
        desired_quantity = 5
        order_line = create_order_line(self.sku, desired_quantity)

        services.allocate(order_line, self.batches_repository)

        batch = self.batches_repository.get(self.batch_ref)

        self.assertEqual(self.purchased_quantity - desired_quantity, batch.available_quantity)
