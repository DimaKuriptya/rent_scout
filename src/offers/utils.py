import asyncio
import aiohttp
from bs4 import BeautifulSoup


def olx_handler(data):
    return 'olx'


def dim_ria_handler(data):
    return 'dim_ria'


def rieltor_handler(data):
    return 'rieltor'


rent_sites = {
    'olx': ('https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH', olx_handler),
    'dim_ria': ('https://dom.ria.com/uk/arenda-kvartir/kiev/', dim_ria_handler),
    'rieltor': ('https://rieltor.ua/kiev/flats-rent/', rieltor_handler)
}


async def fetch_data(url, handler, session):
    async with session.get(url) as response:
        result = await response.text()
    raw_data = BeautifulSoup(result)
    ready_data = handler(raw_data)
    return ready_data


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for site in rent_sites:
            tasks.append(fetch_data(rent_sites[site][0], rent_sites[site][1], session))
        res = await asyncio.gather(*tasks)
    return ' | '.join(res)


def get_data():
    return asyncio.run(main())
