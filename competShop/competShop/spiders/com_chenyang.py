#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2020/4/7 10:37
# software  : PyCharm

# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from competShop.items import JinPIn
from competShop.untils import address_json

#todo：晨阳店铺爬虫
class ChengyangSpider(scrapy.Spider):
    name = 'chengyang'
    allowed_domains = ['www.chenyang.com']
    start_urls = "http://www.chenyang.com/index.php?m=content&c=index&a=lists&catid=27&p={p}&city={city}"
    next_urls = "http://www.chenyang.com/index.php?m=content&c=index&a=lists&catid=27&p={p}&city={city}&page={page}"
    built_url = "http://www.chenyang.com/"

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS':{
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh - CN, zh;q = 0.9",
            "Cache-Control": "max - age = 0",
            "Connection": "keep - alive",
            "Host": "www.chenyang.com",
            "Upgrade-Insecure-Requests": "1",
        }
    }

    def start_requests(self):
        citys = address_json.address
        for i in citys:
            pro = i['p']
            # print(i)
            p = parse.quote(i['p'])
            for c in i['city']:
                cit = c
                # if '北京' in i['p']:
                c = parse.quote(c)
                page = 1
                url = self.start_urls.format(p=p, city=c)
                yield scrapy.Request(url=url, callback=self.parse,
                                         meta={'page': 1, 'p': p, "c": c, 'pro': pro, 'cit': cit})

    def parse(self, response):
        # with open('chengyang.html','w') as f:
        #     f.write(response.text)
        value = response.xpath('//ul[@class="list-zmd"]/li')
        if value:
            pro = response.meta['pro']
            city = response.meta['cit']
            io_data = {'data':[]}
            for i in value:
                name = i.xpath('div[1]/p/strong//text()').extract_first('')
                address = i.xpath('div[2]/p//text()').extract_first('')
                item = {}
                item['name'] = name
                item['address'] = address
                item['province'] = pro
                item['city'] = city
                item['area'] = ""
                item['numbers'] = ""
                item['telphone'] = ""
                item['types'] = 3
                print(item)
                io_data['data'].append(item)
            yield io_data
            if response.xpath('//ul[@class="pages"]/li'):
                len_num = len(response.xpath('//ul[@class="pages"]/li'))
                ressult_li = response.xpath('//ul[@class="pages"]/li[{num}]/a/@href'.format(num=len_num-1)).extract_first('')
                page = response.meta['page']
                page += 1
                c = response.meta['c']
                p = response.meta['p']
                if ressult_li:
                    url = self.built_url + ressult_li
                    yield scrapy.Request(url=url, callback=self.parse,
                                     meta={'page': page, 'p': p, "c": c, 'pro': pro, 'cit': city})
