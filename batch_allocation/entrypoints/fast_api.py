from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from batch_allocation.service_layer import services
from batch_allocation.service_layer.unit_of_work.sql_alchemy import SqlAlchemyUnitOfWork

app = FastAPI()


class OrderLineDTO(BaseModel):
    order_ref: str
    sku: str
    quantity: int


class BatchRefResponse(BaseModel):
    batchref: str


@app.post("/allocate", status_code=201)
def allocate_endpoint(order_line_dto: OrderLineDTO):
    uow = SqlAlchemyUnitOfWork()
    try:
        batchref = services.allocate(
            order_ref=order_line_dto.order_ref,
            sku=order_line_dto.sku,
            quantity=order_line_dto.quantity,
            uow=uow
        )
    except services.OutOfStock:
        raise HTTPException(status_code=400, detail="Out of stock")

    return BatchRefResponse(batchref=batchref)
