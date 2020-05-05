import uuid
from unittest import TestCase

from batch_allocation.domain.events import BatchCreated
from batch_allocation.service_layer import messagebus
from batch_allocation.tests.unit.fixtures import MockedRepository, MockedUnitOfWork


class BatchCreationTestCase(TestCase):

    def test_add_batch_for_new_product(self):
        ref = str(uuid.uuid4())
        sku = "New Shiny Product"
        quantity = 10

        mocked_repo = MockedRepository()
        mocked_uow = MockedUnitOfWork(mocked_repo)

        event = BatchCreated(
            ref=ref,
            sku=sku,
            qty=quantity,
            eta=None
        )

        batchref = messagebus.handle(event, mocked_uow)[0]

        self.assertEqual(ref, batchref)

        self.assertEqual(len(mocked_repo.products), 1)

        created_product = mocked_repo.products[0]
        self.assertEqual(created_product.sku, sku)

        self.assertEqual(len(created_product.batches), 1)

        new_batch = created_product.batches[0]
        self.assertEqual(new_batch.ref, batchref)
