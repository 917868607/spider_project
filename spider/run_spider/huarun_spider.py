
#!/usr/bin/env Python
#-*-coding:utf-8-*-
#todo：华润爬虫
import datetime
import json
import random
import time
import requests
from conf import address_json, Setting
from urllib import parse
from conf.useragent import random_useragent
from mysqlTool.redis_tool import Pipline_to_redis_server
from proxyTool import AbuyunSpider


class HuarunqiSpider(object):
    name = 'huarunqi'
    allowed_domains = ['www.huarun.com']
    start_urls = "http://www.huarun.com/service/store/search?province={}&city=&area=&address=&design=off&page=1&limit=10000"
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

    def start_requests(self):
        citys = address_json.address
        for i in citys:
            cit = parse.quote(i['p'])
            url = self.start_urls.format(cit)
            response = self.process_request(nextPage=url)
            if response:
                self.parse(response)
            # yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        if 'datas' in result['result']:
            io_data = {self.db_name: []}
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
                io_data[self.db_name].append(item)
            print('＃＃＃＃＃＃＃＃＃＃＃＃开始存入redis＃{}＃＃＃＃＃＃＃＃＃＃＃＃＃＃'.format(io_data))
            # yield io_data
            print(io_data)
            server = Pipline_to_redis_server()
            server.sadd(io_data)
        else:
            print('########################没有结果＃＃＃＃＃＃＃＃',result)


if __name__ == '__main__':
    print('##########################华润店铺爬取开始{}###################'.format(datetime.datetime.now()))
    huarun = HuarunqiSpider()
    huarun.start_requests()
    print('##########################华润店铺爬取结束{}###################'.format(datetime.datetime.now()))