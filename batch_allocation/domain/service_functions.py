from batch_allocation.domain.model import Batch, OrderLine
from batch_allocation.domain.exceptions import BatchAllocationError, OrderLineAlreadyAllocatedError, \
    NotEnoughQuantityAvailableError


class SkuNotAvailableError(BatchAllocationError):
    pass


class OutOfStockError(BatchAllocationError):
    pass


def allocate(batches: [Batch], order_lines: [OrderLine]) -> None:
    batches_sku_map = {}

    for batch in batches:
        batches_sku_map.setdefault(batch.sku, []).append(batch)

    for order_line in order_lines:
        sku = order_line.sku

        if sku not in batches_sku_map:
            raise SkuNotAvailableError()

        allocated = False

        for batch in batches_sku_map.get(sku):
            try:
                batch.allocate(order_line=order_line)
                allocated = True
            except OrderLineAlreadyAllocatedError as e:
                raise e
            except NotEnoughQuantityAvailableError:
                pass

        if not allocated:
            raise OutOfStockError()
