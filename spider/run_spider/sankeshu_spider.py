#!/usr/bin/env Python
#-*-coding:utf-8-*-

#todo：三棵树爬虫
import datetime
import random
import time

import requests
from pyquery import PyQuery as pq
from conf.useragent import random_useragent
from mysqlTool.redis_tool import Pipline_to_redis_server
from proxyTool import AbuyunSpider, Setting


class SankeshuSpider(object):
    name = 'jingpin'
    allowed_domains = ['www.skshu.com.cn']
    # next_urls = "https://www.skshu.com.cn/Agency/ajax_lists/province_id/{url}.html?p={page}"
    # start_urls = 'https://www.skshu.com.cn/Agency/result.html'
    start_url = 'https://www.skshu.com.cn/Agency/result.html?identification='
    next_url = "https://www.skshu.com.cn/Agency/ajax_lists.html?p={}"
    first_url = "https://www.skshu.com.cn/Agency/result.html?province_id={province}&city_id=&keyword="
    page_url = "https://www.skshu.com.cn/Agency/ajax_lists/province_id/{url}.html?p={page}"
    returnRequestsProxies = AbuyunSpider.returnRequestProxies()

    def __init__(self,setting=Setting()):
        self.db_name = setting.mysql_table_jinpin_dbname

    def returnBuiltHeaders(self, path, RefererUrl=None):
        """
        构造headers
        :return:
        """
        headers = {
            "Host": "www.skshu.com.cn",
            "Referer": "",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "text/html, */*; q=0.01", "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "keep-alive",
            "User-Agent": random_useragent(),
        }
        if RefererUrl:
            headers['Referer'] = RefererUrl

        return headers

    # todo：处理requests 请求URL
    def process_request(self, nextPage, meta=None, Referer=None):
        path_params = '/' + '/'.join(nextPage.split('/')[-3:])
        count = 0
        while 1:
            try:
                response = requests.get(url=nextPage,
                                        headers=self.returnBuiltHeaders(path=path_params, RefererUrl=Referer),
                                        timeout=3, allow_redirects=False, proxies=self.returnRequestsProxies)
                if response.status_code == 200:
                    print('#########解析成功ＵＲＬ: {}＃＃＃＃＃＃＃＃'.format(response.url))
                    return response
                else:
                    print(nextPage)
                    print(response)
                    if count > 40:
                        return False
                    count += 1
            except Exception as e:
                print(e)
                print(nextPage)
                time.sleep(random.randint(2, 5))

    def start_requests(self):
        start_urls = self.start_url
        response = self.process_request(nextPage=start_urls)
        if response:
            self.parse(response)

    def parse(self, response):
        # with open ('sankeshu.html','w') as f:
        #     f.write(response.text)
        docment = pq(response.text)
        io_data = {self.db_name: []}
        for tr in docment('#content-list').find('tr').items():
            item = {}
            item['name'] = tr('td').eq(0).text()
            item['address'] = tr('td').eq(4).text()
            item['province'] = tr('td').eq(1).text()
            item['city'] = tr('td').eq(2).text()
            item['area'] = tr('td').eq(3).text()
            item['numbers'] = tr('td').eq(5).text()
            item['telphone'] = ""
            item['types'] = 4
            io_data[self.db_name].append(item)
        server = Pipline_to_redis_server()
        server.sadd(io_data)
        for x in range(2,2000):
            next_url = self.next_url.format(x)
            response = self.process_request(nextPage=next_url)
            if response:
                self.parse_next(response)

    def parse_next(self,response):
        # print(response.text)
        if response.text:
            documents = pq(response.text)
            io_data = {self.db_name: []}
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
                io_data[self.db_name].append(item)
            server = Pipline_to_redis_server()
            server.sadd(io_data)


if __name__ == '__main__':
    print('##########################三棵树店铺爬取开始{}###################'.format(datetime.datetime.now()))
    sankeshu = SankeshuSpider()
    sankeshu.start_requests()
    print('##########################三棵树店铺爬取结束{}###################'.format(datetime.datetime.now()))