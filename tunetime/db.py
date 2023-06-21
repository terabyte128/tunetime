from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session

from tunetime.settings import SETTINGS

engine = create_engine(SETTINGS.db_connection)


class make_session:
    def __init__(self):
        self.session = Session(engine)

    def __enter__(self):
        return self.session

    def __exit__(self, *_):
        self.session.close()
