from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from settings import env

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{env.DB_USERNAME}:{env.DB_USER_PASSWORD}@" \
                          f"{env.DB_HOSTNAME}:{env.DB_PORT}/{env.DB_NAME}"


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=False)
AsyncLocalSession = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()
