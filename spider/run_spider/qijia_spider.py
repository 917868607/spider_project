#!/usr/bin/env Python
#-*-coding:utf-8-*-

import random
import re
# author    :Guido.shu
# datetime  :2020/4/20 9:47
# software  : PyCharm
import requests
import time
from pyquery import PyQuery as pq
import json

from mysqlTool.redis_tool import Pipline_to_redis_server
from proxyTool import AbuyunSpider, Setting
from mysqlTool.save_mysql import MysqlUntileFunction
from conf.useragent import random_useragent
from mysqlTool.py_bloom import BloomFilter
import datetime


class qijiaSpider(object):

    def __init__(self,setting=Setting()):
        self.requestsProxies = self.reutnRequestsProxies()
        self.builtUrl = 'https://www.jia.com/zx/{}/company/gexingbao/'
        self.db_name = setting.mysql_table_qijia_dbname

    def reutnRequestsProxies(self):
        """
        :return: 返回requests的proxies
        """
        return AbuyunSpider.returnRequestProxies()

    def returnBuiltHeaders(self, path, RefererUrl=None):
        """
        构造headers
        :return:
        """
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.jia.com",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "user-agent": random_useragent(),
         }
        if RefererUrl:
            headers['Referer'] = RefererUrl

        return headers

    def process_response(self, response, meta):
        """
        处理response
        :param response:
        :return:
        """
        # print(response)
        # with open('齐家.html', 'w', encoding='utf-8') as f:
        #     f.write(response.text)
        documents = pq(response.text)
        li_params = documents('.company-item > div')
        # mysqlunit = MysqlUntileFunction()
        io_data = {self.db_name:[]}
        for li in li_params.items():
            href_params = li('a').attr('href')
            # todo:公司名称
            companyName = li('div > h2 > a').text()
            # todo:案例数量
            span_params = li('div > div ')('.tag-count > span')
            case_num = work_num = foreman = stylist_num= ''
            for span in span_params.items():
                text_params = span.text()
                if '案例' in text_params:
                    case_num = text_params[2:]
                elif '工地' in text_params:
                    work_num = text_params[2:]
                elif '工长' in text_params:
                    foreman = text_params[2:]
                elif '设计师' in text_params:
                    stylist_num = text_params[3:]
            item = {
                'case_num': case_num,
                'work_num': work_num,
                'foreman': foreman,
                'stylist_num': stylist_num,
                'companyName': companyName,
                'href_params': href_params,
                'city': meta['city'],
            }
            bloom = BloomFilter()

            if bloom.isContains(json.dumps(item)):
                print('#############{}公司已经存入###########'.format(item['companyName']))
                continue

            io_data[self.db_name].append(item)
            print('正在爬去{}'.format(meta['city']))
        server = Pipline_to_redis_server()
        server.sadd(io_data)
        nextPage = documents('.changedown').text()
        if '下一页' in nextPage:
            pattern = re.compile(' |>')
            next_page = re.sub(pattern, '', nextPage)
            if '下一页' == next_page:
                nextpage_url = documents('.changedown').attr('href')
            else:
                nextpage_url = documents('.changedown').eq(1).attr('href')
            page = re.search(re.compile('(\d+)'), nextpage_url)
            print('################正在爬取{}页##############'.format(int(page.group(1)) - 1))
            nextUrl = 'https:' + nextpage_url
            response = self.process_request(nextUrl, Referer=response.url)
            self.process_response(response=response, meta=meta)
        else:
            page = documents('.cur').text()
        try:
            print('################正在爬取最后{}页---爬虫结束##############'.format(page))
        except Exception as e:
            print(e)

    # todo：处理requests 请求URL
    def process_request(self, nextPage,meta=None, Referer=None):
        path_params = '/' + '/'.join(nextPage.split('/')[-3:])
        count = 0
        while 1:
            try:
                response = requests.get(url=nextPage,
                                        headers=self.returnBuiltHeaders(path=path_params, RefererUrl=Referer),
                                        timeout=3, allow_redirects=False, proxies=self.reutnRequestsProxies())
                if response.status_code == 200:
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

    # todo：获取城市列表
    def process_city(self):
        url = 'https://www.jia.com/citylist/'
        response = self.process_request(url)
        if response.status_code == 200:
            document = pq(response.text)
            city = document('.city_main > dl > dd')
            result = [{'city': x.text(), 'city_link': x('a').attr('href').split('/')[-2]} for x in city.items()]
            return result

    # todo：处理url
    def process_start(self):
        """
        处理url
        :return:
        """
        result = self.process_city()
        for key in result:
            url = self.builtUrl.format(key['city_link'])
            response = self.process_request(url,meta=key)
            print(response)
            self.process_response(response, meta=key) if response else ''


    def start(self):
        print('###########################齐家爬虫开启##############')

        self.process_start()


if __name__ == '__main__':
    print('##########################齐家店铺爬取开始{}###################'.format(datetime.datetime.now()))
    tubatu = qijiaSpider()
    tubatu.start()
    print('##########################华润店铺爬取开始{}###################'.format(datetime.datetime.now()))