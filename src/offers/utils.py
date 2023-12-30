import asyncio
import aiohttp


rent_sites_links = {
    'olx': 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH',
    'dim_ria': 'https://dom.ria.com/uk/arenda-kvartir/kiev/',
    'rieltor': 'https://rieltor.ua/kiev/flats-rent/'
}


async def olx_handler(url, session):
    return 'olx response'


async def dim_ria_handler(url, session):
    return 'dim ria response'


async def rieltor_handler(url, session):
    return 'rieltor response'


async def main():
    async with aiohttp.ClientSession() as session:
        cors = [
            olx_handler(rent_sites_links['olx'], session),
            dim_ria_handler(rent_sites_links['dim_ria'], session),
            rieltor_handler(rent_sites_links['rieltor'], session)
        ]
        res = await asyncio.gather(*cors)
    return ' | '.join(res)


def get_data():
    return asyncio.run(main())
