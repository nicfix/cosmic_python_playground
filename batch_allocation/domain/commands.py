from dataclasses import dataclass
from datetime import date
from typing import Optional


class Command:
    pass


@dataclass
class BatchCreated(Command):
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None


@dataclass
class AllocationRequired(Command):
    order_ref: str
    sku: str
    qty: int


@dataclass
class BatchQuantityChanged(Command):
    ref: str
    sku: str
    qty: int
