import time

import aiohttp

from loguru import logger


class Client:
    def __init__(self, headers: dict = None) -> None:
        self.session = aiohttp.ClientSession()
        if not headers:
            self.headers = {
                # 'content-type': 'application/x-www-form-urlencoded',
                'accept': '*/*',
                'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0'
            }
        else:
            self.headers = headers

    async def post(self, url: str, payload: dict = None, params: dict = None) -> dict:
        # logger.info(f"Sending request to {url}")
        start = time.time()
        async with self.session.post(url, headers=self.headers, params=params, data=payload) as resp:
            logger.info(f"<{resp.status}> Got response from {url} in {time.time() - start}s.")
            resp_text = await resp.text()
            return {'status_code': resp.status, 'response': resp_text}

    async def get(self, url: str, params: dict = None) -> dict:
        # logger.info(f"Sending request to {url}")
        start = time.time()
        async with self.session.post(url, headers=self.headers, params=params) as resp:
            logger.info(f"<{resp.status}> Got response from {url} in {time.time() - start}s.")
            resp_text = await resp.text()
            return {'status_code': resp.status, 'response': resp_text}
