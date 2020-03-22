from batch_allocation.adapters.repositories.abstract import BatchAbstractRepository
from batch_allocation.domain.exceptions import OrderLineAlreadyAllocatedError
from batch_allocation.domain.model import OrderLine, Batch
from batch_allocation.domain import service_functions
from batch_allocation.domain.service_functions import OutOfStockError


class UnknownSku(Exception):
    pass


class OutOfStock(Exception):
    pass


class OrderLineAlreadyAllocatedConflict(Exception):
    pass


def allocate(order_line: OrderLine, batch_repository: BatchAbstractRepository) -> Batch:
    """
    Allocates an order_line given the batches already stored on database.
    :param order_line: OrderLine, the line that we want to allocate
    :param batch_repository: BatchAbstractRepository, the Batches repository
    :raises: OrderLineAlreadyAllocatedError, in case the order line was already allocated to a batch
    :raises: OutOfStockError, in case no batch can satisfy the request
    :raises: UnknownSku, in case there's no batch with the same sku of the order line
    :return: Batch, the batch that the order was allocated to
    """

    batches = batch_repository.get_by_sku(order_line.sku)

    if len(batches) == 0:
        raise UnknownSku()

    try:
        allocated_batch = service_functions.allocate_single_order_line(
            batches, order_line
        )
    except OrderLineAlreadyAllocatedError:
        raise OrderLineAlreadyAllocatedConflict()
    except OutOfStockError:
        raise OutOfStock()

    batch_repository.update(batch=allocated_batch)

    return allocated_batch
