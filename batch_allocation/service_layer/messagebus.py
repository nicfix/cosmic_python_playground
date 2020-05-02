# Import the email modules we'll need

from batch_allocation.domain.events import Event, OutOfStock


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
}


def handle(event: Event):
    for handler in HANDLERS[type(event)]:
        handler(event)
