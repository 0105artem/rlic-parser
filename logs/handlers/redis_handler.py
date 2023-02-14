import logging

import redis


class RedisHandler(logging.Handler):
    def __init__(self, redis_pool: redis.ConnectionPool, queue_name: str = "logging_queue") -> None:
        """
        :param redis_pool:
        :param queue_name: Name of the list that will be created in Redis and storing logs.
        """
        logging.Handler.__init__(self)
        self.queue_name = queue_name

        if isinstance(redis_pool, redis.ConnectionPool):
            self.redis = redis.Redis(connection_pool=redis_pool)

    def emit(self, record) -> None:
        """Emit a log message on redis queue."""
        try:
            bmsg = self.format(record).encode("utf8")
        except Exception:
            self.handleError(record)
            return

        self.redis.lpush(self.queue_name, bmsg)
