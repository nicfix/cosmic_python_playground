import random
from datetime import date
from unittest import TestCase

from batch_allocation.domain.model import Batch, Product
from batch_allocation.tests.unit.fixtures import (
    MockedRepository,
)


class RepositoryTestCase(TestCase):
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

        self.repository = MockedRepository(tuple(self.products))

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
