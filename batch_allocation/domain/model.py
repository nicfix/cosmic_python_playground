from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Iterable

import batch_allocation.domain.commands
from batch_allocation.domain import events
from batch_allocation.domain.events import Event
from batch_allocation.domain.exceptions import (
    OrderLineAlreadyAllocatedError,
    NotEnoughQuantityAvailableError,
    UnknownSkuError, OutOfStockError, UnknownRefError,
)


@dataclass()
class OrderLine(object):
    order_ref: str
    sku: str
    quantity: int


class Batch(object):
    def __init__(
            self, ref: str, sku: str, purchased_quantity: int, eta: Optional[date] = None
    ):
        self.ref = ref
        self.sku = sku
        self._purchased_quantity = purchased_quantity
        self.eta = eta
        self._allocated_order_lines = []

    @property
    def allocated_order_lines(self) -> List[OrderLine]:
        return self._allocated_order_lines

    @property
    def allocated_quantity(self) -> int:
        return sum([line.quantity for line in self._allocated_order_lines])

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    @property
    def purchased_quantity(self):
        return self._purchased_quantity

    @purchased_quantity.setter
    def purchased_quantity(self, new_quantity):
        self._purchased_quantity = new_quantity

    def allocate(self, order_line: OrderLine) -> None:
        """
        Attempts to allocate an order line to this batch, raises exceptions in case of failure.
        :param order_line: OrderLine
        :raises UnknownSkuError: in case of a wrong sku in the order line
        :raises OrderLineAlreadyAllocatedError: if the same order line is already allocated to this batch
        :raises NotEnoughQuantityAvailable: if the order line cannot be allocated to the current batch
        """
        if order_line.sku != self.sku:
            raise UnknownSkuError()

        if order_line in self._allocated_order_lines:
            raise OrderLineAlreadyAllocatedError()

        if self.available_quantity < order_line.quantity:
            raise NotEnoughQuantityAvailableError()

        self._allocated_order_lines.append(order_line)

    def deallocate_one(self) -> OrderLine:
        """
        Deallocates an orderline from this batch and returns it.
        """
        return self._allocated_order_lines.pop()


class Product:

    def __init__(self, sku: str, batches: Iterable[Batch] = (), evts: Iterable[events.Event] = ()):
        self.sku = sku
        self._batches = list(batches)
        self._events = list(evts)

    @property
    def events(self) -> List[Event]:
        return self._events

    @events.setter
    def events(self, evts: List[Event]):
        self._events = evts

    @property
    def batches(self) -> List[Batch]:
        return self._batches

    @batches.setter
    def batches(self, batches: List[Batch]):
        self._batches = batches

    def change_batch_quantity(self, ref, new_quantity) -> int:
        batch = self.get_batch(ref)
        batch.purchased_quantity = new_quantity
        while batch.available_quantity < 0:
            line = batch.deallocate_one()
            self.events.append(
                batch_allocation.domain.commands.AllocationRequired(
                    order_ref=line.order_ref,
                    sku=line.sku,
                    qty=line.quantity
                )
            )

        return new_quantity

    def get_batch(self, ref: str) -> Batch:
        try:
            return next(b for b in self.batches if b.ref == ref)
        except StopIteration:
            raise UnknownRefError()

    def allocate(self, order_line: OrderLine) -> Batch:
        for batch in self.batches:
            try:
                batch.allocate(order_line=order_line)
                return batch
            except OrderLineAlreadyAllocatedError as e:
                raise e
            except UnknownSkuError:
                """
                One or more batches might have the wrong sku, we don't care, maybe one of the other ones will be
                compatible. We could filter it before.
                """
                pass
            except NotEnoughQuantityAvailableError:
                """
                One or more batches might have not enough quantity, we don't care, maybe one of the other ones will be
                compatible. We could filter it before.
                """
                pass

        self.events.append(events.OutOfStock(self.sku))

        raise OutOfStockError()
