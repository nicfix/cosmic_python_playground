from batch_allocation.adapters.repositories.abstract import BatchAbstractRepository
from batch_allocation.domain.model import OrderLine, Batch
from batch_allocation.domain import service_functions


def allocate(order_line: OrderLine, batch_repository: BatchAbstractRepository) -> Batch:
    """
    Allocates an order_line given the batches already stored on database.

    :param order_line: OrderLine, the line that we want to allocate
    :param batch_repository: BatchAbstractRepository, the Batches repository
    :param session: Session, a session for the ORM (this can be improved)
    :return:
    """

    batches = batch_repository.get_by_sku(order_line.sku)

    allocated_batch = service_functions.allocate_single_order_line(batches, order_line)

    batch_repository.update(batch=allocated_batch)

    return allocated_batch
