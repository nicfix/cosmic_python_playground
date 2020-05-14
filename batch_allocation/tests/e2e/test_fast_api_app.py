from unittest import TestCase

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from batch_allocation.adapters.orm.orm import create_tables
from batch_allocation.entrypoints.fast_api import app
from batch_allocation.tests.e2e.fixtures import cleanup_product, create_product, allocate_line_item


class FastApiAppTestCase(TestCase):
    engine = None

    @classmethod
    def setUpClass(cls) -> None:
        engine = create_engine("sqlite:///./sql_app.db", echo=False)
        create_tables(engine)
        cls.engine = engine

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.session = Session(FastApiAppTestCase.engine)
        self.batch_ref = 'batch-1'
        self.order_ref = 'order-5'
        self.sku = 'RED-CHAIR'

    def tearDown(self) -> None:
        cleanup_product(self.sku, self.batch_ref, self.order_ref, self.session)

    def test_allocate(self):
        desired_quantity = 5

        create_product(self.sku, self.batch_ref, desired_quantity, self.session)

        response = self.client.post(
            "/allocate",
            json={
                'order_ref': self.order_ref,
                'sku': self.sku,
                'quantity': desired_quantity
            })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'batchref': self.batch_ref})

    def test_allocate_out_of_stock(self):
        available_quantity = 10
        desired_quantity = 20

        create_product(self.sku, self.batch_ref, available_quantity, self.session)

        response = self.client.post(
            "/allocate",
            json={
                'order_ref': self.order_ref,
                'sku': self.sku,
                'quantity': desired_quantity
            })
        self.assertEqual(response.status_code, 400)

    def test_allocations(self):
        available_quantity = 10
        order_ref = '12345'
        create_product(self.sku, self.batch_ref, available_quantity, self.session)

        allocate_line_item(1, self.sku, order_ref, self.batch_ref, available_quantity, self.session)

        response = self.client.get(
            f"/{self.sku}/allocations")
        self.assertEqual(response.status_code, 200)

        allocations = response.json()
        self.assertEqual(1, len(allocations))
        for item in allocations:
            self.assertEqual(self.sku, item.get('sku'))
