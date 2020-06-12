#!/usr/bin/env Python
#-*-coding:utf-8-*-
import datetime
import random
import re
import time

import requests
from pyquery import PyQuery as pq
from conf import address_json, Setting
from urllib import parse

from conf.useragent import random_useragent
from mysqlTool.redis_tool import Pipline_to_redis_server
from proxyTool import AbuyunSpider


class chenYangSpider(object):

    start_urls = "http://www.chenyang.com/index.php?m=content&c=index&a=lists&catid=27&p={p}&city={city}"
    next_urls = "http://www.chenyang.com/index.php?m=content&c=index&a=lists&catid=27&p={p}&city={city}&page={page}"
    built_url = "http://www.chenyang.com/"
    returnRequestsProxies = AbuyunSpider.returnRequestProxies()

    def __init__(self,setting=Setting()):
        self.db_name = setting.mysql_table_jinpin_dbname

    def returnBuiltHeaders(self, path, RefererUrl=None):
        """
        构造headers
        :return:
        """
        headers = {
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh - CN, zh;q = 0.9",
            "Cache-Control": "max - age = 0",
            "Connection": "keep - alive",
            "Host": "www.chenyang.com",
            "Upgrade-Insecure-Requests": "1",
            "user-agent": random_useragent(),
        }
        if RefererUrl:
            headers['Referer'] = RefererUrl

        return headers

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
                response = self.process_request(nextPage=url)
                if response:
                    self.parse(response, meta={'page': 1, 'p': p, "c": c, 'pro': pro, 'cit': cit})

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
                    if count > 20:
                        return False
                    count += 1
            except Exception as e:
                print(e)
                print(nextPage)
                time.sleep(random.randint(2, 5))

    def parse(self, response,meta):
        # with open('chengyang.html','w') as f:
        #     f.write(response.text)
        document_pq = pq(response.text)
        value = document_pq('.list-zmd > li')
        if value:
            pro = meta['pro']
            city = meta['cit']
            io_data = {self.db_name: []}
            for i in value.items():
                name = i('div').eq(0)('p > strong').text()
                address = i('div').eq(1)('p').text()
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
                io_data[self.db_name].append(item)
            server = Pipline_to_redis_server()
            server.sadd(io_data)
            if document_pq('.pages > li'):
                len_num = len(document_pq('.pages > li'))
                ressult_li = document_pq('.pages > li').eq(len_num-1)('a').attr('href')
                pattern = re.compile('page=(.*?)&')
                page_li = re.search(pattern,ressult_li).group()
                try:
                    page_url = re.search(pattern,response.url).group()
                except Exception as e:
                    page_url = ''
                if page_li == page_url:
                    ressult_li = ''
                page = meta['page']
                page += 1
                c = meta['c']
                p = meta['p']
                if ressult_li:
                    url = self.built_url + ressult_li
                    response = self.process_request(nextPage=url)
                    if response:
                        self.parse(response=response,meta={'page': page, 'p': p, "c": c, 'pro': pro, 'cit': city})


if __name__ == '__main__':
    print('##########################晨阳店铺爬取开始{}###################'.format(datetime.datetime.now()))
    # chenyang = chenYangSpider()
    # chenyang.start_requests()
    print('##########################晨阳店铺爬取结束{}###################'.format(datetime.datetime.now()))