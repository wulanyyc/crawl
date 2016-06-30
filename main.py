#!/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import redis
import ConfigParser
import re
import logging
import Queue
import threading
import time

sys.path.append('./task/')
sys.path.append('./libs/')
import mysql
import courier

def getMysql():
    cwd = os.getcwd()
    config = ConfigParser.ConfigParser()
    config.read(cwd + "/config/global.conf")

    # db
    db_host = config.get("db", "host")
    db_port = config.get("db", "port")
    db_user = config.get("db", "user")
    db_password = config.get("db", "password")
    db_database = config.get("db", "database")

    resource_db = mysql.MySQL(db_host, db_port, db_user, db_password)
    resource_db.selectDb(db_database)

    return resource_db

class ThreadCrawl(threading.Thread):
    def __init__(self, queue, db):
        threading.Thread.__init__(self)
        self.queue = queue
        self.db = db
        
    def run(self):
        while True:
            #grab info from queue
            url = self.queue.get()

            if re.match('http://ucms.sudiyi.cn/admin/couriers/[1-9][0-9]*', url):
                try:
                    self.db.conn.ping()
                except Exception, e:
                    self.db = getMysql()

                crawl  = courier.Courier(url, self.db)
                ret = crawl.run()
                if ret != 'suc':
                    # print ret
                    if ret != 404:
                        resource_redis.lpush(channel, url)
                    logging.info(url + ':' + str(ret))
                else:
                    logging.info(url + ':' + ret)
            #signals to queue job is done
            self.queue.task_done()
            time.sleep(0.1)

if __name__ == '__main__':
    cwd = os.getcwd()
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename= cwd + '/logs/run.log',
        filemode='w')

    config = ConfigParser.ConfigParser()
    config.read(cwd + "/config/global.conf")

    # redis
    redis_host = config.get("redis", "host")
    redis_port = config.get("redis", "port")
    redis_db   = config.get("redis", "db")

    # crawl
    channel = config.get("crawl", "channel")

    # resource init
    resource_redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    resource_db    = getMysql()

    # resource_db.query('set interactive_timeout=24*3600');

    # while 1:
    #     msg = resource_redis.brpop(channel, 2)
    #     if type(msg) is tuple:
    #         url = msg[1]
    #         if re.match('http://ucms.sudiyi.cn/admin/couriers/[1-9][0-9]*', url):
    #             crawl  = courier.Courier(url, resource_db)
    #             ret = crawl.run()
    #             if ret != 'suc':
    #                 resource_redis.lpush(channel, url)
    #                 logging.info(url + ':' + ret)
    #             else:
    #                 logging.info(url + ':' + ret)

    #spawn a pool of threads, and pass them queue instance
    queue = Queue.Queue()
    for i in range(5):
        t = ThreadCrawl(queue, resource_db)
        t.setDaemon(True)
        t.start()

    while True:
        msg = resource_redis.brpop(channel, 1)
        if type(msg) is tuple:
            url = msg[1]
            queue.put((url), False, 1)
        time.sleep(0.1)

    #wait on the queue until everything has been processed
    queue.join()
    resource_db.close()
    print 'queue end'

