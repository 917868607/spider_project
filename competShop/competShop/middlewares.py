# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from competShop.untils.useragent import *
from scrapy.downloadermiddlewares.retry import *
from competShop.untils.abuyun import *
from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.text import TextResponse
import random
import base64
import time


class CompetshopSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CompetshopDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)





class UserAgentMiddleware(object):
    """This middleware allows spiders to override the user_agent"""

    def __init__(self, user_agent='Scrapy'):
        # try:
        #     self.user_agent = UserAgent()
        # except Exception as e:
        self.user_agent = RandomUserAgent()
    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        # crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agent = getattr(spider, 'user_agent', self.user_agent)
        pass
    def process_request(self, request, spider):
        """阿布云"""
        cookie_list = [0,1]
        # city = request.meta['city']
        # sheng = request.meta['sheng']
        # if 'ips' in request.meta:
            # ips = str(random.choice(request.meta['ips'].split(',')[:-1])).split(':')
        # ips = IP(city)

        if 'ips' in request.meta:
            ips = random.choice(request.meta['ips'])
            if ips:
                ip = str(ips).split(':')[0]
                port = str(ips).split(':')[1]
                request.meta['ip'] = ip
                request.meta['port'] = port
                proxyServer = "http://{}:{}".format(ip, port)
            else:
                request.meta['ip'] = ''
                request.meta['port'] = ''
                choice_res = random.choice(cookie_list)
                proxyServer = "http://http-dyn.abuyun.com:9020"
                # proxyServer = "http://{}:{}".format(ip, port)
                proxyUser = PROXYUSER
                proxyPass = PROXYPAWD
                proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode(
                    "utf8")
        else:
            request.meta['ip'] = ''
            request.meta['port'] = ''
            choice_res = random.choice(cookie_list)
            proxyServer = "http://http-dyn.abuyun.com:9020"
            # proxyServer = "http://{}:{}".format(ip, port)
            proxyUser = PROXYUSER
            proxyPass = PROXYPAWD
            proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")
        if 'https://m.' in request.url or 'https://wap.' in request.url:
            useragent = RandomUserAgent().random_ios
            # if 'm.sogou.com' in request.url:#360
            #     useragent = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
            request.headers.setdefault(b'User-Agent',useragent)
            if 'm.baidu.com' in request.url:
                request.headers.setdefault(b'Host', BAI_MOBIL.get('Host'))
                request.headers.setdefault(b'Connection', BAI_MOBIL.get('Connection'))
                request.headers.setdefault(b'Accept', BAI_MOBIL.get('Accept'))
                request.headers.setdefault(b'Cache-Control', BAI_MOBIL.get('Cache-Control'))
                request.headers.setdefault(b'X-Requested-With', BAI_MOBIL.get('X-Requested-With'))
                request.headers.setdefault(b'Async-Type', BAI_MOBIL.get('Async-Type'))
                request.headers.setdefault(b'Accept-Language', BAI_MOBIL.get('Accept-Language'))
                # request.headers.setdefault(b'Cookie', BAI_MOBIL.get('Cookie'))
            elif 'm.sogou.com' in request.url: #搜狗
                # request.headers.setdefault(b'Host',SOGOU_MOBIL.get('Host'))
                request.headers.setdefault(b'Connection',SOGOU_MOBIL.get('Connection'))
                request.headers.setdefault(b'Accept',SOGOU_MOBIL.get('Accept'))
                request.headers.setdefault(b'Accept-Language',SOGOU_MOBIL.get('Accept-Language'))
                # request.headers.setdefault(b'Cookie',SOGOU_MOBIL.get('Cookie'))
                request.headers.setdefault(b'X-Requested-With',SOGOU_MOBIL.get('X-Requested-With'))
            elif 'm.sm.cn' in request.url: #神马
                request.headers.setdefault(b'Connection',SHENMA_MOBIL.get('Connection'))
                request.headers.setdefault(b'Accept',SHENMA_MOBIL.get('Accept'))
                request.headers.setdefault(b'Accept-Language',SHENMA_MOBIL.get('Accept-Language'))
                # request.headers.setdefault(b'Cookie',SHENMA_MOBIL.get('Cookie'))
                request.headers.setdefault(b'X-Requested-With',SHENMA_MOBIL.get('X-Requested-With'))
            elif 'm.so.com' in request.url:#360
                # request.headers.setdefault(b'Host',MOBIL_SO.get('Host'))
                request.headers.setdefault(b'Connection',MOBIL_SO.get('Connection'))
                request.headers.setdefault(b'Accept',MOBIL_SO.get('Accept'))
                request.headers.setdefault(b'Accept-Language',MOBIL_SO.get('Accept-Language'))
                # request.headers.setdefault(b'Cookie',MOBIL_SO.get('Cookie'))
                # request.headers.setdefault(b'X-Requested-With',MOBIL_SO.get('X-Requested-With'))
        else:
            request.headers.setdefault(b'User-Agent', self.user_agent.u_random())
            if 'sogou.com' in request.url:
                # request.headers.setdefault(b'User-Agent', UserAgent().random)
                request.headers.setdefault(b'Accept', SOGOU_PC.get('Accept'))
                request.headers.setdefault(b'Cache-Control', SOGOU_PC.get('Cache-Control'))
                request.headers.setdefault(b'Accept-Language', SOGOU_PC.get('Accept-Language'))
                request.headers.setdefault(b'Connection', SOGOU_PC.get('Connection'))
                # if choice_res == 1:
                #     request.headers.setdefault(b'Cookie', SOGOU_PC.get('Cookie'))
                request.headers.setdefault(b'Upgrade-Insecure-Requests', SOGOU_PC.get('Upgrade-Insecure-Requests'))
            if 'www.baidu.com/s' in request.url:
                request.headers.setdefault(b'Accept',BAI_DU.get('Accept'))
                request.headers.setdefault(b'Accept-Language',BAI_DU.get('Accept-Language'))
                request.headers.setdefault(b'Cache-Control',BAI_DU.get('Cache-Control'))
                request.headers.setdefault(b'Connection',BAI_DU.get('Connection'))
                # if choice_res == 1:
                # request.headers.setdefault(b'Cookie',BAI_DU.get('Cookie'))
                request.headers.setdefault(b'Host',BAI_DU.get('Host'))
                request.headers.setdefault(b'Upgrade-Insecure-Requests',BAI_DU.get('Upgrade-Insecure-Requests'))
            elif 'www.so.com' in request.url: #360搜索
                request.headers.setdefault(b'Accept',PC_SO.get('Accept'))
                request.headers.setdefault(b'Accept-Language',PC_SO.get('Accept-Language'))
                request.headers.setdefault(b'Cache-Control',PC_SO.get('Cache-Control'))
                request.headers.setdefault(b'Connection',PC_SO.get('Connection'))
                # if choice_res == 1:
                #     request.headers.setdefault(b'Cookie',PC_SO.get('Cookie'))
                request.headers.setdefault(b'Upgrade-Insecure-Requests',PC_SO.get('Upgrade-Insecure-Requests'))
        if not request.meta['ip']:
            request.headers["Proxy-Authorization"] = proxyAuth
        request.meta["proxy"] =  proxyServer
        # print('使用代理ip########{}'.format(p))

    def process_exception(self, request, exception, spider):
        print('异常报错。。。。重新请求,异常url:{}'.format(request.url))
        response = get_response(request)
        if response:
            return response
        else:
            pass
        # return request
        # pass


class Process_Proxies(RetryMiddleware):
    logger = logging.getLogger(__name__)

    def process_response(self, request, response, spider):
        # if request.meta.get('dont_retry',False):
        #     return response
        # if response.status in self.retry_http_codes:
        if response.status != 200:
            print('状态码异常')
            reason = response_status_message(response.status)

            response = get_response(request=request)
            if response:
                return response
                # else:
                #     raise IgnoreRequest
            time.sleep(random.randint(5,10))
            return self._retry(request,reason,spider) or response
        return response

    def process_exception(self, request, exception, spider):
        # if isinstance(exception,self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry',False):
            # self.dele_proxy(request.meta.get('proxy',False))
        time.sleep(random.randint(1,3))
        self.logger.warning('连接异常,进行重试......')
        ipcheck = IP_Check()
        # print(type(request.headers))
        # city = request.meta['city']
        # ips = IP(city)
        # ip = ips[0]
        # port = ips[1]
        if 'ips' in request.meta:
            # ips = str(random.choice(request.meta['ips'].split(',')[:-1])).split(':')
            # request.meta['ip'] = ip
            # request.meta['port'] = port
            ips = random.choice(request.meta['ips'])
            ip = str(ips).split(':')[0]
            port = str(ips).split(':')[1]
            response = ipcheck.ip_test(url=request.url, user=request.headers['User-Agent'], ip=ip,
                                       prot=port)
        else:
            response = ipcheck.ip_test(url=request.url, user= request.headers.get('User-Agent') if request.headers.get('User-Agent') else RandomUserAgent().random_ios)
        if response:
            response = HtmlResponse(url=request.url,body=response,encoding='utf-8',request=request)
            return response
        return self._retry(request,exception,spider)


def get_response(request):
    ipcheck = IP_Check()
    # city = request.meta['city']
    # ips = IP(city)
    # ip = ips[0]
    # port = ips[1]
    # if 'ips' in request.meta:
    #     # ips = str(random.choice(request.meta['ips'].split(',')[:-1])).split(':')
    #     # request.meta['ip'] = ip
    #     # request.meta['port'] = port
    #     ips = random.choice(request.meta['ips'])
    #     ip = str(ips).split(':')[0]
    #     port = str(ips).split(':')[1]
    #     response = ipcheck.ip_test(url=request.url, user=request.headers['User-Agent'], ip=ip, prot=port)
    # else:
    response = ipcheck.ip_test(url=request.url, user=request.headers['User-Agent'])
    if response:
        response = HtmlResponse(url=request.url, body=response, request=request)

    else:
        response = ''
    return response