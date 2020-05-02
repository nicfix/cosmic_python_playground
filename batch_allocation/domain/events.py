from dataclasses import dataclass
from datetime import date
from typing import Optional


class Event:
    pass


@dataclass
class OutOfStock(Event):
    sku: str


@dataclass
class BatchCreated(Event):
    ref: str
    sky: str
    qty: int
    eta: Optional[date] = None


@dataclass
class AllocationRequired(Event):
    order_ref: str
    sku: str
    qty: int
