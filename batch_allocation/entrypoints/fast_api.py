from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from batch_allocation.domain.events import AllocationRequired
from batch_allocation.service_layer import services, messagebus
from batch_allocation.service_layer.unit_of_work.sql_alchemy import UnitOfWork

app = FastAPI()


class OrderLineDTO(BaseModel):
    order_ref: str
    sku: str
    quantity: int


class BatchRefResponse(BaseModel):
    batchref: str


@app.post("/allocate", status_code=201)
def allocate_endpoint(order_line_dto: OrderLineDTO):
    uow = UnitOfWork()
    event = AllocationRequired(
        order_ref=order_line_dto.order_ref,
        sku=order_line_dto.sku,
        qty=order_line_dto.quantity
    )

    try:
        results = messagebus.handle(event, uow)
        return BatchRefResponse(batchref=results.pop(0))
    except services.OutOfStock:
        raise HTTPException(status_code=400, detail="Out of stock")
