import uuid
from unittest import TestCase

from batch_allocation.domain import events
from batch_allocation.service_layer import messagebus
from batch_allocation.tests.unit.fixtures import MockedRepository, MockedUnitOfWork


class ChangeBatchQuantityTestCase(TestCase):

    def setUp(self) -> None:
        batchref_to_be_changed = str(uuid.uuid4())
        other_batchref = str(uuid.uuid4())
        sku = 'Red Shoes'
        original_quantity = 20

        mocked_repo = MockedRepository(())
        mocked_unit_of_work = MockedUnitOfWork(mocked_repo)

        events_history = [
            events.BatchCreated(
                ref=batchref_to_be_changed,
                sku=sku,
                qty=original_quantity
            ),
            events.BatchCreated(
                ref=other_batchref,
                sku=sku,
                qty=original_quantity
            ),
        ]

        for event in events_history:
            messagebus.handle(event, uow=mocked_unit_of_work)

        self.uow = mocked_unit_of_work
        self.batchref_to_be_changed = batchref_to_be_changed
        self.other_batchref = other_batchref
        self.sku = sku
        self.original_quantity = original_quantity

    def test_decrease_quantity_no_re_allocation(self):
        new_quantity = 5
        event = events.BatchQuantityChanged(sku=self.sku, ref=self.batchref_to_be_changed, qty=new_quantity)

        results = messagebus.handle(event, self.uow)

        self.assertGreater(len(results), 0)
        self.assertEqual(new_quantity, results[0])

        product = self.uow.products.get(self.sku)
        self.assertEqual(product.batches[0].available_quantity, new_quantity)

    def test_decrease_quantity_reallocation_needed(self):
        allocated_quantity = 20

        # We need first to allocate the orders
        allocation_events = [
            events.AllocationRequired(
                order_ref=str(uuid.uuid4()),
                sku=self.sku,
                qty=int(allocated_quantity / 2)
            ),
            events.AllocationRequired(
                order_ref=str(uuid.uuid4()),
                sku=self.sku,
                qty=int(allocated_quantity / 2)
            )
        ]

        allocated_events_count = len(allocation_events)

        for event in allocation_events:
            messagebus.handle(event, self.uow)

        changed_batch = self.uow.products.get(self.sku).get_batch(self.batchref_to_be_changed)

        # The quantity that is allocated is correct
        self.assertEqual(allocated_quantity, changed_batch.allocated_quantity)
        # All the order lines are allocated to the same batch
        self.assertEqual(allocated_events_count, len(changed_batch.allocated_order_lines))

        # Now we can test our quantity change
        new_quantity = 10

        allocation_change_event = events.BatchQuantityChanged(
            ref=self.batchref_to_be_changed,
            sku=self.sku,
            qty=new_quantity
        )

        messagebus.handle(allocation_change_event, self.uow)

        changed_batch = self.uow.products.get(self.sku).get_batch(self.batchref_to_be_changed)

        # The quantity that is allocated is correct
        self.assertEqual(new_quantity, changed_batch.purchased_quantity)

        self.assertEqual(1, len(changed_batch.allocated_order_lines))

        self.assertEqual(new_quantity - int(allocated_quantity / 2), changed_batch.available_quantity)

        second_batch = self.uow.products.get(self.sku).get_batch(self.other_batchref)

        self.assertEqual(1, len(second_batch.allocated_order_lines))

        self.assertEqual(int(allocated_quantity / 2), second_batch.allocated_quantity)
