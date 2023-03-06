import asyncio
import datetime
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Event

from loguru import logger

from db.config import engine
from logs.handlers.redis_handler import RedisHandler
from processes import log_server, db_server, parser_process
from src.parser import get_num_pages
from src.redis import RedisCli, ParsingTask
from src.utils import split_urls
from schemas.statistics_schema import Statistics
from db.dals.statistics_dal import StatisticsDAL


class RlicParserApp:
    NUM_WORKERS = os.cpu_count()
    logs_rq = "logging_queue"  # Name of the Redis list that will store logs
    db_rq = "db_cards_queue"  # Name of the Redis list that will store parsed cards

    def __init__(self):
        self.stop_log_server = Event()
        self.log_server = log_server.RedisLogServer(event=self.stop_log_server, rq_name=self.logs_rq)
        self.stop_db_server = Event()
        self.db_server = db_server.DBServer(engine=engine, event=self.stop_db_server, rq_name=self.db_rq)
        self.redis_client = RedisCli()

    def configure_logger(self, log_format: str = None):
        """Change loguru's default log format and adds RedisHandler for sending log records to Redis queue."""

        logger.remove()
        if log_format is None:
            log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSSSS}</green> | <level>{level: <8}</level> | " \
                         "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        logger.add(sys.stdout, format=log_format)

        logger.add(RedisHandler(), format=log_format)

    def clear_redis(self):
        """Delete Redis variables that were using."""
        self.redis_client.delete(self.db_rq)
        self.redis_client.delete(self.logs_rq)

    @classmethod
    def worker(cls, worker_id: int, urls: list):
        logger.info(f"Started worker {worker_id}, PID: {os.getpid()}")
        parser = parser_process.ParserProcess(urls=urls, worker_id=worker_id)
        asyncio.run(parser.run())
        logger.info(f"Done worker {worker_id}, PID: {os.getpid()}")

    def run(self) -> None:
        num_pages, num_licenses = (asyncio.run(get_num_pages())).values()
        logger.info(f"Counted {num_pages} pages, {num_licenses} licenses.")
        parsing_task.set_value('num_results', num_licenses)
        parsing_task.set_value('num_results', num_licenses)

        urls = [f'https://islod.obrnadzor.gov.ru/rlic/search/?page={i}' for i in range(1, num_pages + 1)]

        urls_chunks = split_urls(urls, self.NUM_WORKERS)

        # Create workers
        with ProcessPoolExecutor(max_workers=self.NUM_WORKERS) as executor:
            for i in range(self.NUM_WORKERS):
                try:
                    executor.submit(self.worker, worker_id=i+1, urls=urls_chunks[i])

                except Exception as e:
                    logger.error(e)


if __name__ == "__main__":
    app = RlicParserApp()
    app.configure_logger()
    app.log_server.start()
    parsing_task = ParsingTask(app.redis_client)

    while True:
        if parsing_task.get_value('status') == 'active':
            try:
                app.db_server.start()
                logger.info(f"Main Process PID: {os.getpid()}")

                parsing_task.set_value('status', 'in_progress')
                parsing_task.set_value('started', str(datetime.datetime.utcnow()))
                parsing_task.set_value('ended', '')

                app.run()

                app.stop_db_server.set()
                app.db_server.join()
                app.stop_log_server.set()
                app.log_server.join()
                app.clear_redis()

                parsing_task.set_value('status', 'done')
            except Exception as e:
                app.redis_client.hset('parsing_task', 'status', 'failed')
                app.redis_client.hset('parsing_task', 'details', e)
            finally:
                parsing_task.set_value('ended', str(datetime.datetime.utcnow()))

                # Insert to statistics table
                finished_task = parsing_task.get_hash()
                finished_task['table'] = 'active_licenses'
                statistics = StatisticsDAL()
                print(finished_task)
                print(Statistics(**finished_task))
                asyncio.run(statistics.create(Statistics(**finished_task)))

        else:
            # Waiting for active task
            time.sleep(1)
