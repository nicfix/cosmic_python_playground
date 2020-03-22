from dataclasses import dataclass
from datetime import date
from typing import Optional

from batch_allocation.domain.exceptions import (
    OrderLineAlreadyAllocatedError,
    NotEnoughQuantityAvailableError,
    WrongSkuError,
)


@dataclass()
class OrderLine(object):
    order_ref: str
    sku: str
    quantity: int


class Batch(object):
    def __init__(
        self, ref: str, sku: str, purchased_quantity: int, eta: Optional[date]
    ):
        self.ref = ref
        self.sku = sku
        self._purchased_quantity = purchased_quantity
        self.eta = eta
        self._allocated_order_lines = []

    @property
    def allocated_quantity(self) -> int:
        return sum([line.quantity for line in self._allocated_order_lines])

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def allocate(self, order_line: OrderLine) -> None:
        """
        :param order_line:
        :return:
        """
        if order_line.sku != self.sku:
            raise WrongSkuError()

        if order_line in self._allocated_order_lines:
            raise OrderLineAlreadyAllocatedError()

        if self.available_quantity < order_line.quantity:
            raise NotEnoughQuantityAvailableError()

        self._allocated_order_lines.append(order_line)
