# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import xlwt
import datetime
from twisted.enterprise import adbapi
import pymysql
from pymysql import cursors
from .untils.mysql_connect import *
from .io_servers import *


class CompetshopPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlSpiderPipeline(object):
    def __init__(self,db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls,settings):
        db_params = dict(
            host = settings['MYSQL_HOST'],
            user = settings['MYSQL_USER'],
            password = settings['MYSQL_PAWD'],
            port = settings['MYSQL_PORT'],
            db = settings['MYSQL_DB'],
            charset = settings['MYSQL_CHARSET'],
            use_unicode = True,
            cursorclass = cursors.DictCursor)
        db_pool = adbapi.ConnectionPool('pymysql',**db_params)
        return cls(db_pool)
    def process_item(self,item,spider):

        query = self.db_pool.runInteraction(self.insert_item,item)
        # query.addErrback(self.handle_error,item,spider)
        return item
    def handle_error(self, failure, item, spider):
        # 输出错误原因
        print(failure)
    # def process_item(self,item,spider):
    #     with getPTConnection() as db:
    #         self.insert_item(db.cursor,item)
    #     return item
    def insert_item(self,cursor,item):
        item.insert_mysql(cursor)


class SuningBookPipeline(object):

    def __init__(self):
        self.redis_server = Pipline_to_redis_server()

    def process_item(self,item, spider):
        datas = item['data']
        self.redis_server.sadd(datas)