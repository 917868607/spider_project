#!/usr/bin/env Python
#-*-coding:utf-8-*-

import requests
from conf.useragent import random_useragent
from pyquery import PyQuery as pq
import re
from urllib import parse

from mysqlTool.redis_tool import Pipline_to_redis_server
from proxyTool import AbuyunSpider, datetime, Setting
import time
import random
import threadpool
import time,random
import os
from mysqlTool.save_mysql import MysqlUntileFunction
from mysqlTool.py_bloom import BloomFilter


class SessionTubatuSpider(object):

    def __init__(self,setting=Setting()):
        self.built_url_info = 'https://{}.to8to.com'
        self.db_name = setting.mysql_table_tubatu_dbname

    # todo:ｃｏｏｋｉｅ伪造
    def cookie(self,item,type_status):
        city = parse.quote(item['city'])
        city_num = item['city_num']
        type_key = type_status['key']
        sourceUrl_built_url = 'https%3A%2F%2F{}.to8to.com%2Fcompany%2F'.format(city_num)
        firstUrl_built_url = 'https://{city_num}.to8to.com/company/{city_type}/'.format(city_num=city_num,city_type=type_key)
        sourceUrl = item['sourceUrl'].replace('://', '%3A%2F%2F').replace('/', "%2F") if item.get('sourceUrl') else sourceUrl_built_url
        firstUrl = item.get('firstUrl').replace('://', '%3A%2F%2F').replace('/', "%2F") if item.get('firstUrl') else firstUrl_built_url.replace(':/', '%3A%2F%2F').replace('/', "%2F")
        nowpage = item.get('firstUrl').replace('://', '%253A%252F%252F').replace('/', '%252F') if item.get('firstUrl') else firstUrl_built_url.replace(':/', '%253A%252F%252F').replace('/', "%252F")

        items = {"to8tocookieid":"eae21f21367709f845f1198fb815d8b8144651",
                 # item = {"to8tocookieid":"f982c677f999237b9fe9e5ee3947f2cc806225",
                 #         "tracker2019session":"%7B%22session%22%3A%2217201522ce2109-0c32fb225c0495-14291003-2073600-17201522ce3201%22%7D",
                 "tracker2019session":"%7B%22session%22%3A%2217201522ce2109-0c32fb225c0495-14291003-2073600-17201522ce3201%22%7D",
                 "tracker2019jssdkcross": "%7B%22session%22%3A%2217201522ce2109-0c32fb225c0495-14291003-2073600-17201522ce3201%22%7D",
                 # "tracker2019jssdkcross": "%7B%22distinct_id%22%3A%2217201522ce612f-03e21b7f111ee1-14291003-2073600-17201522ce71e%22%7D",
                 "to8to_landtime":"1589160062",
                 "to8to_townid": "{}".format(item['cityID']),
                 "to8to_tcode": "{}".format(city_num),
                 "to8to_tname": "{}".format(city),
                 "Hm_lvt_dbdd94468cf0ef471455c47f380f58d2":"1589160063",
                 "tender_popup_flag": "true",
                 "ONEAPM_BI_sessionid": "9238.924|1589197648127",
                 "Hm_lpvt_dbdd94468cf0ef471455c47f380f58d2":"1589264798",
                 "act":"freshen",
                 "to8to_landpage": "https%3A//sz.to8to.com/",
                 "to8to_cmp_sourceUrl": "{}".format(sourceUrl),
                 "to8to_cmp_firstUrl": "{}".format(firstUrl),
                 "to8to_nowpage": "{}".format(nowpage)}

        sss = {
            "to8to_tcode":"{}".format(city_num), "to8to_tname":"{}".format(city),
            "to8to_townid":"{}".format(item['cityID']),
            "to8to_landpage":"https%3A%2F%2F{}.to8to.com%2Fcompany%2F".format(city_num),
            "to8to_cmp_sourceUrl":"{}".format(sourceUrl),
            "to8to_cmp_firstUrl":"{}".format(firstUrl), "to8to_nowpage":"{}".format(nowpage)

        }
        res = random.randint(1,2)
        # if res  == 1:
        sss = items

        return sss

    # todo:request q请求
    def process_requesst(self,session,url):
        while 1:
            try:
                response = session.get(url, headers={'user-agent': random_useragent()},
                                       proxies=AbuyunSpider.returnRequestProxies(),timeout=6)
                if response.status_code == 200:
                    break
            except Exception as e:
                print(e)
                time.sleep(random.randint(2, 5))
        return session, response

    def start(self,session,url=None,city=None,type_status=None,first=''):
        #todo:db参数
        if not first:
            built_url = 'https://{}.to8to.com/company/'.format(city['city_num'])
            cityID = self.get_cityid(built_url)
            city['cityID'] = cityID

        to8to_cmp_sourceUrl = city['to8to_cmp_sourceUrl'] if city.get('to8to_cmp_sourceUrl') else 'https%3A%2F%2F{}.to8to.com%2Fcompany%2F'.format(city['city_num'])
        cookie_params = self.cookie(city,type_status)
        cookiejar_params = requests.utils.cookiejar_from_dict(cookie_params, cookiejar=None, overwrite=True)
        session.cookies = cookiejar_params

        url = url if url else 'https://{city}.to8to.com/company/{type_status}/'.format(city=city['city_num'], type_status=type_status['key'])
        first_url = url[:-1]
        session, first_res = self.process_requesst(session, first_url)

        second_res = url.replace('https', 'http')
        session, second_res = self.process_requesst(session, second_res)
        three_yrl = url
        session, result = self.process_requesst(session, three_yrl)
        # print(result.text)
        # with open('ss3.html', 'w') as f:
        #     # print(result.text)
        #     f.write(result.text)
        documents = pq(result.text)

        li_params = documents('.company__list--content > ul > li')
        io_data = {self.db_name:[]}
        for li in li_params.items():
            bulitDivs = li('.company__info')
            href_params = li('a').attr('href')
            # todo:公司名称
            companyName = bulitDivs('.company__info--top').text()
            # todo:评论数量
            commentNum = bulitDivs('.company__info--all > .comment-count').text()
            # todo:日志数量
            logNum = bulitDivs('.company__info--all > .owner-diary').text()
            # todo：最近签约
            clientStatus = bulitDivs('.company__info--all')('.info-num > .recent-signing').text()
            # todo:价格
            priceNum = bulitDivs('.company__info--all')('.info-num > .average-price').text()

            # print(companyName, commentNum, logNum, clientStatus, priceNum, href_params)
            info_url = self.built_url_info.format(city['city_num']) + href_params
            #todo:去重
            bloom = BloomFilter()
            if bloom.isContains(info_url):
                print('#############{}公司已经存入###########'.format(info_url))
                continue
            response = self.process_requesst(session=session, url=info_url)
            response_result = self.process_info(response[1])
            item = {
                "companyName":companyName,
                "commentNum":commentNum,
                "logNum":logNum,
                "clientStatus":clientStatus,
                "priceNum" :priceNum,
                "phone":response_result['phone'],
                "address":response_result['address'],
                "desgin_number":response_result['desgin_number'],
                "decoration_number":response_result['decoration_number'],
                "comment_num":response_result['comment_num'],
                "city":city['city'],
                "mole":type_status['value'],
                "type_key":type_status['type_key']
            }
            io_data[self.db_name].append(item)
            # db_Params(companyName=companyName,commentNum=commentNum,logNum=logNum,clientStatus=clientStatus,priceNum=priceNum,
            #           phone=response_result['phone'],address=response_result['address'],desgin_number=response_result['desgin_number'],
            #           decoration_number=response_result['decoration_number'],
            #           comment_num=response_result['comment_num'],city=city['city'],
            #           mole=type_status['value'],type_key=type_status['type_key']
            #           )
            print('##################################爬取{}#######################'.format(companyName))

        server = Pipline_to_redis_server()
        server.sadd(io_data)
        #下一页
        nextPage = documents('#nextpageid').attr('href')
        if nextPage:
            page = re.search(re.compile('(\d+)'), nextPage)
            print('################正在爬取{}页##############'.format(int(page.group(1)) - 1))
            city['to8to_cmp_sourceUrl'] = to8to_cmp_sourceUrl
            city['firstUrl'] = result.url

            nextUrl = self.built_url_info.format(city['city_num']) + '/' + nextPage.split('/')[1] + '/' + type_status['key'] + '-' + nextPage.split('/')[-1] + '/'
            print('#######下一页{}'.format(nextUrl))
            self.start(session,city=city,url=nextUrl,type_status=type_status,first='ss')

    def process_info(self,response):
        item = {}
        document = pq(response.text)
        # with open('aaa.html','w') as f:
        #     f.write(response.text)
        params_doc = document('div[@class="right-content-wrap needguide"]')
        #名称
        item['companyName'] = params_doc('div > span').eq(0).text()
        item['desgin_number'] = ''
        item['decoration_number'] = ''
        item['comment_num'] = ''
        for x in params_doc('div[@class="service-num-bar clearfix"] div').items():
            # print(x)
            number = x('.number').text()
            title_params = x('.label').text()
            if '设计案例' in title_params:
                item['desgin_number'] = number
            elif '装修' in title_params:
                item['decoration_number'] = number
            else:
                item['comment_num'] = number
            # print(number,title_params)
        item['phone'] = params_doc('div[@class="head-com-tel shopTreasure pg-block-show pg-block-click"]').text()
        item['address'] = params_doc('div[@class="com-address-bx"] > p').text()
        if not item['phone']:
            print('ssss')
        return item

    # todo：获取城市地址：
    def process_start_built_url(self):
        url = 'https://www.to8to.com/index.html'

        while 1:
            try:
                response = requests.get(url, headers={
                    'user-agent': random_useragent()
                }, proxies=AbuyunSpider.returnRequestProxies())
                response.encoding = response.apparent_encoding
                if response.status_code == 200:
                    break
            except Exception as e:
                print(e)
                time.sleep(random.randint(2, 5))

        # with open('ddddd.html','w') as f:
        #     f.write(response.text)
        document = pq(response.text)
        res = []
        for x in document('div[@class="xzcs_dt"] > a').items():
            # print(x)
            item = {}
            pattern = re.compile('//(.*?)\.')
            item['city'] = x.text()
            item['city_num'] = re.search(pattern,x.attr('href')).group(1)

            res.append(item)
        return res

    # todo:获取cityid
    def get_cityid(self,url):
        while 1:
            print('###############获取城市ＩＤ{}'.format(url))
            try:
                response = requests.get(url, headers={
                    'user-agent': random_useragent()
                }, proxies=AbuyunSpider.returnRequestProxies())
                if response.status_code == 200:
                    break
            except Exception as e:
                print(e)
                time.sleep(random.randint(2,5))
        document = pq(response.text)
        cityID = document('#cityId').attr('value')
        return cityID


def db_Params(*args,**kwargs):
    """城市，类型（家装or工装），家装公司名称，地址，电话，设计案例数，装修工地数"""
    item = {
        '城市': kwargs['city'],
        '类型': kwargs['mole'],
        '家装公司名称': kwargs['companyName'],
        '地址': kwargs['address'],
        '电话': kwargs['phone'],
        '设计案例数': kwargs['desgin_number'],
        '装修工地数': kwargs['decoration_number'],
        '大类型': kwargs['type_key'],
    }
    mysqldb = MysqlUntileFunction()
    mysqldb.savaMysqlDB(kwargs, type='tubatu')

    print('#######################################获取参数{}#########################################'.format(item))

def start(city_params):
    url_item = [
        {'value': "小户型", 'key': "ht1", "type_key": "家装"},
        {'value': "普通住宅", 'key': "ht4", "type_key": "家装"},
        {'value': "复式", 'key': "ht19", "type_key": "家装"},
        {'value': "别墅", 'key': "ht3", "type_key": "家装"},
        {'value': "局部装修", 'key': "ht5", "type_key": "家装"},
        {'value': "其他", 'key': "ht0", "type_key": "家装"},
        {'value': "餐厅", 'key': "pt3", "type_key": "工装"},
        {'value': "商铺", 'key': "pt2", "type_key": "工装"},
        {'value': "展厅", 'key': "pt7", "type_key": "工装"},
        {'value': "办公室", 'key': "pt8", "type_key": "工装"},
        {'value': "休闲娱乐", 'key': "pt5", "type_key": "工装"},
        {'value': "酒店", 'key': "pt6", "type_key": "工装"},
        {'value': "其他", 'key': "pt0", "type_key": "工装"},
    ]
    spider = SessionTubatuSpider()
    # x = city_params.pop(0)
    for x in city_params:

        for k in url_item:
            session = requests.Session()
            spider.start(session, city=x, type_status=k)


if __name__ == '__main__':
    print('##########################土巴兔店铺爬取开始{}###################'.format(datetime.datetime.now()))
    spider = SessionTubatuSpider()
    city_params = spider.process_start_built_url()
    start(city_params)
    print('##########################土巴兔铺爬取开始{}###################'.format(datetime.datetime.now()))


