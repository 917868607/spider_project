# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompetshopItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


#todo：竞品店铺
class JinPIn(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    area = scrapy.Field()
    numbers = scrapy.Field()
    telphone = scrapy.Field()
    types = scrapy.Field()
    db_name = 'jingpin'

    def insert_mysql(self, cursor):
        sql = 'insert into {}(' \
              'name,' \
              'address,' \
              'province,' \
              'city,' \
              'area,' \
              'numbers,' \
              'telphone,' \
              'types) values(%s,%s,%s,%s,%s,%s,%s,%s)'.format(self.db_name)
        params = (
            self['name'],
            self['address'],
            self['province'],
            self['city'],
            self['area'],
            self['numbers'],
            self['telphone'], self['types']
        )
        try:
            cursor.execute(sql, params)
            print('##################存入数据成功##########{}'.format(params))
        except Exception as e:
            print(e)
            print(sql)
            print('竞品店铺错误的sql,参数{}'.format(params))



class jinPinItem(scrapy.Item):
    pass