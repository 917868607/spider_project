#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2020/4/20 11:53
# software  : PyCharm

import pymysql
import datetime
# from . import *
import redis
import re
import random
import time
from DBUtils.PooledDB import PooledDB
import threadpool
import time,random
import os

"""
阿布云配置
"""


class Setting():

    # 代理隧道验证信息
    proxyUser = "***********"
    proxyPass = "************"


    """
    mysql 数据库配置
    """
    MYSQL_CHARSET = 'utf8'
    MYSQL_HOST = '*8******'
    MYSQL_USER = 'root'
    MYSQL_PAWD = '********'
    MYSQL_PORT = 3305
    MYSQL_DB = 'seo'
    # REDIS_HOST = MYSQL_HOST
    # REDIS_PORT = 6378
    # REDIS_DB = 11
    # REDIS_PASSWD = '*******'
    # DB_CHARSET="utf8"
    #mincached : 启动时开启的闲置连接数量(缺省值 0 以为着开始时不创建连接)
    DB_MIN_CACHED=10
    #maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
    DB_MAX_CACHED=10
    #maxshared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量,被请求为共享的连接将会被共享使用
    DB_MAX_SHARED=20
    #maxconnecyions : 创建连接池的最大数量(缺省值 0 代表不限制)
    DB_MAX_CONNECYIONS=1000
    #blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误<toMany......>; 其他代表阻塞直到连接数减少,连接被分配)
    DB_BLOCKING=True
    #maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
    DB_MAX_USAGE=0
    #setsession : 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]
    DB_SET_SESSION=None

    REDIS_HOST = '*********'
    REDIS_PORT = 6378
    REDIS_DB = 14
    REDIS_PASSWD = '**********'
    DB_CHARSET = "utf8"
    REDIS_PARAMS = {
        "password": "*************",
        'db': 14
    }
    redis_key_name = 'data'
    redis_error_file = 'redis_error.log'
    redis_pop_num = 1000
    mysql_filter_names = ['id']
    mysql_error_file = 'mysql_error.log'
    mysql_table_jinpin_dbname = 'jinpin'
    mysql_table_tubatu_dbname = 'spider_tubatu'
    mysql_table_qijia_dbname = 'spider_qijia'







'''
@功能：PT数据库连接池
'''
class PTConnectionPool(object):
    __pool = None

    def __enter__(self):
        self.conn = self.getConn()
        self.cursor = self.conn.cursor()
        print("PT数据库创建con和cursor")
        return self

    def getConn(self,setting=Setting()):
        if self.__pool is None:
            self.__pool = PooledDB(creator=pymysql, mincached=setting.DB_MIN_CACHED , maxcached=setting.DB_MAX_CACHED,
                                   maxshared=setting.DB_MAX_SHARED, maxconnections=setting.DB_MAX_CONNECYIONS,
                                   blocking=setting.DB_BLOCKING, maxusage=setting.DB_MAX_USAGE,
                                   setsession=setting.DB_SET_SESSION,
                                   host=setting.MYSQL_HOST , port=setting.MYSQL_PORT ,
                                   user=setting.MYSQL_USER , passwd=setting.MYSQL_PAWD ,
                                   db=setting.MYSQL_DB , use_unicode=False, charset=setting.MYSQL_CHARSET)
        return self.__pool.connection()

    """
    @summary: 释放连接池资源
    """
    def __exit__(self, type=None, value=None, trace=None):
        self.cursor.close()
        self.conn.close()
        print("PT连接池释放con和cursor")
'''
@功能：获取PT数据库连接
'''
def getPTConnection():
    return PTConnectionPool()
