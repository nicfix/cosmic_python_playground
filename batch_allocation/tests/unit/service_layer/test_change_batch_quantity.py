import uuid
from unittest import TestCase

from batch_allocation.domain.events import BatchQuantityChanged
from batch_allocation.domain.model import Product, Batch
from batch_allocation.service_layer import messagebus
from batch_allocation.tests.unit.fixtures import MockedRepository, MockedUnitOfWork


class ChangeBatchQuantityTestCase(TestCase):

    def setUp(self) -> None:
        batchref = str(uuid.uuid4())
        sku = 'Red Shoes'
        original_quantity = 10

        batch = Batch(
            ref=batchref,
            sku=sku,
            purchased_quantity=original_quantity,
        )

        product = Product(
            sku=sku,
            batches=(batch,)
        )

        mocked_repository = MockedRepository((product,))
        mocked_unit_of_work = MockedUnitOfWork(mocked_repository)

        self.batchref = batchref
        self.uow = mocked_unit_of_work
        self.sku = sku

    def test_decrease_quantity_no_re_allocation(self):
        new_quantity = 5
        event = BatchQuantityChanged(sku=self.sku, ref=self.batchref, qty=new_quantity)

        results = messagebus.handle(event, self.uow)

        self.assertGreater(len(results), 0)
        self.assertEqual(new_quantity, results[0])

        product = self.uow.products.get(self.sku)
        self.assertEqual(product.batches[0].available_quantity, new_quantity)

