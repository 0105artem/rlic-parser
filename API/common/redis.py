import random
import string

from aioredis import Redis, TimeoutError, AuthenticationError
from loguru import logger

from settings import env


class RedisCli(Redis):

    def __init__(self):
        super(RedisCli, self).__init__(
            host=env.REDIS_HOST,
            port=env.REDIS_PORT,
            password=env.REDIS_PASSWORD,
            db=env.REDIS_DB,
            socket_timeout=env.REDIS_TIMEOUT,
            decode_responses=True  # Decode as utf-8
        )

    async def init_redis_connect(self) -> None:
        """
        Test if a connection still alive
        :return:
        """
        try:
            await self.ping()
        except TimeoutError:
            logger.error("Connection to Redis timed out")
        except AuthenticationError:
            logger.error("Authentication failed to connect to Redis")
        except Exception as e:
            logger.error(f"Connection to Redis is abnormal {e}")


class RedisHash:
    def __init__(self, r_client: RedisCli, hname: str, keys: tuple, values: tuple):
        self.hname = hname
        self.hash = {k: v for k, v in zip(keys, values)}
        if isinstance(r_client, RedisCli):
            self.redis_client = r_client

    async def init_hash(self):
        try:
            for k, v in self.hash.items():
                if v is None:
                    v = ""
                await self.redis_client.hset(self.hname, k, v)
        except Exception as e:
            logger.error(f"Failed to set hash to Redis database\n{e}")
            await self.redis_client.init_redis_connect()

    async def reset_hash(self):
        await self.init_hash()

    async def get_hash(self):
        try:
            task = await self.redis_client.hgetall(self.hname)
            if task:
                return {k: str(v) for k, v in task.items()}
        except Exception as e:
            logger.error(f"Failed to get hash from Redis database\n{e}")
            await self.redis_client.init_redis_connect()

    async def get_value(self, key):
        try:
            if key in self.hash.keys():
                value = await self.redis_client.hget(self.hname, key)
                return value
        except Exception as e:
            logger.error(f"Failed to get value of key {key} from Redis database\n{e}")
            await self.redis_client.init_redis_connect()

    async def set_value(self, key, value):
        try:
            if key in self.hash.keys():
                await self.redis_client.hset(self.hname, key, value)
        except Exception as e:
            logger.error(f"Failed to get value to key {key} from Redis database\n{e}")
            await self.redis_client.init_redis_connect()


class ParsingTask(RedisHash):
    _hash = {
        'task_id': None,       # str | None
        'status': 'inactive',  # str
        'started': None,       # str | None
        'ended': None,         # str | None
        'num_results': None,   # int | None
        'details': None        # str | None
    }

    def __init__(self, r_client):
        super(ParsingTask, self).__init__(
            r_client=r_client,
            hname="parsing_task",
            keys=tuple(self._hash.keys()),
            values=tuple(self._hash.values())
        )

    @staticmethod
    async def generate_task_id(size: int = 8):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    async def start(self):
        task_id = await self.generate_task_id()
        try:
            await self.set_value("task_id", task_id)
            await self.set_value("status", "active")
        except Exception as e:
            logger.error(f"Failed to set task as started in {self.hname}\n{e}")
            await self.redis_client.init_redis_connect()
        finally:
            return task_id

    async def get_status(self):
        return await self.get_value('status')

    async def get_task_id(self):
        return await self.get_value('task_id')

    async def get_task(self):
        return await self.get_hash()


redis_client = RedisCli()
parsing_task = ParsingTask(redis_client)
