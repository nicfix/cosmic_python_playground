class BatchAllocationError(Exception):
    pass


class OrderLineAlreadyAllocatedError(BatchAllocationError):
    pass


class NotEnoughQuantityAvailableError(BatchAllocationError):
    pass


class WrongSkuError(BatchAllocationError):
    pass