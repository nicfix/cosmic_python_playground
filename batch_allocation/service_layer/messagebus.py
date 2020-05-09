# Import the email modules we'll need
from typing import Union

from batch_allocation.domain import commands, events
from batch_allocation.domain.commands import BatchCreated, AllocationRequired, BatchQuantityChanged
from batch_allocation.domain.events import Event, OutOfStock
from batch_allocation.service_layer import services
from batch_allocation.service_layer.unit_of_work.abstract import AbstractUnitOfWork


def send_out_of_stock_notification(event: OutOfStock):
    """
    msg = EmailMessage()
    msg.set_content(f'Out of stock for {event.sku}')
    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = f'Out of stock for {event.sku}'
    msg['From'] = 'n.sacco.88@gmail.com'
    msg['To'] = 'n.sacco.88@gmail.com'

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    """

    return event


HANDLERS = {
    OutOfStock: [send_out_of_stock_notification],
    AllocationRequired: [services.allocate],
    BatchCreated: [services.add_batch],
    BatchQuantityChanged: [services.change_batch_quantity]
}


Message = Union[events.Event, commands.Command]


def handle(message: Message, uow: AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        for handler in HANDLERS[type(message)]:
            results.append(handler(message, uow))
            queue.extend(uow.collect_new_events())
    return results
