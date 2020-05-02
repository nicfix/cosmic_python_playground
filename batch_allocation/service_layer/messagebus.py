# Import the email modules we'll need
from batch_allocation.domain.events import Event, OutOfStock, AllocationRequired
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
    AllocationRequired: [services.allocate_handler]
}


def handle(event: Event, uow: AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow))
            queue.extend(uow.collect_new_events())
    return results
