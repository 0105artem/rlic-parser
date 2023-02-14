import asyncio
import multiprocessing as mp
import os
from ast import literal_eval
from typing import List

import redis
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Session

from db.config import async_session, Base
from db.dals import card_dal
from schemas.card_schema import Card


class DBServer(mp.Process):
    """Interacts with Postgres database and Redis until the event is set."""

    def __init__(self, redis_pool: redis.ConnectionPool, event: mp.Event, engine: AsyncEngine,
                 queue_name: str = "db_cards_queue", chunk_size: int = 10) -> None:
        """
        :param engine: SQLAlchemy AsyncEngine instance.
        :param event: Flag when to stop interact with db.
        :param queue_name: Name of the Redis list that will store parsed cards which will be inserted into DB.
        :param chunk_size: How many rows insert into db at once.
        """
        super(DBServer, self).__init__()

        self.event = event
        self.queue_name = queue_name
        self.chunk_size = chunk_size

        if isinstance(redis_pool, redis.ConnectionPool):
            self.redis_client = redis.Redis(connection_pool=redis_pool)
        if isinstance(engine, AsyncEngine):
            self.engine = engine

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_cards(self) -> List[dict]:
        """
        Pops N cards from the redis queue and formats them into dicts.
        N = self.chunk_size or less if queue length < self.chunk_size.
        """
        n_inserts = min(self.chunk_size, self.redis_client.llen(self.queue_name))
        cards = [literal_eval(self.redis_client.rpop(self.queue_name).decode('utf8', 'strict'))
                 for _ in range(n_inserts)]
        return cards

    @async_session
    async def insert_cards(self, session, cards: List[dict]) -> None:
        """Inserts pack of cards into the database."""
        CardDAL = card_dal.CardDAL(session)
        await CardDAL.create_cards([Card(**card) for card in cards])

    async def coroutine(self, pause: float = 5) -> None:
        """
        Interacts with the database until the event is set. Interactions like: inserting cards, etc.
        :param pause: How long to sleep if redis queue empty.
        """

        await self.drop_tables()
        await self.create_tables()

        while not self.event.is_set():
            if self.redis_client.llen(self.queue_name):
                cards = await self.get_cards()
                await self.insert_cards(cards)
            else:
                await asyncio.sleep(pause)
        else:
            # Sometimes happens that event is set but redis queue is still not empty.
            # In that case need to add the rest cards from the queue into the db.
            while self.redis_client.llen(self.queue_name):
                cards = await self.get_cards()
                await self.insert_cards(cards)
            await self.engine.dispose()

    def run(self) -> None:
        try:
            logger.info(f"Starting Process for working with the DataBase. PID: {os.getpid()}")
            asyncio.run(self.coroutine())
        finally:
            logger.info(f"Stopping Process for working with the DataBase. PID: {os.getpid()}")
            self.redis_client.delete(self.queue_name)
