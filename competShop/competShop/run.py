#!/usr/bin/env Python
#-*-coding:utf-8-*-

# author    :Guido.shu
# datetime  :2020/4/8 11:07
# software  : PyCharm

#-*-coding:utf-8-*-
from scrapy import cmdline
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# cmdline.execute(['scrapy','crawl','chengyang'])
# cmdline.execute(['scrapy','crawl','jingpin'])
# cmdline.execute(['scrapy','crawl','duoleshi'])
# cmdline.execute(['scrapy','crawl','huarunqi'])
################开启全部爬虫################
cmdline.execute(['scrapy','crawlall'])

#'E:\ENVS\py3spiderENV\Lib\site-packages\scrapy\core\downloader\middleware.py'
# 'usr\local\lib\python3.6\dis-packages\scrapy\spiders\__init__.py'