from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from settings import env

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{env.DB_USERNAME}:{env.DB_USER_PASSWORD}@" \
                          f"{env.DB_HOSTNAME}:{env.DB_PORT}/{env.DB_NAME}"


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=False)
AsyncLocalSession = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


@asynccontextmanager
async def get_async_session():
    session = AsyncLocalSession()
    try:
        yield session
    except Exception as e:
        logger.error(e)
        await session.rollback()
    finally:
        await session.close()


def async_session(meth):
    async def method_wrapper(self, *args, **kwargs):
        async with get_async_session() as session:
            return await meth(self, session, *args, **kwargs)
    return method_wrapper


# @asynccontextmanager
# async def get_async_session():
#     try:
#         async_session = AsyncLocalSession
#
#         async with async_session() as session:
#             yield session
#     except Exception as e:
#         await session.rollback()
#         logger.error(e)
#     finally:
#         await session.close()
