#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2020/4/20 9:47
# software  : PyCharm
import requests
from pyquery import PyQuery as pq
from proxyTool import AbuyunSpider
import time
import random
import re
from urllib import parse
from conf.useragent import random_useragent


"""
土巴兔爬虫
需求：爬取 城市、类型（家装or工装），家庭公司名称、地址、电话、设计案例、装修公司数
"""


class TubatuSpider(object):

    def __init__(self):
        self.requestsProxies = self.reutnRequestsProxies()
        self.builtUrl = 'https://sz.to8to.com/'

    def reutnRequestsProxies(self):
        """
        :return: 返回requests的proxies
        """
        return AbuyunSpider.returnRequestProxies()

    def returnBuiltHeaders(self, path, item, RefererUrl=None, page=None):
        """
        构造headers

        :return:
        """
        city = parse.quote(item['city'])
        city_num = item['city_num']
        city_type = item['city_type']

        sourceUrl_built_url = 'https%3A%2F%2F{}.to8to.com%2Fcompany%2F'.format(city_num)
        firstUrl_built_url = 'https://{city_num}.to8to.com/company/{city_type}/'.format(city_num=city_num,city_type=city_type)
        sourceUrl = item['sourceUrl'].replace('://', '%3A%2F%2F').replace('/', "%2F") if item.get('sourceUrl') else sourceUrl_built_url
        firstUrl = item.get('firstUrl').replace('://', '%3A%2F%2F').replace('/', "%2F") if item.get('firstUrl') else firstUrl_built_url.replace(':/', '%3A%2F%2F').replace('/', "%2F")
        nowpage = item.get('firstUrl').replace('://', '%253A%252F%252F').replace('/','%252F') if item.get('firstUrl') else firstUrl_built_url.replace(':/', '%253A%252F%252F').replace('/', "%252F")
        if not page:
            landpage = 'https%3A//sz.to8to.com/'
        else:
            landpage = firstUrl
        headers = {
            # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            # "accept-encoding": "gzip, deflate, br",
            # "accept-language": "zh-CN,zh;q=0.9",
            # "cache-control": "no-cache",
            # "pragma": "no-cache",
            # "sec-fetch-dest": "document",
            # "sec-fetch-mode": "navigate",
            # "sec-fetch-site": "cross-site",
            # "sec-fetch-user": "?1",
            # "upgrade-insecure-requests": '1',
            "user-agent": random_useragent()
            ,"cookie": "uid=CgoKUF61XAWCtJc0A7vvAg==; "
                       "to8tocookieid=f982c677f999237b9fe9e5ee3947f2cc806225; "
                       "tracker2019session=%7B%22session%22%3A%2217201522ce2109-0c32fb225c0495-14291003-2073600-17201522ce3201%22%7D; "
                       "tracker2019jssdkcross=%7B%22distinct_id%22%3A%2217201522ce612f-03e21b7f111ee1-14291003-2073600-17201522ce71e%22%7D; "
                       "to8to_sourcepage=; to8to_landtime=1589160062; "
                       "to8to_cook=OkOcClPzRWV8ZFJlCIF4Ag==; "
                       "to8to_townid=1103; to8to_tcode=sh; "
                       "to8to_tname=%E4%B8%8A%E6%B5%B7; "
                       "Hm_lvt_dbdd94468cf0ef471455c47f380f58d2=1589160063; "
                       "tender_popup_flag=true;"
                       " ONEAPM_BI_sessionid=9238.924|1589197648127; "
                       "Hm_lpvt_dbdd94468cf0ef471455c47f380f58d2={times}; act=freshen;"
                       "to8to_landpage={landpage}; "
                       "to8to_tcode={city_num}; to8to_tname={city}; "
                       "to8to_cmp_sourceUrl={sourceUrl}; "
                       "to8to_cmp_firstUrl={firstUrl}; "
                       "to8to_nowpage={nowpage}; ".format(city=city,
                                                          city_num=item['city_num'],
                                                          sourceUrl=sourceUrl,
                                                          firstUrl=firstUrl,
                                                          nowpage=nowpage,
                                                          landpage=landpage,times=now_to_timestamp())
        }
        if RefererUrl:
            headers['Referer'] = RefererUrl
        headers['sourceUrl'] = sourceUrl
        return headers

    def process_response(self, response, meta, item):
        """
        处理response
        :param response:
        :return:
        """
        # print(response)
        with open('土巴兔.html','w',encoding='utf-8') as f:
            f.write(response.text)
        documents = pq(response.text)
        li_params = documents('.company__list--content > ul > li')
        for li in li_params.items():
            bulitDivs = li('.company__info')
            href_params = li('a').attr('href')
            #todo:公司名称
            companyName = bulitDivs('.company__info--top').text()
            #todo:评论数量
            commentNum = bulitDivs('.company__info--all > .comment-count').text()
            #todo:日志数量
            logNum = bulitDivs('.company__info--all > .owner-diary').text()
            #todo：最近签约
            clientStatus = bulitDivs('.company__info--all')('.info-num > .recent-signing').text()
            #todo:价格
            priceNum = bulitDivs('.company__info--all')('.info-num > .average-price').text()

            print(companyName,commentNum,logNum,clientStatus,priceNum,href_params)

        #下一页
        print('ssssss', response.url)
        nextPage = documents('#nextpageid').attr('href')
        if nextPage:
            page = re.search(re.compile('(\d+)'), nextPage)
            item['sourceUrl'] = meta['firstUrl']
            item['firstUrl'] = response.url
            print('################正在爬取{}页##############'.format(int(page.group(1))-1))
            nextUrl = self.builtUrl + nextPage.split('/')[1] + '/' + meta['key_con'] + '-' + nextPage.split('/')[-1] + '/'

            response,meta = self.process_request(nextUrl, meta=meta, Referer=response.url, item=item)
            meta['firstUrl'] = response.url
            self.process_response(response=response, meta=meta,item=item)
        else:
            page = re.search(re.compile('page(\d+)'), response.url)

        print('################正在爬取{}页##############'.format(page.group(1)))

    #todo：处理requests 请求URL
    def process_request(self, nextPage, meta, item,Referer=None):
        path_params = '/' + '/'.join(nextPage.split('/')[-3:])
        """
        header
        """



        headers = self.returnBuiltHeaders(path=path_params, RefererUrl=Referer, item=item)
        meta['firstUrl'] = headers['sourceUrl']
        del headers['sourceUrl']
        while 1:
            try:
                first_url = nextPage[:-1]
                first_res = requests.get(first_url, headers={'user-agent': random_useragent()})
                with open('ss1.html', 'w') as f:
                    # print(first_res.text)
                    f.write(first_res.text)
                second_res = nextPage.replace('https', 'http')
                second_res = requests.get(second_res, headers={'user-agent': random_useragent()})
                with open('ss2.html', 'w') as f:
                    # print(second_res.text)
                    f.write(second_res.text)
                three_yrl = nextPage
                response = requests.get(url=three_yrl,
                                        headers=headers,
                                        timeout=3, allow_redirects=False, proxies=self.reutnRequestsProxies())
                if response.status_code == 200:
                    return response,meta
                else:
                    print(response)
            except Exception as e:
                print(e)
                time.sleep(random.randint(2, 5))



    #todo：处理url
    def process_start(self):
        """
        处理url
        :return:
        """
        url_item = {
            'ht1': "小户型",
            # 'ht4': "普通住宅",
        }
        city_params = [
            {'city': '上海', "city_num": "sh"},
            # {'city': '深圳', "city_num": "sz"},
        ]
        for key, value in url_item.items():
            for x in city_params:
                url = 'https://{city_num}.to8to.com/company/{key}/'.format(city_num=x['city_num'], key=key)
                x['city_type'] = key
                response = self.process_request(url, meta={'key_con': key, "value_con": value}, item=x)
                print(response)
                self.process_response(response[0], meta=response[1], item=x)

    def start(self):
        print('###########################土巴兔爬虫开启##############')

        self.process_start()

def now_to_timestamp(digits = 10):
    """获取13位时间"""
    time_stamp = time.time()
    digits = 10 ** (digits -10)
    time_stamp = str(round(time_stamp*digits))
    return time_stamp

if __name__ == '__main__':
    tubatu = TubatuSpider()
    tubatu.start()