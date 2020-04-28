from batch_allocation.domain import service_functions
from batch_allocation.domain.exceptions import OrderLineAlreadyAllocatedError, OutOfStockError, UnknownSkuError
from batch_allocation.domain.model import OrderLine
from batch_allocation.service_layer.unit_of_work.abstract import AbstractBatchesUnitOfWork, AbstractUnitOfWork


class UnknownSku(Exception):
    pass


class OutOfStock(Exception):
    pass


class OrderLineAlreadyAllocatedConflict(Exception):
    pass


def allocate(order_ref: str, sku: str, quantity: int, uow: AbstractUnitOfWork) -> str:
    """
    Allocates an order_line given the batches already stored on database.
    :param order_ref: str, the line that we want to allocate
    :param sku: str, the product's sku
    :param quantity: int, the desired quantity
    :param uow: AbstractUnitOfWork, the Unit Of Work
    :raises: OrderLineAlreadyAllocatedError, in case the order line was already allocated to a batch
    :raises: OutOfStockError, in case no batch can satisfy the request
    :raises: UnknownSku, in case there's no batch with the same sku of the order line
    :return: Batch, the batch that the order was allocated to
    """

    order_line = OrderLine(
        order_ref=order_ref,
        sku=sku,
        quantity=quantity,
    )

    with uow:

        try:
            product = uow.products.get(order_line.sku)
        except UnknownSkuError:
            raise UnknownSku()

        batches = product.batches

        if len(batches) == 0:
            raise OutOfStock()

        try:
            allocated_batch = service_functions.allocate_single_order_line(
                batches, order_line
            )
        except OrderLineAlreadyAllocatedError:
            raise OrderLineAlreadyAllocatedConflict()
        except OutOfStockError:

            raise OutOfStock()

        # uow.batches.update(batch=allocated_batch)

        batchref = allocated_batch.ref

    return batchref
