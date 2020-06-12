#!/usr/bin/env Python
#-*-coding:utf-8-*-
import ast
import datetime
import multiprocessing
import random

import redis
from conf import Setting, getPTConnection
from mysqlTool.redis_tool import async


class Redis_to_mysql_server(object):

    def __init__(self,db_name,setting=Setting()):
        self.settings = setting
        self.db_name = db_name
        if setting.REDIS_PASSWD:
            pool = redis.ConnectionPool(host=setting.REDIS_HOST, port=setting.REDIS_PORT,
                                        password=setting.REDIS_PASSWD, db=setting.REDIS_DB)
        else:
            pool = redis.ConnectionPool(host=setting.REDIS_HOST, port=setting.REDIS_PORT)
        self._r = redis.StrictRedis(connection_pool=pool)
        self.settings = setting
        with getPTConnection() as cs:
            cs.cursor.execute('show columns from %s'% self.db_name)
        table_data_s = cs.cursor.fetchall()
        self.column_name_s = []
        for table_data in table_data_s:
            column_name = str(table_data[0],encoding='utf-8')
            if column_name not in self.settings.mysql_filter_names:
                self.column_name_s.append(column_name)

    def run(self):
        now = datetime.datetime.now().strftime('%Y%m%d')
        sql_params = 'insert into %s (%s) values '%(self.db_name,','.join(self.column_name_s))
        while 1:
            self.data_s = self._r.spop(self.db_name,self.settings.redis_pop_num)
            if self.data_s:
                total_value = ''
                for redis_data in self.data_s:
                    sss = str(redis_data,encoding='utf-8')
                    data_dic = ast.literal_eval(sss)
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
                print('等待获取redis值＃＃＃＃＃＃＃＃＃＃＃')
                import time as ti
                ti.sleep(random.randint(2,3))
                next_now = datetime.datetime.now().strftime('%Y%m%d')
                if int(next_now) - int(now) >= 1:
                    print('########################监听结束＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃')
                    break


if __name__ == '__main__':
    print('##############################redi缓存mysql数据库开始＃＃＃＃＃＃＃＃＃＃＃')
    setting = Setting()
    params_list = [setting.mysql_table_jinpin_dbname,setting.mysql_table_qijia_dbname,setting.mysql_table_tubatu_dbname]
    for x in params_list:
        mysql_save = Redis_to_mysql_server(db_name=x)
        mysql_save.run()
    jobs = []
    for x in range(len(params_list)):
        mysql_save = Redis_to_mysql_server(db_name=params_list[x])
        p = multiprocessing.Process(target=mysql_save.run)
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join(timeout=5)
    print('##############################redi缓存mysql数据库结束＃＃＃＃＃＃＃＃＃＃＃')