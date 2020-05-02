from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Iterable

from sqlalchemy import orm

from batch_allocation.domain import events
from batch_allocation.domain.events import Event
from batch_allocation.domain.exceptions import (
    OrderLineAlreadyAllocatedError,
    NotEnoughQuantityAvailableError,
    UnknownSkuError, OutOfStockError,
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
    def allocated_order_lines(self) -> List[OrderLine]:
        return self._allocated_order_lines

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
            raise UnknownSkuError()

        if order_line in self._allocated_order_lines:
            raise OrderLineAlreadyAllocatedError()

        if self.available_quantity < order_line.quantity:
            raise NotEnoughQuantityAvailableError()

        self._allocated_order_lines.append(order_line)


class Product:

    def __init__(self, sku: str, batches: Iterable[Batch] = (), evts: Iterable[events.Event] = ()):
        self.sku = sku
        self._batches = list(batches)
        self._events = list(evts)

    @property
    def events(self) -> Iterable[Event]:
        return self._events

    @events.setter
    def events(self, evts: Iterable[Event]):
        self._events = evts

    @property
    def batches(self) -> Iterable[Batch]:
        return self._batches

    @batches.setter
    def batches(self, batches: Iterable[Batch]):
        self._batches = batches

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
