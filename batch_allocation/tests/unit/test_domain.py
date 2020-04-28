import uuid
from datetime import date
from unittest import TestCase

from batch_allocation.domain.model import (
    OrderLine,
    Batch,
)
from batch_allocation.domain.exceptions import (
    OrderLineAlreadyAllocatedError,
    NotEnoughQuantityAvailableError,
    UnknownSkuError, OutOfStockError,
)
from batch_allocation.domain.service_functions import allocate


def create_order_line(sku, desired_quantity):
    order_ref = str(uuid.uuid4())

    order_line = OrderLine(order_ref=order_ref, sku=sku, quantity=desired_quantity)

    return order_line


def create_batch(sku, available_quantity):
    batch_ref = str(uuid.uuid4())

    batch = Batch(
        ref=batch_ref, sku=sku, purchased_quantity=available_quantity, eta=date.today()
    )

    return batch


def create_batch_and_line(sku, available_quantity, desired_quantity):
    order_line = create_order_line(sku, desired_quantity)

    batch = create_batch(sku, available_quantity)

    return batch, order_line


class BatchAllocationTestCase(TestCase):
    def test_create_order_line(self):
        order_ref = str(uuid.uuid4())
        product_sku = "Red Chair"
        desired_quantity = 10

        order_line = OrderLine(
            order_ref=order_ref, sku=product_sku, quantity=desired_quantity
        )

        self.assertEqual(order_line.quantity, desired_quantity)

    def test_reserve_stock_in_batch(self):
        product_sku = "Red Chair"
        available_quantity = 20
        desired_quantity = 10

        batch, order_line = create_batch_and_line(
            product_sku, available_quantity, desired_quantity
        )

        batch.allocate(order_line)

        self.assertEqual(
            batch.available_quantity, available_quantity - desired_quantity
        )

        self.assertEqual(batch.allocated_quantity, desired_quantity)

    def test_reserve_stock_in_batch_out_of_stock(self):
        product_sku = "Red Chair"

        desired_quantity = 30

        available_quantity = 20

        batch, order_line = create_batch_and_line(
            product_sku, available_quantity, desired_quantity
        )

        with self.assertRaises(NotEnoughQuantityAvailableError):
            batch.allocate(order_line)

    def test_reserve_stock_in_batch_multiple_times(self):
        product_sku = "Red Chair"

        desired_quantity = 10

        available_quantity = 20

        batch, order_line = create_batch_and_line(
            product_sku, available_quantity, desired_quantity
        )

        batch.allocate(order_line)

        with self.assertRaises(OrderLineAlreadyAllocatedError):
            batch.allocate(order_line)

    def test_allocate_stock_multiple_order_lines(self):
        product_sku = "Red Chair"

        available_quantity = 20

        batch = create_batch(product_sku, available_quantity)

        desired_quantity = 10

        for i in range(0, 2):
            order_line = create_order_line(product_sku, desired_quantity)
            batch.allocate(order_line)

            requested_quantity = desired_quantity * (i + 1)

            self.assertEqual(
                batch.available_quantity, available_quantity - requested_quantity
            )
            self.assertEqual(batch.allocated_quantity, requested_quantity)

    def test_allocate_different_sku(self):
        batch = create_batch("Red Chair", 20)

        order_line = create_order_line("Blue table", 2)

        with self.assertRaises(UnknownSkuError):
            batch.allocate(order_line)


class AllocateServiceFunctionTestCase(TestCase):
    def test_allocate(self):
        skus = ["Red shoes", "Blue laces", "Black pants"]

        batches = [create_batch(sku, 10) for sku in skus]

        order_lines = [create_order_line(sku, 1) for sku in skus]

        allocate(batches, order_lines)

    def test_duplicated_order_line(self):
        order_ref = "order1"
        sku = "Red shoes"
        order_lines = [
            OrderLine(order_ref=order_ref, sku=sku, quantity=10),
            OrderLine(order_ref=order_ref, sku=sku, quantity=10),
        ]

        batches = [create_batch(sku, 10) for i in range(0, 10)]

        with self.assertRaises(OrderLineAlreadyAllocatedError):
            allocate(batches, order_lines)

    def test_out_of_stock_error(self):
        order_ref = "order1"
        sku = "Red shoes"
        order_lines = [
            OrderLine(order_ref=order_ref, sku=sku, quantity=10),
            OrderLine(order_ref=order_ref, sku=sku, quantity=10),
        ]

        batches = [create_batch(sku, 1) for i in range(0, 10)]

        with self.assertRaises(OutOfStockError):
            allocate(batches, order_lines)
