from typing import List

from pydantic import BaseModel

from batch_allocation.service_layer.unit_of_work.abstract import AbstractUnitOfWork


class Allocation(BaseModel):
    sku: str
    batchref: str


def get_allocations(sku: str, uow: AbstractUnitOfWork) -> List[Allocation]:
    with uow:
        results = list(uow.session.execute(
            'SELECT a.sku, b.ref'
            ' FROM order_lines AS a'
            ' JOIN batches AS b ON a.allocated_batch_ref = b.ref'
            ' WHERE a.sku = :sku',
            dict(sku=sku)
        ))
    return [Allocation(sku=sku, batchref=batchref) for sku, batchref in results]
