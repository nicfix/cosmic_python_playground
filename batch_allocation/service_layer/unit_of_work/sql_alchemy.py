from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from batch_allocation.adapters.repositories.sql_alchemy import BatchSQLAlchemyRepository
from batch_allocation.service_layer import config
from batch_allocation.service_layer.unit_of_work.abstract import AbstractUnitOfWork

engine = create_engine(
    config.get_db_uri(),
    connect_args={"check_same_thread": False}
)

DEFAULT_SESSION_FACTORY = sessionmaker(bind=engine, autocommit=False, autoflush=False, )


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.batches = BatchSQLAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):  # (4)
        self.session.rollback()
