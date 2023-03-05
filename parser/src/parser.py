import math
import re
from typing import List

from bs4 import BeautifulSoup

from loguru import logger
from src.client import Client


class Parser:
    @staticmethod
    def make_soup(html_doc: str, parser: str = 'html.parser') -> BeautifulSoup:
        soup = BeautifulSoup(html_doc, parser)
        return soup


class RlicParser(Parser):
    @staticmethod
    def get_cards_num(soup: BeautifulSoup) -> int:
        """Search for h3 tag that contains results (cards) number on the search page.
           Return that number as integer"""

        # Поиск заголовка h3, содержащего результаты поиска
        try:
            h3 = soup.h3
            if h3:
                h3 = str(h3)
            else:
                raise AttributeError("h3 object is None")
        except AttributeError as e:
            logger.error(f"Can't find h3 tag with num of search results\n{e}")
            return 0

        # Достаю числовое значение из заголовка h3
        regex = re.compile(r'\((\d+)\)')
        results = regex.findall(h3)
        results = int(results[0]) if results else 0

        return results

    @staticmethod
    def count_pages(html_doc: str) -> dict:
        """
        Calculate the number of pages by dividing the number of results by 10.
        :param html_doc: HTML page that contains search results (cards) number.
        :return: number of pages and number of licenses.
        """

        main_page_soup = RlicParser.make_soup(html_doc, 'html.parser')
        # Getting overall number of cards
        results_num = RlicParser.get_cards_num(main_page_soup)
        logger.info(f"Got number of results -- {results_num}")

        # Getting table body
        table_rows = RlicParser.get_table_body(main_page_soup)

        # Count all rows inside table
        num_rows = len(table_rows)

        num_pages = math.ceil(results_num / num_rows)
        return {'num_pages': num_pages, 'num_licenses': results_num}

    @staticmethod
    def get_table_body(soup: BeautifulSoup) -> tuple:
        """Gets BeautifulSoup object that contains a table and returns table's body."""
        try:
            # Поиск тела таблицы
            tbody = soup.table.tbody
            if tbody is None:
                raise AttributeError("Can't find tbody tag")
        except AttributeError as e:
            logger.error(f"Failed to read table.\n{e}")
            return tuple()
        return tbody.find_all("tr")

    @staticmethod
    def parse_table(html_doc: str) -> List[str]:
        """
        Parse table from searching page.
        :param html_doc: HTML code of searching page that contains table with cards.
        :return: cards ids from the table.
        """

        soup = RlicParser.make_soup(html_doc)

        # Getting table body
        table_rows = RlicParser.get_table_body(soup)

        # Extracting cards ids
        cards_ids = [row['data-guid'] for row in table_rows]

        return cards_ids

    @staticmethod
    def parse_card(html_doc: str) -> dict:
        """
        Parse card from a table.
        :param html_doc: HTML code of card page.
        :return: Parsed card with its fields and values.
        """
        soup = RlicParser.make_soup(html_doc)

        card_rows = soup.table.find_all("td")
        card = {}
        for field, value in zip(card_rows[::2], card_rows[1::2]):
            field = field.text.strip()
            value = value.text.strip()
            card[field] = value

        return card


async def get_num_pages() -> dict:
    """
    Send request to the search url. Get number of results (cards) and calculate number of pages.
    :return: Number of pages and number of licenses.
    """
    client = Client()  # Создаю экземпляр класса Client с открытой aiohttp.ClientSession()

    # Забираю данные с первой страницы поиска
    main_page = await client.post(url='https://islod.obrnadzor.gov.ru/rlic/search/',
                                  payload={'licenseStateId': 1})

    if main_page['status_code'] == 200:
        html_doc = main_page['response']
        res = RlicParser.count_pages(html_doc)
    else:
        res = {'num_pages': 0, 'num_licenses': 0}

    await client.session.close()  # Закрываю aiohttp.ClientSession()

    return res
