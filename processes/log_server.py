import multiprocessing as mp
import os
import time

import redis
from loguru import logger

from src.utils import current_date


class RedisLogServer(mp.Process):
    def __init__(self, redis_pool: redis.ConnectionPool, event: mp.Event,
                 output: str = f"./logs/log_files/{current_date()}.log",
                 queue_name: str = "logging_queue") -> None:
        """
        :param event: Flag when to stop LogServer.
        :param output: Where to save log files.
        :param queue_name: Name of the Redis list that will store logs.
        """
        super(RedisLogServer, self).__init__()

        self.event = event
        self.queue_name = queue_name
        self.output = output

        if isinstance(redis_pool, redis.ConnectionPool):
            self.redis_client = redis.Redis(connection_pool=redis_pool)

    def run(self, pause: float = 1.0):
        """
        :param pause: How long to sleep while the redis queue with logs empty to not overload Redis with RPOP requests.
        """
        try:
            logger.info(f"Starting Process for writing logs. PID: {os.getpid()}")
            while self.redis_client.llen(self.queue_name) or not self.event.is_set():
                log_record = self.redis_client.rpop(self.queue_name)
                if log_record:
                    log_record = log_record.decode('UTF-8')
                    if log_record[-2:] != '\n':
                        log_record = log_record + '\n'
                    with open(self.output, "a") as file:
                        file.write(log_record)
                else:
                    time.sleep(pause)
        finally:
            logger.info(f"Stopping Process for writing logs. PID: {os.getpid()}")
            self.redis_client.delete(self.queue_name)
