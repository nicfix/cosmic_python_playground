from batch_allocation.adapters.repositories.abstract import BatchAbstractRepository
from batch_allocation.domain.model import OrderLine


def allocate(order_line: OrderLine, batch_repository: BatchAbstractRepository) -> None:
    """
    Allocates an order_line given the batches already stored on database.

    :param order_line: OrderLine, the line that we want to allocate
    :param batch_repository: BatchAbstractRepository, the Batches repository
    :param session: Session, a session for the ORM (this can be improved)
    :return:
    """
    pass
