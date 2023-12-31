import asyncio
import aiohttp
from bs4 import BeautifulSoup


def olx_handler(data):
    cards_list = data.find_all('a', class_='css-rc5s2u')
    offers_list = []
    for card in cards_list:
        attrs = {}
        attrs['link'] = 'https://www.olx.ua' + card.get('href')
        attrs['title'] = card.find('h6').text
        location_date = card.find('p', attrs={'data-testid': 'location-date'}).text.split(' - ')
        attrs['location'] = location_date[0]
        attrs['date'] = location_date[1]
        attrs['area'] = card.find('span').text
        attrs['price'] = card.find('p', attrs={'data-testid': 'ad-price'}).text
        attrs['image_link'] = card.find('img').get('src') 
        offers_list.append(attrs)
    return offers_list


def dim_ria_handler(data):
    return 'dim_ria'


def rieltor_handler(data):
    return 'rieltor'


rent_sites = {
    'olx': (olx_handler, 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH&search%5Border%5D=created_at:desc'),
    # 'dim_ria': ('https://dom.ria.com/uk/arenda-kvartir/kiev/', dim_ria_handler),
    # 'rieltor': ('https://rieltor.ua/kiev/flats-rent/', rieltor_handler)
}


async def fetch_data(handler, url, session):
    async with session.get(url) as response:
        result = await response.text()
    raw_data = BeautifulSoup(result, features="html.parser")
    ready_data = handler(raw_data)
    return ready_data


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for site in rent_sites:
            tasks.append(fetch_data(rent_sites[site][0], rent_sites[site][1], session))
        res = await asyncio.gather(*tasks)
    return res[0]


def get_data():
    return asyncio.run(main())
