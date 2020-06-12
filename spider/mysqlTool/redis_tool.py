import datetime
import random
import re
import time
from threading import Thread
import redis
from conf import Setting


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


class Pipline_to_redis_server(object):

    def __init__(self,settings=Setting):
        self.settings = settings
        if settings.REDIS_PASSWD:
            pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT,password=settings.REDIS_PASSWD,db=settings.REDIS_DB)
        else:
            pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        self._r = redis.StrictRedis(connection_pool=pool)
        self.time = datetime.datetime.now().strftime('%Y%m%d')

    @async
    def sadd(self,data_s:dict):

        redis_key_name = list(data_s.keys())[0]
        redis_sql = 'sadd %s ' % redis_key_name
        for data in data_s[redis_key_name]:
            data_str = re.sub('\s','',str(data))
            redis_sql += data_str + ' '
        while 1:
            try:
                self._r.execute_command(redis_sql)
                print('#######redis保存成功＃{}＃＃＃＃＃＃＃＃＃'.format(redis_sql))
                break
            except:
                print('#######redis保存失败＃{}＃＃＃＃＃＃＃＃＃'.format(redis_sql))
                time.sleep(random.randint(2,3))
                with open(self.settings.redis_error_file,'a')as f:
                    f.write(str(data_s)+ '\n')