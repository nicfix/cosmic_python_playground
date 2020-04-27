import random
from datetime import date
from unittest import TestCase, skip

from batch_allocation.domain.model import OrderLine, Batch, Product
from batch_allocation.tests.unit.fixtures import (
    MockedOrderLineRepository,
    MockedBatchRepository, MockedProductRepository,
)


@skip("We are removing the repositories that are not the product one")
class TestOrderLineRepository(TestCase):
    def setUp(self) -> None:
        self.order_ref = "order-1"
        self.skus = ["Red chair", "Blue door", "Black table"]

        self.order_lines = [
            OrderLine(self.order_ref, sku, random.randrange(0, 100, 1))
            for sku in self.skus
        ]

        self.repository = MockedOrderLineRepository(tuple(self.order_lines))

    def test_get_order_line(self):
        order_lines = self.repository.get(self.order_ref)

        self.assertEqual(self.order_lines, order_lines)

    def test_add_order_line(self):
        new_order_ref = "order-5"

        new_order_order_line = OrderLine(
            order_ref=new_order_ref, sku=self.skus[0], quantity=10
        )

        self.repository.add(new_order_order_line)

        old_order_order_line = OrderLine(
            order_ref=self.order_ref, sku=self.skus[0], quantity=10
        )

        self.repository.add(old_order_order_line)

        new_order_order_lines = self.repository.get(new_order_ref)

        self.assertEqual([new_order_order_line], new_order_order_lines)

        old_order_order_lines = self.repository.get(self.order_ref)

        self.assertEqual(
            self.order_lines + [old_order_order_line], old_order_order_lines
        )


@skip("We are removing the repositories that are not the product one")
class TestBatchRepository(TestCase):
    def setUp(self) -> None:
        self.refs = ["batch-1", "batch-2", "batch-3"]

        self.batches = [
            Batch(
                ref=ref,
                sku="Red socks",
                purchased_quantity=random.randrange(0, 100, 1),
                eta=date.today(),
            )
            for ref in self.refs
        ]

        self.repository = MockedBatchRepository(tuple(self.batches))

    def test_get_batch(self):
        batch = self.repository.get(self.refs[0])
        self.assertEqual(self.batches[0], batch)

    def test_add_batch(self):
        batch = Batch(
            ref="new_ref", sku="Black pants", purchased_quantity=10, eta=date.today()
        )
        self.repository.add(batch)
        retrieved_batch = self.repository.get(batch.ref)
        self.assertEqual(batch, retrieved_batch)


class TestProductRepository(TestCase):
    def setUp(self) -> None:
        self.refs = ["batch-1", "batch-2", "batch-3"]
        self.skus = ["Red Socks", "Blue pants", "Black chair"]
        self.products = []

        for sku in self.skus:
            batches = [
                Batch(
                    ref=f'{sku}_{ref}',
                    sku=sku,
                    purchased_quantity=random.randrange(0, 100, 1),
                    eta=date.today(),
                )
                for ref in self.refs
            ]

            self.products.append(Product(sku, batches))

        self.repository = MockedProductRepository(tuple(self.products))

    def test_get_product(self):
        products = self.repository.get(self.skus[0])
        self.assertEqual(self.products[0], products)

    def test_add_product(self):
        new_sku = "Black pants"

        product = Product(
            new_sku,
            []
        )
        self.repository.add(product)
        retrieved_product = self.repository.get(new_sku)
        self.assertEqual(product, retrieved_product)
