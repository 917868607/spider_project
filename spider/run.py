
import os
import multiprocessing
import datetime
from multiprocessing import Manager



os_path = os.getcwd()
path = os_path + '/run_spider'
res = os.listdir(path)
print(res)
jobs = []

def run_start(x):
    log_name = datetime.datetime.now().strftime('%Y%m%d')+"--" + x[:-3]
    linux_params = 'python {pro}  >  {path}/{log}.log 2>&1 &'.format(pro=path+'/'+x,log=log_name,path=os_path+'/log')
    os.system(linux_params)


if __name__ == '__main__':
    print('######################爬虫店铺定时开始＃＃＃＃＃＃＃＃＃＃＃＃＃')
    for x in range(len(res)):
        p = multiprocessing.Process(target=run_start,args=(res[x],))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join(timeout=5)
    print('######################爬虫店铺定时结束＃＃＃＃＃＃＃＃＃＃＃＃＃')