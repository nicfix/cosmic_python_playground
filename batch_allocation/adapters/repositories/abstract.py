import abc

from batch_allocation.domain.model import OrderLine, Batch


class OrderLineAbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, order_reference: str) -> [OrderLine]:
        raise NotImplementedError()

    @abc.abstractmethod
    def add(self, order_line: OrderLine):
        raise NotImplementedError()


class BatchAbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, reference: str) -> Batch:
        raise NotImplementedError()

    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError()
