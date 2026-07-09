from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from .config import settings


engine = create_engine(settings.database_url)

class Base(DeclarativeBase):
    "ORM Wrapper"


def init_db():
    from . import models

    Base.metadata.create_all(bind=engine)
