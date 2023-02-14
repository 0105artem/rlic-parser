import asyncio
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Event

import redis
from loguru import logger

from db.config import engine
from logs.handlers.redis_handler import RedisHandler
from processes import log_server, db_server, parser_process
from settings import env
from src.parser import get_num_pages
from src.utils import split_urls


class RlicParserApp:
    NUM_WORKERS = os.cpu_count()
    redis_pool = redis.ConnectionPool(host=env.REDIS_HOST, port=env.REDIS_PORT, db=env.REDIS_DB)

    def __init__(self):
        self.logs_redis_q = "logging_queue"  # Name of the Redis list that will store logs
        self.stop_log_server = Event()
        self.log_server = log_server.RedisLogServer(redis_pool=self.redis_pool, event=self.stop_log_server,
                                                    queue_name=self.logs_redis_q)

        self.db_redis_q = "db_cards_queue"  # Name of the Redis list that will store parsed cards
        self.stop_db_server = Event()
        self.db_server = db_server.DBServer(engine=engine, event=self.stop_db_server, redis_pool=self.redis_pool,
                                            queue_name=self.db_redis_q)

    def configure_logger(self, log_format: str = None):
        """Change loguru's default log format and adds RedisHandler for sending log records to Redis queue."""

        logger.remove()
        if log_format is None:
            log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSSSS}</green> | <level>{level: <8}</level> | " \
                         "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        logger.add(sys.stdout, format=log_format)

        logger.add(RedisHandler(self.redis_pool), format=log_format)

    def clear_redis(self):
        """Delete Redis variables that were using."""
        redis_client = redis.Redis(connection_pool=self.redis_pool)
        redis_client.delete(self.db_redis_q)
        redis_client.delete(self.logs_redis_q)

    @classmethod
    def worker(cls, worker_id: int, urls: list):
        logger.info(f"Started worker {worker_id}, PID: {os.getpid()}")
        parser = parser_process.ParserProcess(redis_pool=cls.redis_pool, urls=urls,
                                              worker_id=worker_id)
        asyncio.run(parser.run())
        logger.info(f"Done worker {worker_id}, PID: {os.getpid()}")

    def run(self) -> None:
        num_pages = asyncio.run(get_num_pages())
        logger.info(f"Counted {num_pages} pages")

        urls = [f'https://islod.obrnadzor.gov.ru/rlic/search/?page={i}' for i in range(1, num_pages + 1)]

        urls_chunks = split_urls(urls, self.NUM_WORKERS)

        # Create workers
        with ProcessPoolExecutor(max_workers=self.NUM_WORKERS) as executor:
            for i in range(self.NUM_WORKERS):
                try:
                    executor.submit(self.worker, worker_id=i+1, urls=urls_chunks[i])

                except Exception as e:
                    print(e)


if __name__ == "__main__":
    app = RlicParserApp()
    app.configure_logger()
    app.log_server.start()
    app.db_server.start()

    logger.info(f"Main Process PID: {os.getpid()}")
    app.run()

    app.stop_db_server.set()
    app.db_server.join()
    app.stop_log_server.set()
    app.log_server.join()

    app.clear_redis()
