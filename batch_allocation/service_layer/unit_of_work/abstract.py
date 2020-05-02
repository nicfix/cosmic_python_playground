import abc

from batch_allocation.adapters.repositories.abstract import AbstractRepository


class AbstractUnitOfWork(abc.ABC):
    products = AbstractRepository

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def collect_new_events(self):
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self):  # (3)
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):  # (4)
        raise NotImplementedError
