from batch_allocation.adapters.repositories.sql_alchemy import (
    SQLAlchemyRepository,
)
from batch_allocation.domain.exceptions import UnknownSkuError
from batch_allocation.domain.model import Product
from batch_allocation.tests.integration.base_test_class import BaseSessionTestCase


class RepositoryTestCase(BaseSessionTestCase):
    def test_get_product(self):
        session = RepositoryTestCase.get_session()
        session.execute(
            "INSERT INTO products (sku) VALUES "
            '("RED-CHAIR")'
        )

        repository = SQLAlchemyRepository(session)

        product = repository.get("RED-CHAIR")

        self.assertIsInstance(product, Product)

        session.execute('DELETE FROM products where sku ="RED-CHAIR"')

    def test_get_product_wrong_sku(self):
        session = RepositoryTestCase.get_session()
        session.execute(
            "INSERT INTO products (sku) VALUES "
            '("RED-CHAIR")'
        )

        repository = SQLAlchemyRepository(session)

        with self.assertRaises(UnknownSkuError):
            product = repository.get("BLACK-TABLE")

        session.execute('DELETE FROM products where sku ="RED-CHAIR"')

    def test_add_product(self):
        session = RepositoryTestCase.get_session()

        repository = SQLAlchemyRepository(session)

        product = Product('NEW-SKU')

        repository.add(product)

        rows = list(
            session.execute(
                "SELECT sku FROM products WHERE sku = 'NEW-SKU'"
            )
        )

        self.assertEqual(len(rows), 1)

        self.assertEqual(rows[0]['sku'], product.sku)

        session.execute('DELETE FROM products where sku ="NEW-SKU"')
