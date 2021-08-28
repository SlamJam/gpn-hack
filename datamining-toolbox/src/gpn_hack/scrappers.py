from datetime import datetime
import scrapy
from scrapy import Selector
import os
from scrapy.crawler import CrawlerProcess

def parse_date(s, dt_format='%Y-%m-%d'):
    return datetime.strptime(s, dt_format)


class RubaseScraper(scrapy.Spider):
    download_delay = 3.0

    def __init__(self, url, path, name='rubase_scrapper', date_from=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.url = url
        self.date_from = parse_date(date_from)
        self.path = path

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        sel = Selector(text=response.text)
        urls = sel.xpath('//loc/text()').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.extract_urls_from_page)

    def extract_urls_from_page(self, response):
        urls = Selector(text=response.text).xpath('//loc/text()').extract()
        dates = Selector(text=response.text).xpath('//lastmod/text()').extract()
        dates = [parse_date(date) for date in dates]
        for url, date in zip(urls, dates):
            if date < self.date_from:
                yield scrapy.Request(url=url, callback=self.save_page)

    def save_page(self, response):
        link = response.url.replace('https://', '').replace('http://', '').replace('/', '-')
        name = f'./{link}.html'
        fpath = os.path.join(self.path, name)
        with open(fpath, 'wb') as fout:
            fout.write(response.body)


def do_rubase_scrapping(path, url='https://rb.ru/sitemap.xml', date_from='2021-04-01'):
    if not os.path.exists(path):
        os.makedirs(path)
    process = CrawlerProcess()
    process.crawl(RubaseScraper, url=url, path=path, date_from=date_from)
    process.start()