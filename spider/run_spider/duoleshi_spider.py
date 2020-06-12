#!/usr/bin/env Python
#-*-coding:utf-8-*-


#todo:多乐士爬虫
import datetime
import json
import random
import time
import requests
from conf.useragent import random_useragent
from mysqlTool.redis_tool import Pipline_to_redis_server
from proxyTool import AbuyunSpider, Setting


class DuoleshiSpider(object):
    name = 'duoleshi'
    allowed_domains = ['www.dulux.com.cn']
    # start_urls = "https://www.dulux.com.cn/find/store-ajax?address={address}&attributes=&language=zh&pagenum={page}"
    start_urls = "https://www.dulux.com.cn/ajax/stores-api/select/all-id?flds=id,latitude,longitude,companyName,companyName_zh,address,address_zh,city,city_zh,zipcode,zipcode_zh,attributeCodes,brands,region,region_zh,phone,phone_zh,district,district_zh,country,countryCode_zh,country_zh"
    returnRequestsProxies = AbuyunSpider.returnRequestProxies()

    def __init__(self,setting=Setting()):
        self.db_name = setting.mysql_table_jinpin_dbname

    def returnBuiltHeaders(self, path, RefererUrl=None):
        """
        构造headers
        :return:
        """
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "if-none-match": "1591637021-1",
            "referer": "https://www.dulux.com.cn/zh/find-a-stockist",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
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
                                        headers=self.returnBuiltHeaders(path=path_params),
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
        url = self.start_urls
        response = self.process_request(nextPage=url)
        if response:
            self.parse(response)
        # yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)['response']['docs']
        print('####################爬取多乐士网站数据:{}条＃＃＃＃＃＃＃＃＃＃'.format(len(result)))
        import re
        if result:
            io_data = {self.db_name: []}
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
                    io_data[self.db_name].append(item)
                except Exception as e:
                    print(e)

            server = Pipline_to_redis_server()
            server.sadd(io_data)


if __name__ == '__main__':
    print('##########################多乐士店铺爬取开始{}###################'.format(datetime.datetime.now()))
    duoleshi = DuoleshiSpider()
    duoleshi.start_requests()
    print('##########################多乐士店铺爬取结束{}###################'.format(datetime.datetime.now()))