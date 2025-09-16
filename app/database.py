from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOSTNAME = os.getenv('POSTGRES_HOSTNAME')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
APP_ENV = os.getenv("APP_ENV", "production")

engine = create_engine(DATABASE_URL, echo=(APP_ENV == "development"))

def get_session(engine=engine):
    """Yield a session for FastAPI dependency injection."""
    def _get_session():
        with Session(engine) as session:
            yield session
    return _get_session

def create_db_and_tables(engine=engine):
    SQLModel.metadata.create_all(engine)