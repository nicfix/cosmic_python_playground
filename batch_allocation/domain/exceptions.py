class BatchAllocationError(Exception):
    pass


class OrderLineAlreadyAllocatedError(BatchAllocationError):
    pass


class NotEnoughQuantityAvailableError(BatchAllocationError):
    pass


class WrongSkuError(BatchAllocationError):
    pass


class SkuNotAvailableError(BatchAllocationError):
    pass


class OutOfStockError(BatchAllocationError):
    pass