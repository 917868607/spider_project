#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2020/4/7 10:39
# software  : PyCharm


import scrapy
from urllib import parse
import json
from competShop.items import JinPIn
from competShop.untils import address_json

#todo：华润爬虫
class HuarunqiSpider(scrapy.Spider):
    name = 'huarunqi'
    allowed_domains = ['www.huarun.com']
    start_urls = "http://www.huarun.com/service/store/search?province={}&city=&area=&address=&design=off&page=1&limit=10000"

    def start_requests(self):
        citys = address_json.address
        for i in citys:
            cit = parse.quote(i['p'])
            url = self.start_urls.format(cit)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        if 'datas' in result['result']:
            io_data = {'data': []}
            for j in result['result']['datas']:
                name = j['name']
                address = j['address']
                province = j['province']
                city = j['city']
                area = j['area']
                numbers = j['numbers']
                telphone = j['telphone']
                item = {}
                item['name'] = name
                item['address'] = address
                item['province'] = province
                item['city'] = city
                item['area'] = area
                item['numbers'] = numbers
                item['telphone'] = telphone
                item['types'] = 1
                io_data['data'].append(item)
            print('＃＃＃＃＃＃＃＃＃＃＃＃开始存入redis＃{}＃＃＃＃＃＃＃＃＃＃＃＃＃＃'.format(io_data))
            yield io_data
        else:
            print('########################没有结果＃＃＃＃＃＃＃＃',result)
