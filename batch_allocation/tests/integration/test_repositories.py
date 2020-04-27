from datetime import date
from unittest import skip

from batch_allocation.adapters.repositories.sql_alchemy import (
    OrderLineSQLAlchemyRepository,
    BatchSQLAlchemyRepository,
)
from batch_allocation.domain.model import OrderLine, Batch
from batch_allocation.tests.integration.base_test_class import BaseSessionTestCase


@skip("We deprecated the OrderLineRepository")
class OrderLineRepositoryTestCase(BaseSessionTestCase):
    def test_get_by_order(self):
        session = OrderLineRepositoryTestCase.get_session()
        session.execute(
            "INSERT INTO order_lines (order_ref, sku, quantity) VALUES "
            '("order1", "RED-CHAIR", 12),'
            '("order1", "RED-TABLE", 13),'
            '("order1", "BLUE-LIPSTICK", 14)'
        )

        repository = OrderLineSQLAlchemyRepository(session)

        order_lines = repository.get("order1")

        self.assertEqual(len(order_lines), 3)

        for line in order_lines:
            self.assertIsInstance(line, OrderLine)

        session.execute("DELETE FROM order_lines")

    def test_add_new_order_line(self):
        session = OrderLineRepositoryTestCase.get_session()

        sku = "Black belt"
        order_ref = "order2"

        order_line_instance = OrderLine(order_ref=order_ref, sku=sku, quantity=20)

        repository = OrderLineSQLAlchemyRepository(session)

        repository.add(order_line_instance)

        rows = session.execute(
            "SELECT order_ref, sku, quantity FROM order_lines WHERE order_ref = '%s'"
            % order_ref
        )

        rows = list(rows)

        self.assertEqual(1, len(rows))
        self.assertEqual(rows[0][1], sku)

        session.execute("DELETE FROM order_lines")


class BatchRepositoryTestCase(BaseSessionTestCase):
    def test_get_batch(self):
        session = BatchRepositoryTestCase.get_session()
        session.execute(
            "INSERT INTO batches (ref, sku, _purchased_quantity) VALUES "
            '("batch-1", "RED-CHAIR", 12)'
        )

        repository = BatchSQLAlchemyRepository(session)

        batch = repository.get("batch-1")

        self.assertIsInstance(batch, Batch)

        session.execute("DELETE FROM batches")

    def test_allocate_order_lines(self):
        session = BatchRepositoryTestCase.get_session()
        repository = BatchSQLAlchemyRepository(session)

        batch = Batch("batch-1", "RED-CHAIR", 20, date.today())
        order_line = OrderLine("order1", "RED-CHAIR", 12)

        batch.allocate(order_line)

        repository.add(batch)

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

    def test_update_batch(self):
        session = BatchRepositoryTestCase.get_session()
        repository = BatchSQLAlchemyRepository(session)

        batch = Batch("batch-1", "RED-CHAIR", 20, date.today())
        order_line = OrderLine("order1", "RED-CHAIR", 12)

        repository.add(batch)

        batch.allocate(order_line)

        repository.update(batch)

        batch = session.query(Batch).filter_by(ref=batch.ref).one()

        self.assertEqual(batch._allocated_order_lines, [order_line])