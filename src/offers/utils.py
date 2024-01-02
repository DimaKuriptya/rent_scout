import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


class Offer():
    def __init__(self, attrs):
        for key, value in attrs.items():
            setattr(self, key, value)


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
        attrs['date'] = card.find('div', class_='catalog-card-update').find_all('span')[-1].text.split(' ')[-1]
        attrs['area'] = card.find('div', class_='catalog-card-details').find_all('div')[1].find('span').text.split(' / ')[0]
        attrs['price'] = card.get('data-label')
        attrs['image_link'] = card.find_all('img', class_='offer-photo-slider-slide-image')[0].get('data-src')
        offers_list.append(attrs)
    return offers_list


rent_sites = {
    'olx': (olx_handler, 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?currency=UAH&search%5Border%5D=created_at%3Adesc'),
    'rieltor': (rieltor_handler, 'https://rieltor.ua/kiev/flats-rent/?radius=20&sort=bycreated')
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
        browser = await session.chromium.launch()
        tasks = []
        for site in rent_sites:
            page = await browser.new_page()
            tasks.append(fetch_data(rent_sites[site][0], rent_sites[site][1], page))
        res = await asyncio.gather(*tasks)
        await browser.close()
    return [offer for site_list in res for offer in site_list]


def get_data():
    return asyncio.run(main())
