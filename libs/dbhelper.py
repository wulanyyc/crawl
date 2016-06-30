#!/usr/local/bin/python
import mysql
import ConfigParser
import os

def get_mysql():
    cwd = os.getcwd()
    config = ConfigParser.ConfigParser()
    config.read("/Users/yangyuncai/test/crawl/config/global.conf")
    host = config.get("db", "host")
    port = config.get("db", "port")
    user = config.get("db", "user")
    password = config.get("db", "password")
    database = config.get("db", "database")

    db = mysql.MySQL(host, port, user, password)
    db.selectDb(database)
    return db

