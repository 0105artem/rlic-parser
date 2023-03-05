import asyncio
import os
from typing import List

from loguru import logger

from db.models.models import DBCardFields
from src.client import Client
from src.parser import RlicParser
from src.redis import RedisCli
from src.utils import ping


class ParserProcess:
    def __init__(self, urls: List[str], worker_id: int, rq_name: str = "db_cards_queue") -> None:
        self.tables_queue = asyncio.Queue()
        self.cards_queue = asyncio.Queue()
        self.rq_name: str = rq_name
        self.urls = urls
        self.worker_id = worker_id
        self.redis_client = RedisCli()

    async def read_tables(self) -> None:
        """
        Coroutine for reading tables. Until the self.tables_queue empty, it will be
        getting pack of urls from the self.tables_queue, creating tasks for getting
        and parsing each table and after that filling self.cards_queue with parsed
        cards ids from a table.
        """

        try:
            client = Client()
            while self.tables_queue.qsize():
                # Number of simultaneously sent requests. Shouldn't be more than 10 or more than queue size.
                num_req = min(10, self.tables_queue.qsize())

                urls = [await self.tables_queue.get() for _ in range(num_req)]

                tasks = [asyncio.create_task(self.get_table(client, url)) for url in urls]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Handling results and filling cards_queue
                for res in results:
                    self.tables_queue.task_done()

                    if isinstance(res, Exception):
                        continue

                    if res['status_code'] == 200:
                        # Else fill cards_queue with card's url for each successful result.
                        for license_id in res['licenses_ids']:
                            url = f'https://islod.obrnadzor.gov.ru/rlic/details/{license_id}/'
                            await self.cards_queue.put(url)
                    elif res['status_code'] >= 500:
                        logger.error(f"Failed to parse table {res['table_id']} from {res['url']}. "
                                     f"Response status code -- <{res['status_code']}>. "
                                     f"Is server available?")
                        available = await self.check_server(url='https://islod.obrnadzor.gov.ru/rlic/')
                        if available:
                            # If server is alive then put table url back to queue
                            await self.tables_queue.put(res['url'])
                        else:
                            break
                    if res['status_code'] >= 400:
                        logger.error(f"Failed to parse table {res['table_id']} from {res['url']}. "
                                     f"Response status code -- <{res['status_code']}>")
                        continue
        finally:
            await client.session.close()

    async def read_cards(self) -> None:
        """
        Coroutine for reading cards. Until the self.tables_queue and self.cards_queue
        are empty, it will be getting pack of urls from the self.cards_queue, creating
        tasks for getting and parsing each card and after that filling the redis queue
        with parsed cards to write cards into the database in the separate process.
        """
        try:
            client = Client()
            while True:
                if self.cards_queue.qsize():
                    num_req = min(10, self.cards_queue.qsize())

                    urls = [await self.cards_queue.get() for _ in range(num_req)]

                    tasks = [asyncio.create_task(self.get_card(client, url)) for url in urls]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for res in results:
                        if isinstance(res, Exception):
                            continue

                        if res['status_code'] == 200:
                            # Change card rus fields to eng in order to write into the database.
                            card = {v: res['card'][k] for k, v in DBCardFields.keys.items()}
                            card['license_id'] = res['license_id']
                            self.redis_client.lpush(self.rq_name, str(card))
                        elif res['status_code'] >= 500:
                            logger.error(f"Failed to parse card {res['license_id']} from {res['url']}. "
                                         f"Response status code -- <{res['status_code']}>. "
                                         f"Is server available?")
                            available = await self.check_server(url='https://islod.obrnadzor.gov.ru/rlic/')
                            if available:
                                # If server is alive then put table url back to queue
                                await self.cards_queue.put(res['url'])
                            else:
                                break
                        if res['status_code'] >= 400:
                            logger.error(f"Failed to parse card {res['license_id']} from {res['url']}. "
                                         f"Response status code -- <{res['status_code']}>")
                            continue

                    for _ in results:
                        self.cards_queue.task_done()
                else:
                    # If cards_queue is empty sleep for 3 sec.
                    await asyncio.sleep(3)
        except asyncio.CancelledError:
            await client.session.close()

    @staticmethod
    async def get_table(client: Client, url: str, payload: dict = None) -> dict:
        """
        Send post request and parse table.
        :param client: Asynchronous client that sends post request.
        :param url: Link page that func parsing.
        :param payload: Searching parameters. E.g., to search for active licenses payload should
                        contain 'licenseStateId' param equals to 1.
        :return: {url: table url, status_code: response status code, table_id: table's page number,
                  licenses_ids: IDs of licenses that managed to parse}
        """

        if payload is None:
            payload = {'licenseStateId': 1}

        # Getting table id from url query param 'page'
        table_id = url.split('page=')[-1]

        page = await client.post(url, payload)
        status_code = page['status_code']

        if status_code == 200:
            html_doc = page['response']
            licenses_ids = RlicParser.parse_table(html_doc)
        else:
            licenses_ids = None

        return {'url': url, 'status_code': status_code, 'table_id': table_id, 'licenses_ids': licenses_ids}

    async def check_server(self, url: str = 'https://islod.obrnadzor.gov.ru/rlic/') -> int:
        """Check if server available by sending requests to the server."""
        for i in range(10):
            server_available = await ping(url)
            if server_available:
                return 1
            else:
                if i == 9:
                    logger.error(f"Server is not available. Stopping worker {self.worker_id}, "
                                 f"PID: {os.getpid()}")
                    await self.clear_queue(self.cards_queue)
                    await self.clear_queue(self.tables_queue)
                    return 0
                logger.warning("Seems like server is not available. Will check again in 30 secs.")
                await asyncio.sleep(30)

    @staticmethod
    async def clear_queue(queue: asyncio.Queue) -> None:
        while queue.qsize():
            await queue.get()
            queue.task_done()

    @staticmethod
    async def get_card(client: Client, url: str) -> dict:
        """
        Send get request and parse card.
        :param client: Asynchronous client that sends get request.
        :param url: Card url
        :return: {url: card url, status_code: response status code, license_id: unique license's id,
                  card: parsed card}
        """
        license_id = url[:-1].split('/')[-1]
        page = await client.get(url)
        status_code = page['status_code']

        if status_code == 200:
            html_doc = page['response']
            card = RlicParser.parse_card(html_doc)
        else:
            card = None

        return {'url': url, 'status_code': status_code, 'license_id': license_id, 'card': card}

    async def run(self) -> None:
        """
        Run two coroutines. One for reading tables, other for reading cards.
        They will run until the tables queue with tables urls and cards queue
        with cards urls empty."""

        for url in self.urls:
            await self.tables_queue.put(url)

        read_table_task = asyncio.create_task(self.read_tables())
        read_cards_task = asyncio.create_task(self.read_cards())

        await self.tables_queue.join()
        await self.cards_queue.join()

        read_cards_task.cancel()
        await asyncio.gather(read_table_task, read_cards_task, return_exceptions=True)
