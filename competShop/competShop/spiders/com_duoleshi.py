#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2020/4/7 10:38
# software  : PyCharm

import scrapy
import json
from urllib import parse
from competShop.items import JinPIn

#todo:多乐士爬虫
class DuoleshiSpider(scrapy.Spider):
    name = 'duoleshi'
    allowed_domains = ['www.dulux.com.cn']
    # start_urls = "https://www.dulux.com.cn/find/store-ajax?address={address}&attributes=&language=zh&pagenum={page}"
    start_urls = "https://www.dulux.com.cn/ajax/stores-api/select/all-id?flds=id,latitude,longitude,companyName,companyName_zh,address,address_zh,city,city_zh,zipcode,zipcode_zh,attributeCodes,brands,region,region_zh,phone,phone_zh,district,district_zh,country,countryCode_zh,country_zh"


    def start_requests(self):
        url = self.start_urls
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)['response']['docs']
        print('####################爬取多乐士网站数据:{}条＃＃＃＃＃＃＃＃＃＃'.format(len(result)))
        import re
        if result:
            io_data = {'data': []}
            for index,i in enumerate(result):
                # print(index)
                try:
                    name = i['companyName_zh']
                    pattern_params = re.compile('(.*?){}|(\s)+省'.format(i['city_zh']))
                    try:
                        region = re.search(pattern_params,i['address_zh']).group(1) #  省份
                    except Exception as e:
                        print(e)
                        region = ''
                    city = i['city_zh']  # 城市
                    subtitle = ''  # 授权号
                    address = i['address_zh']
                    phone = i.get('phone_zh','')
                    item = {}
                    item['name'] = name
                    item['address'] = address
                    item['province'] = region
                    item['city'] = city
                    item['area'] = ""
                    item['numbers'] = subtitle
                    item['telphone'] = phone
                    item['types'] = 2
                    io_data['data'].append(item)
                except Exception as e:
                    print(e)

            yield io_data