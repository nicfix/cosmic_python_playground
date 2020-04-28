def create_product(sku, batch_ref, quantity, session):
    session.execute(
        f"INSERT INTO products (sku) "
        f"VALUES ('{sku}')"
    )

    session.execute(
        f"INSERT INTO batches (ref, sku, _purchased_quantity, eta) "
        f"VALUES ('{batch_ref}', '{sku}', {quantity}, '2020-10-10')"
    )

    session.commit()


def cleanup_product(sku, batch_ref, order_ref, session):
    session.execute(
        f"DELETE FROM order_lines WHERE order_ref = '{order_ref}'"
    )

    session.execute(
        f"DELETE FROM batches WHERE ref = '{batch_ref}'"
    )

    session.execute(
        f"DELETE FROM products WHERE sku = '{sku}'"
    )

    session.commit()
