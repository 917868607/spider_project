import ast
import datetime
import random
import re
import time

import pymysql
import redis
from DBUtils.PooledDB import PooledDB

class Setting():
    MYSQL_HOST = '***********'
    MYSQL_USER = '***'
    MYSQL_PAWD = '********'
    MYSQL_PORT = 3305
    MYSQL_DB = 'seo'
    MYSQL_CHARSET = 'utf8'
    # mincached : 启动时开启的闲置连接数量(缺省值 0 以为着开始时不创建连接)
    DB_MIN_CACHED = 10
    # maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
    DB_MAX_CACHED = 10
    # maxshared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量,被请求为共享的连接将会被共享使用
    DB_MAX_SHARED = 20
    # maxconnecyions : 创建连接池的最大数量(缺省值 0 代表不限制)
    DB_MAX_CONNECYIONS = 1000
    # blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误<toMany......>; 其他代表阻塞直到连接数减少,连接被分配)
    DB_BLOCKING = True
    # maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
    DB_MAX_USAGE = 0
    # setsession : 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]
    DB_SET_SESSION = None
    REDIS_HOST = '***********'
    REDIS_PORT = 6378
    REDIS_DB = 14
    REDIS_PASSWD = '*********'
    DB_CHARSET = "utf8"
    REDIS_PARAMS = {
        "password": "********",
        'db': 14
    }
    redis_key_name = 'data'
    redis_error_file = 'redis_error.log'
    redis_pop_num = 10
    mysql_filter_names = ['id']
    mysql_table_name = 'jinpin'
    mysql_error_file = 'mysql_error.log'



'''
@功能：PT数据库连接池
'''
class PTConnectionPool(object):
    __pool = None

    def __init__(self,settins=Setting()):
        self.setting = settins

    def __enter__(self):
        self.conn = self.getConn()
        self.cursor = self.conn.cursor()
        print("PT数据库创建con和cursor")
        return self

    def getConn(self):
        if self.__pool is None:
            self.__pool = PooledDB(creator=pymysql, mincached=self.setting.DB_MIN_CACHED , maxcached=self.setting.DB_MAX_CACHED,
                                   maxshared=self.setting.DB_MAX_SHARED, maxconnections=self.setting.DB_MAX_CONNECYIONS,
                                   blocking=self.setting.DB_BLOCKING, maxusage=self.setting.DB_MAX_USAGE,
                                   setsession=self.setting.DB_SET_SESSION,
                                   host=self.setting.MYSQL_HOST , port=self.setting.MYSQL_PORT ,
                                   user=self.setting.MYSQL_USER , passwd=self.setting.MYSQL_PAWD ,
                                   db=self.setting.MYSQL_DB , use_unicode=False, charset=self.setting.MYSQL_CHARSET)
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




class Pipline_to_redis_server(object):

    def __init__(self,settings=Setting):
        self.settings = settings
        if settings.REDIS_PASSWD:
            pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT,password=settings.REDIS_PASSWD,db=settings.REDIS_DB)
        else:
            pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        self._r = redis.StrictRedis(connection_pool=pool)
        self.time = datetime.datetime.now().strftime('%Y%m%d')

    def sadd(self,data_s:list):
        # redis_sql = 'sadd %s '%self.settings.redis_key_name
        redis_sql = ''
        for data in data_s:
            data_str = re.sub('\s','',str(data))
            redis_sql += data_str + ','
        while 1:
            try:
                # self._r.execute_command(redis_sql)
                self._r.sadd(self.settings.redis_key_name,redis_sql)
                break
            except:
                print('#######redis保存失败＃{}＃＃＃＃＃＃＃＃＃'.format(redis_sql))
                time.sleep(random.randint(2,3))
                with open(self.settings.redis_error_file,'a')as f:
                    f.write(str(data_s)+ '\n')


class Redis_to_mysql_server(object):

    def __init__(self,setting=Setting(),redis_pip=Pipline_to_redis_server()):
        self.settings = setting
        if setting.REDIS_PASSWD:
            pool = redis.ConnectionPool(host=setting.REDIS_HOST, port=setting.REDIS_PORT,
                                        password=setting.REDIS_PASSWD, db=setting.REDIS_DB)
        else:
            pool = redis.ConnectionPool(host=setting.REDIS_HOST, port=setting.REDIS_PORT)
        self._r = redis.StrictRedis(connection_pool=pool)
        self.settings = setting
        with getPTConnection() as cs:
            cs.cursor.execute('show columns from %s'% self.settings.mysql_table_name)
        table_data_s = cs.cursor.fetchall()
        self.column_name_s = []
        for table_data in table_data_s:
            column_name = str(table_data[0],encoding='utf-8')
            if column_name not in self.settings.mysql_filter_names:
                self.column_name_s.append(column_name)

    def run(self):
        sql_params = 'insert into %s (%s) values '%(self.settings.mysql_table_name,','.join(self.column_name_s))
        while 1:
            # sss = 'spop "{}" {}'.format(self.settings.redis_key_name,self.settings.redis_pop_num)
            # self.data_s = self._r.execute_command(sss)
            self.data_s = self._r.spop(self.settings.redis_key_name)
            if self.data_s:
                total_value = ''
                data_s_params = '[' + self.data_s.decode('utf-8').replace(" ",",") + ']'
                ssss = ast.literal_eval(data_s_params)
                for redis_data in ssss:
                    # sss = str(redis_data,encoding='utf-8')
                    # data_dic = ast.literal_eval(redis_data)
                    data_dic = redis_data
                    single_value = ''
                    for column_name in self.column_name_s:
                        if column_name in data_dic.keys():
                            single_value += '"{}",' .format(str(data_dic[column_name]).replace('"',''))
                        else:
                            single_value += '"",'
                    total_value += '({}),' .format(single_value[0:-1])
                sql_insert = sql_params + total_value[0:-1]
                while 1:
                        try:
                            with getPTConnection() as db:
                                print(sql_insert)
                                db.cursor.execute(sql_insert)
                                db.conn.commit()
                                break
                        except Exception as e:
                            print(e)
                            import time
                            time.sleep(2)
                            with open(self.settings.mysql_error_file,'a') as f:
                                f.write(str(redis_data) + '\n')

            else:
                pass


if __name__ == '__main__':
    mysql_save = Redis_to_mysql_server()
    mysql_save.run()