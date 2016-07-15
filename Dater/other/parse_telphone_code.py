#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from scrapy.selector import Selector

first = lambda x: x[0] if x else None
xp = lambda x, y: x.xpath(y).extract()


class SpiderParse(Spider):
    name = 'ParsePhone'

    def start_requests(self):
        # response.xpath
        url = 'http://en.sanstv.ru/codes/?&pos={0}&ajax='
        for page in range(0, 100, 25): # 800
            yield Request(url.format(page), callback=self.parse_codes)

    def parse_codes(self, response):
        # print response.body
        for string in response.xpath('//table/tbody/tr'):
            # print string.xpath('td[2]/a/text()').extract()
            if not bool(string.xpath('td[1]/span')):
                print string.xpath('td[3]/a/text()').extract()
        # print strings[1].xpath('//tr/td[2]/a/text()').extract()
        # for string in strings:
        #     print string.xpath('tr/td[2]/a/text()').extract()


if __name__ == '__main__':
    process = CrawlerProcess({
        'CONCURRENT_ITEMS': 400,
        'USER_AGENT': 'Googlebot/2.1 (+http://www.google.com/bot.html)',
        'DOWNLOAD_DELAY': 0.3,
        'CONCURRENT_REQUESTS': 20,
        'LOG_ENABLED': True,
        'LOG_FILE': SpiderParse().name + '.log'
    })
    process.crawl(SpiderParse)
    process.start()