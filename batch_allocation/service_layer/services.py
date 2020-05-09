from batch_allocation.domain.events import AllocationRequired, BatchCreated, BatchQuantityChanged
from batch_allocation.domain.exceptions import OrderLineAlreadyAllocatedError, OutOfStockError, UnknownSkuError, \
    UnknownRefError
from batch_allocation.domain.model import OrderLine, Batch, Product
from batch_allocation.service_layer.unit_of_work.abstract import AbstractUnitOfWork


class UnknownRef(Exception):
    pass


class UnknownSku(Exception):
    pass


class OutOfStock(Exception):
    pass


class OrderLineAlreadyAllocatedConflict(Exception):
    pass


def change_batch_quantity(event: BatchQuantityChanged,
                          uow: AbstractUnitOfWork) -> int:
    sku = event.sku
    ref = event.ref
    new_quantity = event.qty

    with uow:
        try:
            product = uow.products.get(sku)
        except UnknownSkuError:
            raise UnknownSku()

        try:
            return product.change_batch_quantity(ref, new_quantity)
        except UnknownRefError():
            raise UnknownRef()


def add_batch(event: BatchCreated,
              uow: AbstractUnitOfWork) -> str:
    ref = event.ref
    sku = event.sku
    quantity = event.qty
    eta = event.eta

    new_batch = Batch(
        ref=ref,
        sku=sku,
        purchased_quantity=quantity,
        eta=eta
    )

    with uow:
        try:
            product = uow.products.get(sku)
        except UnknownSkuError:
            product = Product(sku=sku)
            uow.products.add(product)

        product.batches.append(new_batch)

    return new_batch.ref


def allocate(event: AllocationRequired,
             uow: AbstractUnitOfWork) -> str:
    """
    Allocates an order_line given the batches already stored on database.
    :param event: AllocationRequired, the event received from the messagebus
    :param uow: AbstractUnitOfWork, the Unit Of Work
    :raises: OrderLineAlreadyAllocatedError, in case the order line was already allocated to a batch
    :raises: OutOfStockError, in case no batch can satisfy the request
    :raises: UnknownSku, in case there's no batch with the same sku of the order line
    :return: Batch, the batch that the order was allocated to
    """
    order_ref = event.order_ref
    sku = event.sku
    quantity = event.qty

    order_line = OrderLine(
        order_ref=order_ref,
        sku=sku,
        quantity=quantity,
    )

    with uow:

        try:
            product = uow.products.get(sku)
        except UnknownSkuError:
            raise UnknownSku()

        batches = product.batches

        if len(batches) == 0:
            raise OutOfStock()

        try:
            allocated_batch = product.allocate(order_line)
        except OrderLineAlreadyAllocatedError:
            raise OrderLineAlreadyAllocatedConflict()
        except OutOfStockError:
            raise OutOfStock()

        batchref = allocated_batch.ref

    return batchref
