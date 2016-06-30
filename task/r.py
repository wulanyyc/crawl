# -*- coding: utf-8 -*-
import redis
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("/Users/yangyuncai/test/crawl/config/global.conf")
config_host = config.get("redis", "host")
config_port = config.get("redis", "port")
config_db   = config.get("redis", "db")

r = redis.Redis(host=config_host, port=config_port, db=config_db)
#info = r.info() 
#for key in info: 
#    print "%s: %s" % (key, info[key])

#r.lpush('crawl_urls', 'http://www.baidu.com')
while 1:
    url = r.brpop('crawl_urls', 5)
    print url
