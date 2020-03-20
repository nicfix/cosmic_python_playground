from datetime import date

from batch_allocation.model import OrderLine, Batch
from tests.integration.base_test_class import BaseTestCase


class OrmMappingIntegrationTestCase(BaseTestCase):
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
