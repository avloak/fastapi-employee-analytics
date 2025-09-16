import app.database as app_db
from fastapi import FastAPI
from app.routes import upload, stats
from app.utils import upsert_postgres, stats_postgres
from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

def create_app(engine_override=None, stats_function=None, upsert_function=None) -> FastAPI:
    # Decide which engine to use
    engine = engine_override or app_db.engine

    @asynccontextmanager
    async def lifespan(app):
        app_db.create_db_and_tables(engine)
        yield
    
    app = FastAPI(lifespan=lifespan)

    # Include routers
    app.include_router(stats.router, prefix="/stats", tags=["stats"])
    app.include_router(upload.router, prefix="/upload", tags=["upload"])

    # Utils (default: Postgres, can override with SQLite in tests)
    app.state.sessionmaker = sessionmaker(
        bind=engine, class_=Session, expire_on_commit=False
    )
    app.state.stats_function = stats_function or stats_postgres
    utils_module = upsert_function or upsert_postgres
    app.state.upsert_dataframe = lambda df, model, **kw: utils_module.upsert_dataframe(
        df, model, engine=engine, **kw
    )

    return app

app = create_app()

@app.get("/")
def root():
    return {"message": "Employee Analytics API is running"}