from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from batch_allocation.adapters.repositories.sql_alchemy import SQLAlchemyRepository
from batch_allocation.adapters.repositories.tracking import TrackingRepository
from batch_allocation.service_layer import config, messagebus
from batch_allocation.service_layer.unit_of_work.abstract import AbstractUnitOfWork

engine = create_engine(
    config.get_db_uri(),
    connect_args={"check_same_thread": False}
)

DEFAULT_SESSION_FACTORY = sessionmaker(bind=engine, autocommit=False, autoflush=False, )


class UnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY, message_bus=messagebus):
        self.session_factory = session_factory
        self.message_bus = message_bus

    def __enter__(self):
        self.session = self.session_factory()
        self.products = TrackingRepository(delegate=SQLAlchemyRepository(self.session))
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def collect_new_events(self):
        for product in self.products.seen:
            while product.events:
                yield product.events.pop(0)

    def commit(self):
        self.session.commit()

    def rollback(self):  # (4)
        self.session.rollback()
