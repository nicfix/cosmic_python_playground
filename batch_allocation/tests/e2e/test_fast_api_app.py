from unittest import TestCase

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from batch_allocation.adapters.orm.orm import create_tables
from batch_allocation.entrypoints.fast_api import app


class FastApiAppTestCase(TestCase):

    def setUp(self) -> None:
        self.client = TestClient(app)
        engine = create_engine("sqlite:///./sql_app.db", echo=False)
        create_tables(engine)
        self.session = Session(engine)

    def test_get_hello_world(self):
        client = TestClient(app)

        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'Hello': 'World'})

    def test_allocate(self):
        batch_ref = 'batch-1'
        order_ref = 'order-5'
        sku = 'RED-CHAIR'
        desired_quantity = 5

        def cleanup():
            self.session.execute(
                f"DELETE FROM batches WHERE ref = '{batch_ref}'"
            )

            self.session.execute(
                f"DELETE FROM order_lines WHERE order_ref = '{order_ref}'"
            )

            self.session.commit()

        self.addCleanup(cleanup)

        self.session.execute(
            f"INSERT INTO batches (ref, sku, _purchased_quantity, eta) "
            f"VALUES ('{batch_ref}', '{sku}', {desired_quantity}, '2020-10-10')"
        )

        self.session.commit()

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

        def cleanup():
            self.session.execute(
                f"DELETE FROM batches WHERE ref = '{batch_ref}'"
            )

            self.session.execute(
                f"DELETE FROM order_lines WHERE order_ref = '{order_ref}'"
            )

            self.session.commit()

        self.addCleanup(cleanup)

        self.session.execute(
            f"INSERT INTO batches (ref, sku, _purchased_quantity, eta) "
            f"VALUES ('{batch_ref}', '{sku}', {available_quantity}, '2020-10-10')"
        )

        self.session.commit()

        response = self.client.post(
            "/allocate",
            json={
                'order_ref': order_ref,
                'sku': sku,
                'quantity': desired_quantity
            })
        self.assertEqual(response.status_code, 400)
