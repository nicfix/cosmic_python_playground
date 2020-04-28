from sqlalchemy import MetaData, Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import mapper, relationship

from batch_allocation.domain.model import OrderLine, Batch, Product

metadata = MetaData()

order_lines = Table(  # (2)
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("quantity", Integer, nullable=False),
    Column("order_ref", String(255)),
    Column("allocated_batch_ref", String(255), ForeignKey("batches.ref")),
)

batches = Table(
    "batches",
    metadata,
    Column("ref", String(255), primary_key=True),
    Column("sku", String(255), ForeignKey("products.sku")),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date()),
)

products = Table(
    "products",
    metadata,
    Column("sku", String(255), primary_key=True),
)


def create_tables(engine):
    metadata.create_all(engine)


def drop_tables(engine):
    metadata.drop_all(engine)


def start_mappers():
    mapper(OrderLine, order_lines)
    mapper(
        Batch,
        batches,
        properties={
            "_allocated_order_lines": relationship(
                OrderLine,
                primaryjoin=batches.c.ref == order_lines.c.allocated_batch_ref,
            )
        },
    )
    mapper(
        Product,
        products,
        properties={
            "_batches": relationship(
                Batch,
                primaryjoin=products.c.sku == batches.c.sku,
            )
        },
    )


start_mappers()
