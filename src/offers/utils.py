import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class Offer():
    months_numbers = {
        'січня': 1,
        'лютого': 2,
        'березня': 3,
        'квітня': 4,
        'травня': 5,
        'червня': 6,
        'липня': 7,
        'серпня': 8,
        'вересня': 9,
        'жовтня': 10,
        'листопада': 11,
        'грудня': 12,
    }

    def __init__(self, attrs):
        for key, value in attrs.items():
            setattr(self, key, value)

    @property
    def price(self):
        return self.__price
    
    @price.setter
    def price(self, value):
        int_price = int(''.join(value.split(' ')[:-1]))
        if '$' in value:
            dollar_rate = 38
            int_price *= dollar_rate
        self.__price = int_price

    @property
    def date(self):
        return self.__date
    
    @date.setter
    def date(self, str_date):
        if 'сьогодні' in str_date.lower():
            date_format = datetime.now().date()
        elif 'вчора' in str_date.lower():
            date_format = datetime.now().date() - timedelta(days=1)
        elif 'дні' in str_date.lower() or 'день' in str_date.lower():
            days_count = int(str_date.split(' ')[0])
            date_format = datetime.now().date() - timedelta(days=days_count)
        elif 'тиж' in str_date.lower():
            weeks_count = int(str_date.split(' ')[0])
            date_format = datetime.now().date() - timedelta(weeks=weeks_count)
        elif 'міс' in str_date.lower():
            weeks_count = int(str_date.split(' ')[0]) * 4
            date_format = datetime.now().date() - timedelta(weeks=weeks_count)
        elif 'р.' in str_date.lower() and 'тому' in str_date.lower():
            days_count = int(str_date.split(' ')[0]) * 365
            date_format = datetime.now().date() - timedelta(days=days_count)
        else:
            day, month, year = str_date.split(' ')[:-1]
            date_format = datetime(int(year), self.months_numbers[month], int(day)).date()
        self.__date = date_format


def olx_handler(data):
    offers_list = []
    cards_list = data.find_all('a', class_='css-rc5s2u')
    for card in cards_list:
        attrs = {}
        attrs['title'] = card.find('h6').text
        attrs['link'] = 'https://www.olx.ua' + card.get('href')
        location_date = card.find('p', attrs={'data-testid': 'location-date'}).text.split(' - ')
        attrs['location'] = location_date[0]
        attrs['date'] = location_date[1]
        attrs['area'] = card.find('span').text.split(' ')[0]
        attrs['price'] = card.find('p', attrs={'data-testid': 'ad-price'}).text
        attrs['image_link'] = card.find('img').get('src')
        offer_obj = Offer(attrs)
        offers_list.append(offer_obj)
    return offers_list


def rieltor_handler(data):
    offers_list = []
    cards_list = data.find_all('div', class_='catalog-card')
    for card in cards_list:
        attrs = {}
        attrs['title'] = card.find('div', class_='catalog-card-address').text
        attrs['link'] = card.find('a').get('href')
        attrs['location'] = card.find('div', class_='catalog-card-region').text
        attrs['date'] = card.find('div', class_='catalog-card-update').find_all('span')[-1].text.split(': ')[1]
        attrs['area'] = card.find('div', class_='catalog-card-details').find_all('div')[1].find('span').text.split(' / ')[0]
        attrs['price'] = card.get('data-label')
        attrs['image_link'] = card.find_all('img', class_='offer-photo-slider-slide-image')[0].get('data-src')
        offer_obj = Offer(attrs)
        offers_list.append(offer_obj)
    return offers_list


rent_sites = {
    'rieltor': (rieltor_handler, 'https://rieltor.ua/kiev/flats-rent/?radius=20&sort=bycreated'),
    'olx': (olx_handler, 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH&search%5Border%5D=created_at%3Adesc'),
}


async def fetch_data(handler, url, page):
    await page.goto(url)
    if handler == olx_handler:
        await page.get_by_test_id("dismiss-cookies-banner").click()
        for _ in range(10):
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(0.1)
        await asyncio.sleep(0.1)
    result = await page.content()
    raw_data = BeautifulSoup(result, features="html.parser")
    ready_data = handler(raw_data)
    return ready_data


async def main():
    async with async_playwright() as session:
        browser = await session.chromium.launch(headless=False)
        tasks = []
        for site in rent_sites:
            page = await browser.new_page()
            tasks.append(fetch_data(rent_sites[site][0], rent_sites[site][1], page))
        res = await asyncio.gather(*tasks)
        await browser.close()
    return [offer for site_list in res for offer in site_list]


def get_data():
    return asyncio.run(main())
