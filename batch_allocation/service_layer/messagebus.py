# Import the email modules we'll need
import logging
from typing import Union

from batch_allocation.domain import commands, events
from batch_allocation.domain.commands import CreateBatch, Allocate, ChangeBatchQuantity
from batch_allocation.domain.events import OutOfStock
from batch_allocation.service_layer import services
from batch_allocation.service_layer.unit_of_work.abstract import AbstractUnitOfWork

logger = logging.getLogger(__file__)


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
    pass


EVENTS_HANDLERS = {
    OutOfStock: [send_out_of_stock_notification]
}

COMMANDS_HANDLERS = {
    Allocate: [services.allocate],
    CreateBatch: [services.add_batch],
    ChangeBatchQuantity: [services.change_batch_quantity]
}

Message = Union[events.Event, commands.Command]


def handle_event(event: events.Event, uow: AbstractUnitOfWork):
    try:
        for handler in EVENTS_HANDLERS[type(event)]:
            handler(event, uow)
    except Exception as e:
        logger.exception('Exception handling command %s: %s' % (event, e))
        pass


def handle_command(command: commands.Command, uow: AbstractUnitOfWork):
    results = []
    try:
        for handler in COMMANDS_HANDLERS[type(command)]:
            results.append(handler(command, uow))
        return results
    except Exception as e:
        logger.exception('Exception handling command %s: %s' % (command, e))
        raise e


def handle(message: Message, uow: AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, uow)
        elif isinstance(message, commands.Command):
            results.extend(handle_command(message, uow))
        else:
            raise Exception(f'{message} was not an Event or Command')
        queue.extend(uow.collect_new_events())
    return results
