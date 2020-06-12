#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2019/5/20 10:32
# software  : PyCharm

import random
import time
from urllib import request
from  competShop.settings import *
import pymysql as mysql

class Mysql(object):
    def __init__(self, config):
        if config:
            self.__config = config

    def __connect_db(self):
        try:
            return mysql.connect(**self.__config)
        except Exception as e:
            print(e)

    def quer_select_db(self, condition):
        con = self.__connect_db()
        if con:
            cur = con.cursor(mysql.cursors.DictCursor)
            try:
                if type(()) == type(condition):
                    p = cur.execute(condition[0])
                else:
                    cur.execute(condition)
                    # print(condition[0])
                rows = cur.fetchall()
                cur.close()
                con.close()
                assert len(rows) != 0, '错误：数据不存在'  # assert断言
                return rows
            except Exception as e:
                print(e)
                return ''
        else:
            return None

def IP(cityID):
    connect = {
        'host': '47.101.166.145',
        'port': 3305,
        'user': 'root',
        'passwd': 'q4tOun8lAqGBdtUN',
        'db': 'seo',
        'charset': 'utf8'
    }
    sql = Mysql(config=connect)
    condition = ("SELECT ip,port FROM zhimaip where cityID = {} ORDER BY RAND() LIMIT 1".format(cityID))
    rows = sql.quer_select_db(condition)
    if rows:
        # ipnum = rows[0]
        ipnum = {"ip":"112.64.52.113","port":'4275'}
    else:
        ipnum = ''
    return ipnum

def ip_params(ip, prot):
    if not ip:
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"
        # proxyHost = ip
        # proxyPort = prot
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host" : proxyHost,
            "port" : proxyPort,
            "user" : PROXYUSER,
            "pass" : PROXYPAWD,
        }
        proxy_handler = request.ProxyHandler({
            "http"  : proxyMeta,
            "https" : proxyMeta,
        })
        return proxy_handler
    else:
        proxyHost = ip + ":" + prot

        proxies = request.ProxyHandler({
            "https": 'https://' + proxyHost,
        })
        return proxies

class IP_Check():
    def __init__(self):
        self.count = 0

    def ip_test(self,url,user, ip=None, prot=None):
        header = {}
        header['User-Agent'] = user
        proxy_handler = ip_params(ip, prot)
        opener = request.build_opener(proxy_handler)
        request.install_opener(opener)
        req = request.Request(url,headers=header)
        try:
            resp = request.urlopen(req,timeout=2)
            # res = resp.read()
            # try:
            response = resp.read()
            # with open('sss.html','w') as f:
            #     f.write( str(response, encoding="utf-8"))
                # response = response.decode()
            # except Exception as e:
            #     print(e)
            # print (resp)
            # print(type(response))
        except Exception as e:
            print('运行错误{}'.format(e))
            self.count += 1
            if self.count < 20:
                time.sleep(random.randint(1,4))
                response = self.ip_test(url=url,user=user,ip=ip, prot=prot)
            else:
                self.count = 0
                response = ''
        return response