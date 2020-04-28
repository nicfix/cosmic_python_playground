import uuid
from datetime import date
from unittest import skip

from batch_allocation.domain.model import OrderLine, Batch, Product
from batch_allocation.tests.integration.base_test_class import BaseSessionTestCase


class OrmMappingIntegrationTestCase(BaseSessionTestCase):

    def test_get_all_order_lines(self):
        session = OrmMappingIntegrationTestCase.get_session()
        session.execute(
            "INSERT INTO order_lines (order_ref, sku, quantity) VALUES "
            '("order1", "RED-CHAIR", 12),'
            '("order1", "RED-TABLE", 13),'
            '("order1", "BLUE-LIPSTICK", 14)'
        )

        expected = [
            OrderLine("order1", "RED-CHAIR", 12),
            OrderLine("order1", "RED-TABLE", 13),
            OrderLine("order1", "BLUE-LIPSTICK", 14),
        ]
        self.assertEqual(session.query(OrderLine).all(), expected)

        session.execute("DELETE FROM order_lines")

    def test_create_new_order_line(self):
        session = OrmMappingIntegrationTestCase.get_session()
        data = ("order2", "RED-CHAIR", 12)

        new_line = OrderLine(*data)

        session.add(new_line)
        session.commit()

        rows = list(
            session.execute(
                "SELECT order_ref, sku, quantity FROM order_lines WHERE order_ref = 'order2'"
            )
        )
        self.assertEqual(rows, [data])

        session.execute("DELETE FROM order_lines")

    @skip('No batch can be created without a product')
    def test_get_batch(self):
        session = OrmMappingIntegrationTestCase.get_session()
        session.execute(
            "INSERT INTO batches (ref, sku, _purchased_quantity, eta) VALUES "
            '("batch-1", "RED-CHAIR", 12, "2020-10-10")'
        )

        session.execute(
            "INSERT INTO order_lines (order_ref, sku, quantity, allocated_batch_ref) VALUES "
            '("order1", "RED-CHAIR", 12, "batch-1"),'
            '("order1", "RED-TABLE", 13, "batch-1"),'
            '("order1", "BLUE-LIPSTICK", 14, "batch-1")'
        )

        batches = session.query(Batch).all()

        expected = [
            OrderLine("order1", "RED-CHAIR", 12),
            OrderLine("order1", "RED-TABLE", 13),
            OrderLine("order1", "BLUE-LIPSTICK", 14),
        ]

        for batch in batches:
            self.assertEqual(batch._allocated_order_lines, expected)

        session.execute("DELETE FROM order_lines")

        session.execute("DELETE FROM batches")

    @skip('No direct allocation to a batch anymore, check the product one')
    def test_allocate_order_line(self):
        session = OrmMappingIntegrationTestCase.get_session()
        batch = Batch("batch-1", "RED-CHAIR", 20, date.today())
        order_line = OrderLine("order1", "RED-CHAIR", 12)

        batch.allocate(order_line)

        session.add(batch)

        batches = session.query(Batch).all()

        for bt in batches:
            self.assertEqual(bt._allocated_order_lines, [order_line])

        rows = list(
            session.execute(
                "SELECT order_ref, sku, quantity FROM order_lines WHERE order_ref = 'order1'"
            )
        )

        self.assertEqual(len(rows), 1)

        session.execute("DELETE FROM order_lines")

        session.execute("DELETE FROM batches")

    def test_get_product(self):
        session = OrmMappingIntegrationTestCase.get_session()
        sku = str(uuid.uuid4())
        session.execute(
            f"INSERT INTO products (sku) "
            f"VALUES ('{sku}')"
        )

        loaded_product = session.query(Product).get(sku)

        self.assertIsInstance(loaded_product, Product)

    def test_store_and_retrieve_product_with_batches(self):
        session = OrmMappingIntegrationTestCase.get_session()
        sku = 'RED-CHAIR'
        batch = Batch(str(uuid.uuid4()), sku, 20, date.today())

        product = Product(sku=sku, batches=[batch])

        session.add(product)

        loaded_product = session.query(Product).get(sku)

        self.assertEqual(product, loaded_product)

        self.assertEqual(product.batches, [batch])

    def test_allocate_order_line_on_product(self):
        session = OrmMappingIntegrationTestCase.get_session()
        sku = 'RED-CHAIR1'
        batch = Batch("batch-1", sku, 20, date.today())
        order_line = OrderLine("order1", sku, 12)

        product = Product(sku=sku, batches=[batch])

        product.allocate(order_line)

        session.add(product)

        loaded_product = session.query(Product).get(sku)

        loaded_batch = loaded_product.batches[0]

        self.assertEqual(batch, loaded_batch)

        self.assertEqual(order_line, loaded_batch.allocated_order_lines[0])
