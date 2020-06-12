# -*- coding: utf-8 -*-
from competShop.settings import *
import pymysql
from DBUtils.PooledDB import PooledDB
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

    def getConn(self):
        if self.__pool is None:
            self.__pool = PooledDB(creator=pymysql, mincached=DB_MIN_CACHED , maxcached=DB_MAX_CACHED,
                                   maxshared=DB_MAX_SHARED, maxconnections=DB_MAX_CONNECYIONS,
                                   blocking=DB_BLOCKING, maxusage=DB_MAX_USAGE,
                                   setsession=DB_SET_SESSION,
                                   host=MYSQL_HOST , port=MYSQL_PORT ,
                                   user=MYSQL_USER , passwd=MYSQL_PAWD ,
                                   db=MYSQL_DB , use_unicode=False, charset=MYSQL_CHARSET)
        return self.__pool.connection()

    """
    @summary: 释放连接池资源
    """
    def __exit__(self, type, value, trace):
        self.cursor.close()
        self.conn.close()
        print("PT连接池释放con和cursor")
'''
@功能：获取PT数据库连接
'''
def getPTConnection():
    return PTConnectionPool()