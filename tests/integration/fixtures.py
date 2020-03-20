from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from batch_allocation.orm.orm import create_tables, drop_tables


def set_up_testing_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    create_tables(engine)
    session = Session(engine)
    return engine, session


def tear_down_testing_db(session, engine):
    session.close()
    drop_tables(engine)
