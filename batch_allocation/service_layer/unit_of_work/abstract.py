import abc

from batch_allocation.adapters.repositories.abstract import BatchAbstractRepository


class AbstractUnitOfWork(abc.ABC):
    batches: BatchAbstractRepository

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):  # (3)
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):  # (4)
        raise NotImplementedError
