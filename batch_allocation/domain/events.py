from dataclasses import dataclass


class Event:
    pass


@dataclass
class OrderAllocated(Event):
    sku: str
    batchref: str


@dataclass
class OutOfStock(Event):
    sku: str
