#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2020/4/20 10:13
# software  : PyCharm

"""
阿布云代理设置

"""

import requests
from urllib import request
from conf import *
from conf import Setting

proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = Setting.proxyUser
proxyPass = Setting.proxyPass


class AbuyunSpider(object):


    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host" : proxyHost,
        "port" : proxyPort,
        "user" : proxyUser,
        "pass" : proxyPass,
    }
    proxies = {
        "http"  : proxyMeta,
        "https" : proxyMeta,
    }
    proxyHandler = request.ProxyHandler({
        "http": proxyMeta,
        "https": proxyMeta,
    })

    #todo:返回requests的proxies
    @classmethod
    def returnRequestProxies(cls):
        return cls.proxies


    #todo：urllib request的proxies
    @classmethod
    def returnUrllibRequestProxies(cls):
        """
        构造urllib 的代理IP
        :return: urllib 的request
        response = request(url).read()
        """
        opener = request.build_opener(cls.proxyHandler)
        request.install_opener(opener)

        return request