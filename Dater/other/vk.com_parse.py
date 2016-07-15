#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
import re, json

first = lambda x: x[0] if x else None
xp = lambda x, y: x.xpath(y).extract()


class SpiderParse(Spider):
    name = 'VK.com'
    allowed_domains = ['vk.com']
    start_urls = ['https://vk.com/al_search.php']
    all_id = []

    def start_requests(self):
        for i in range(1, 30, 20):
            yield FormRequest(url='https://vk.com/al_search.php',
                              formdata={
                                  'al': '1',
                                  'c[age_from]': '16',
                                  'c[age_to]': '30',
                                  'c[city]': '2',
                                  'c[country]': '1',
                                  'c[name]': '1',
                                  'c[online]': '0',
                                  'c[photo]': '1',
                                  'c[section]': 'people',
                                  'c[sex]': '1',
                                  'offset': str(i)},
                              callback=self.parse_search)

    def parse_search(self, response):
        all_id_page = re.findall('bigphOver\(this, ([0-9]+)\)', response.body)

        for id_user in all_id_page:
            if id_user not in self.all_id:
                self.all_id.append(id_user)
                yield FormRequest(url='https://vk.com/al_photos.php',
                                  formdata={'act': 'fast_get_photo',
                                            'al': '1',
                                            'oid': str(id_user)},
                                  meta={'oid': id_user},
                                  callback=self.get_photo)

    def get_photo(self, response):
        json_data = json.loads(response.body[response.body.find('{'):])
        # big_size_image = sorted(json_data['temp'].keys())[-1]
        # original_image = json_data['temp']['base'] + json_data['temp'][big_size_image][0] + u'.jpg'
        yield FormRequest(url='https://vk.com/al_photos.php',
                          formdata={
                                'act': 'show',
                                'al': '1',
                                'list': 'photos' + first(json_data['_id'].split('_')),
                                'module': 'profile',
                                'photo': json_data['_id']},
                          callback=self.parse_other_photo)

    def parse_other_photo(self, response):
        text = response.body
        a = text.find('<!><!json>') + 10
        b = text.find('<!><!json>', a)
        # json_data = json.loads(text[a:b])
        # print json.dumps(text[a:b], sort_keys=True, indent=4)
        print text[a:b]
        print '*' * 200



        # print json_data
if __name__ == '__main__':
    log_file = SpiderParse().name + '_log.txt'
    process = CrawlerProcess({
        'CONCURRENT_ITEMS': 400,
        'USER_AGENT': 'Googlebot/2.1 (+http://www.google.com/bot.html)',
        'DOWNLOAD_DELAY': 0.3,
        'CONCURRENT_REQUESTS': 20,
        'LOG_ENABLED': True,
        'LOG_FILE': log_file
    })
    process.crawl(SpiderParse)
    process.start()