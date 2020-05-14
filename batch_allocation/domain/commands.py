from dataclasses import dataclass
from datetime import date
from typing import Optional

from batch_allocation.domain.events import Event


class Command(Event):
    pass


@dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None


@dataclass
class Allocate(Command):
    order_ref: str
    sku: str
    qty: int


@dataclass
class ChangeBatchQuantity(Command):
    ref: str
    sku: str
    qty: int
