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


class ProductSQLAlchemyRepository(AbstractProductRepository, SQLAlchemyRepository):

    def get(self, sku: str) -> Product:
        product = self.session.query(Product).get(sku)

        if product is None:
            raise UnknownSkuError()

        return product

    def add(self, product: Product):
        self.session.add(product)
        self.session.commit()
