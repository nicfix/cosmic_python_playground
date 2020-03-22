import random
from datetime import date
from unittest import TestCase

from batch_allocation.domain.model import OrderLine, Batch
from batch_allocation.tests.unit.fixtures import MockedOrderLineRepository, MockedBatchRepository


class TestOrderLineRepository(TestCase):

    def setUp(self) -> None:
        self.order_ref = 'order-1'
        self.skus = [
            'Red chair',
            'Blue door',
            'Black table'
        ]

        self.order_lines = [OrderLine(
            self.order_ref,
            sku,
            random.randrange(0, 100, 1)
        ) for sku in self.skus]

        self.repository = MockedOrderLineRepository(tuple(self.order_lines))

    def test_get_order_line(self):
        order_lines = self.repository.get(self.order_ref)

        self.assertEqual(self.order_lines, order_lines)

    def test_add_order_line(self):
        new_order_ref = 'order-5'

        new_order_order_line = OrderLine(
            order_ref=new_order_ref,
            sku=self.skus[0],
            quantity=10
        )

        self.repository.add(new_order_order_line)

        old_order_order_line = OrderLine(
            order_ref=self.order_ref,
            sku=self.skus[0],
            quantity=10
        )

        self.repository.add(old_order_order_line)

        new_order_order_lines = self.repository.get(new_order_ref)

        self.assertEqual([new_order_order_line], new_order_order_lines)

        old_order_order_lines = self.repository.get(self.order_ref)

        self.assertEqual(self.order_lines + [old_order_order_line], old_order_order_lines)


class TestBatchRepository(TestCase):

    def setUp(self) -> None:
        self.refs = [
            'batch-1',
            'batch-2',
            'batch-3'
        ]

        self.batches = [
            Batch(
                ref=ref,
                sku='Red socks',
                purchased_quantity=random.randrange(0, 100, 1),
                eta=date.today()
            ) for ref in self.refs
        ]

        self.repository = MockedBatchRepository(tuple(self.batches))

    def test_get_batch(self):
        batch = self.repository.get(self.refs[0])

        self.assertEqual(self.batches[0], batch)

    def test_add_batch(self):
        batch = Batch(ref='new_ref', sku='Black pants', purchased_quantity=10, eta=date.today())

        self.repository.add(batch)

        retrieved_batch = self.repository.get(batch.ref)

        self.assertEqual(batch, retrieved_batch)
