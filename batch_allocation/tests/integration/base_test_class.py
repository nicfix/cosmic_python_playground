from unittest import TestCase

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from batch_allocation.tests.integration.fixtures import set_up_testing_db, tear_down_testing_db


class BaseSessionTestCase(TestCase):
    session: Session
    engine: Engine

    @classmethod
    def setUpClass(cls) -> None:
        cls.engine, cls.session = set_up_testing_db()

    @classmethod
    def tearDownClass(cls) -> None:
        tear_down_testing_db(cls.session, cls.engine)

    @classmethod
    def get_session(cls):
        return cls.session

    @classmethod
    def get_engine(cls):
        return cls.engine
