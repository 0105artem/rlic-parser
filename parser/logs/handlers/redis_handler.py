import logging

from src.redis import RedisCli


class RedisHandler(logging.Handler):
    def __init__(self, rq_name: str = "logging_queue") -> None:
        """
        :param rq_name: Name of the list that will be created in Redis and storing logs.
        """
        logging.Handler.__init__(self)
        self.rq_name = rq_name
        self.redis_client = RedisCli()

    def emit(self, record) -> None:
        """Emit a log message on redis queue."""
        try:
            bmsg = self.format(record).encode("utf8")
        except Exception:
            self.handleError(record)
            return

        self.redis_client.lpush(self.rq_name, bmsg)
