from sqlalchemy.orm import Session

from batch_allocation.adapters.repositories.abstract import (
    OrderLineAbstractRepository,
    BatchAbstractRepository, AbstractProductRepository,
)
from batch_allocation.domain.exceptions import UnknownSkuError
from batch_allocation.domain.model import OrderLine, Batch, Product


class SQLAlchemyRepository(object):
    session: Session

    def __init__(self, session: Session):
        self.session = session


class OrderLineSQLAlchemyRepository(OrderLineAbstractRepository, SQLAlchemyRepository):
    def get(self, order_reference: str) -> [OrderLine]:
        return list(self.session.query(OrderLine).filter_by(order_ref=order_reference))

    def add(self, order_line: OrderLine):
        self.session.add(order_line)
        self.session.commit()


class BatchSQLAlchemyRepository(BatchAbstractRepository, SQLAlchemyRepository):
    def update(self, batch: Batch):
        self.add(batch)

    def get_by_sku(self, sku: str) -> [Batch]:
        return list(self.session.query(Batch).filter_by(sku=sku))

    def get(self, reference: str) -> Batch:
        return self.session.query(Batch).filter_by(ref=reference).one()

    def add(self, batch: Batch):
        self.session.add(batch)
        self.session.commit()


class ProductSQLAlchemyRepository(AbstractProductRepository, BatchSQLAlchemyRepository):

    def get(self, sku: str) -> Product:
        product = self.session.query(Product).get(sku)

        if product is None:
            raise UnknownSkuError()

        return product

    def add(self, product: Product):
        self.session.add(product)
        self.session.commit()
