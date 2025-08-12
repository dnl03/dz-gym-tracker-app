from sqlmodel import SQLModel, Session, create_engine

from core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_all():
    pass
    # with engine.begin() as conn:
    #     # najpierw tabela
    #     conn.exec_driver_sql('DROP TABLE IF EXISTS users CASCADE;')
    #     # potem typ ENUM
    #     conn.exec_driver_sql('DROP TYPE IF EXISTS genderenum CASCADE;')
    # SQLModel.metadata.drop_all(engine)
    # SQLModel.metadata.create_all(engine)