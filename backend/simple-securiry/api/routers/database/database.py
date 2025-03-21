from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base

DATABASE_URL: str = "sqlite:///database.db"
engine: Engine = create_engine(url=DATABASE_URL)

Base = declarative_base()


def init_database():
    Base.metadata.create_all(bind=engine)


def get_session():
    with Session(bind=engine) as session:
        yield session
