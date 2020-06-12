#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2020/4/7 10:40
# software  : PyCharm
import random
import time

import requests
import scrapy
from competShop.items import JinPIn
from pyquery import PyQuery as pq
from competShop.untils.proxyTool import AbuyunSpider


#todo：三棵树爬虫

class JingpinSpider(scrapy.Spider):
    name = 'jingpin'
    allowed_domains = ['www.skshu.com.cn']
    # next_urls = "https://www.skshu.com.cn/Agency/ajax_lists/province_id/{url}.html?p={page}"
    # start_urls = 'https://www.skshu.com.cn/Agency/result.html'
    start_url = 'https://www.skshu.com.cn/Agency/result.html?identification='
    next_url = "https://www.skshu.com.cn/Agency/ajax_lists.html?p={}"
    first_url = "https://www.skshu.com.cn/Agency/result.html?province_id={province}&city_id=&keyword="
    page_url = "https://www.skshu.com.cn/Agency/ajax_lists/province_id/{url}.html?p={page}"

    custom_settings = {
        "Accept": "text/html, */*; q=0.01", "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "keep-alive",
        # "Cookie": "PHPSESSID=rf5chegp4ori3k83bu7h8bvhj4; Hm_lvt_e11b1fa5e2aac53d0545ca501e01aba8=1571725134; _pykey_=caa90759-088a-5d7b-9a7b-65cdd1cf5b4c; Hm_lpvt_e11b1fa5e2aac53d0545ca501e01aba8=1571735029",
        "Host": "www.skshu.com.cn",
        "Referer": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    def start_requests(self):
        start_urls = self.start_url
        yield scrapy.Request(url=start_urls, callback=self.parse)

    def parse(self, response):
        # with open ('sankeshu.html','w') as f:
        #     f.write(response.text)
        docment = pq(response.text)
        # print(docment)
        io_data = {'data': []}
        for tr in docment('#content-list').find('tr').items():
            # print(tr)
            item = {}
            item['name'] = tr('td').eq(0).text()
            item['address'] = tr('td').eq(4).text()
            item['province'] = tr('td').eq(1).text()
            item['city'] = tr('td').eq(2).text()
            item['area'] = tr('td').eq(3).text()
            item['numbers'] = tr('td').eq(5).text()
            item['telphone'] = ""
            item['types'] = 4
            io_data['data'].append(item)
        yield io_data
        referer_url = ''
        page_num = 0
        # for num in range(1,200):
        #     if page_num > 20:
        #         continue
        #     next_url = self.page_url.format(page=num,url=response.meta['province'])
        #     print(next_url)
        #     self.custom_settings['Referer'] = referer_url if referer_url else response.url
        #     count = 1
        #     while 1:
        #         try:
        #             responseRequest = requests.get(next_url,proxies=AbuyunSpider.returnRequestProxies(),headers=self.custom_settings,timeout=5,allow_redirects=False)
        #             if responseRequest.status_code == 200:
        #                 # print(responseRequest.text)
        #                 if responseRequest.text:
        #                     yield scrapy.Request(url=next_url, callback=self.parse_next, headers=self.custom_settings,
        #                                          dont_filter=True,
        #                                          meta=response.meta)
        #                     break
        #                 count += 1
        #                 if count > 20:
        #                     page_num += 1
        #                     print('##################获取下一页异常{}################'.format(responseRequest.url))
        #                     break
        #             else:
        #                 print('###########获取地址状态吗异常{}＃＃＃＃＃＃＃＃＃＃＃＃'.format(next_url))
        #         except Exception as e:
        #             print(e)
        #             time.sleep(random.randint(2,3))
        #     referer_url = next_url
        for x in range(2,2000):
            next_url = self.next_url.format(x)
            yield scrapy.Request(url=next_url, callback=self.parse_next, headers=self.custom_settings,
                                                     dont_filter=True)

    def parse_next(self,response):
        # print(response.text)
        if response.text:
                documents = pq(response.text)
                io_data = {'data': []}
                for tr in documents('tr').items():
                    if not tr:
                        continue
                    item = {}
                    item['name'] = tr('td').eq(0).text()
                    item['address'] = tr('td').eq(4).text()
                    item['province'] = tr('td').eq(1).text()
                    item['city'] = tr('td').eq(2).text()
                    item['area'] = tr('td').eq(3).text()
                    item['numbers'] = tr('td').eq(5).text()
                    item['telphone'] = ""
                    item['types'] = 4
                    io_data['data'].append(item)
                yield io_data

