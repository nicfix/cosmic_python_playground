from batch_allocation.domain.exceptions import BatchAllocationError, OrderLineAlreadyAllocatedError, \
    NotEnoughQuantityAvailableError, WrongSkuError
from batch_allocation.domain.model import Batch, OrderLine


class SkuNotAvailableError(BatchAllocationError):
    pass


class OutOfStockError(BatchAllocationError):
    pass


def allocate(batches: [Batch], order_lines: [OrderLine]) -> None:
    """
    :param batches:
    :param order_lines:
    :raises: OrderLineAlreadyAllocatedError
    :raises: OutOfStockError
    """
    batches_sku_map = {}

    for batch in batches:
        batches_sku_map.setdefault(batch.sku, []).append(batch)

    for order_line in order_lines:
        sku = order_line.sku

        if sku not in batches_sku_map:
            raise SkuNotAvailableError()

        sku_batches = batches_sku_map.get(sku)

        allocate_single_order_line(sku_batches, order_line)


def allocate_single_order_line(batches: [Batch], order_line: OrderLine) -> Batch:
    """
    Given a list of batches allocates one order-line and returns the batch that the order line was allocated to
    :param batches: A list of batches
    :param order_line: OrderLine, an order line to allocate
    :raises: OrderLineAlreadyAllocatedError, if the order line was already allocated to one of the batches
    :raises: OutOfStockError, if no one of the batches was able to allocate the order line
    :return: Batch, the batch that the order line was allocated to.
    """
    for batch in batches:
        try:
            batch.allocate(order_line=order_line)
            return batch
        except OrderLineAlreadyAllocatedError as e:
            raise e
        except WrongSkuError:
            """
            One or more batches might have the wrong sku, we don't care, maybe one of the other ones will be
            compatible. We could filter it before.
            """
            pass
        except NotEnoughQuantityAvailableError:
            """
            One or more batches might have not enough quantity, we don't care, maybe one of the other ones will be
            compatible. We could filter it before.
            """
            pass

    raise OutOfStockError()
