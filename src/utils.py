from datetime import datetime
from typing import List

from loguru import logger

from src.client import Client


def current_date(date_format: str = "%d-%m-%Y_%H.%M.%S") -> str:
    """Return current date and time as string."""
    dt_string = datetime.now().strftime(date_format)
    return dt_string


def split_urls(urls: List[str], n: int) -> List[List[str]]:
    """Split list of urls into N even lists."""
    chunks = [[]]*n
    for i in range(n):
        chunks[i] = urls[i::n]

    return chunks


async def ping(url: str = 'https://islod.obrnadzor.gov.ru/rlic/') -> int:
    """Check if server available."""
    client = Client()
    page = await client.post(url)
    if page['status_code'] >= 500:
        logger.warning("Server is not available")
        res = 0
    else:
        res = 1
    await client.session.close()
    return res
