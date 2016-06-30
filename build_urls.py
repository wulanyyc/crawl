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

if __name__ == '__main__':
    cwd = os.getcwd()
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

    for i in range(1, 200):
        resource_redis.lpush(channel, "http://ucms.sudiyi.cn/admin/couriers/" + str(i))
