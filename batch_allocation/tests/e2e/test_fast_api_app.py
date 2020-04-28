from unittest import TestCase

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from batch_allocation.adapters.orm.orm import create_tables
from batch_allocation.entrypoints.fast_api import app
from batch_allocation.tests.e2e.fixtures import cleanup_product, create_product


class FastApiAppTestCase(TestCase):

    def setUp(self) -> None:
        self.client = TestClient(app)
        engine = create_engine("sqlite:///./sql_app.db", echo=False)
        create_tables(engine)
        self.session = Session(engine)

    def test_allocate(self):
        batch_ref = 'batch-1'
        order_ref = 'order-5'
        sku = 'RED-CHAIR'
        desired_quantity = 5
        session = self.session

        def cleanup():
            cleanup_product(sku, batch_ref, order_ref, session)

        self.addCleanup(cleanup)

        create_product(sku, batch_ref, desired_quantity, self.session)

        response = self.client.post(
            "/allocate",
            json={
                'order_ref': order_ref,
                'sku': sku,
                'quantity': desired_quantity
            })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'batchref': batch_ref})

    def test_allocate_out_of_stock(self):
        batch_ref = 'batch-1'
        order_ref = 'order-5'
        sku = 'RED-CHAIR'
        available_quantity = 10
        desired_quantity = 20
        session = self.session

        def cleanup():
            cleanup_product(sku, batch_ref, order_ref, session)

        self.addCleanup(cleanup)

        create_product(sku, batch_ref, available_quantity, self.session)

        self.session.commit()

        response = self.client.post(
            "/allocate",
            json={
                'order_ref': order_ref,
                'sku': sku,
                'quantity': desired_quantity
            })
        self.assertEqual(response.status_code, 400)
