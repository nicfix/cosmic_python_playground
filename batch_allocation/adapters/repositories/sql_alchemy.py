from sqlalchemy.orm import Session

from batch_allocation.adapters.repositories.abstract import (
    AbstractRepository,
)
from batch_allocation.domain.exceptions import UnknownSkuError
from batch_allocation.domain.model import Product


class SQLAlchemyRepository(AbstractRepository):
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get(self, sku: str) -> Product:
        product = self.session.query(Product).get(sku)

        if product is None:
            raise UnknownSkuError()

        return product

    def add(self, product: Product):
        self.session.add(product)
        self.session.commit()
