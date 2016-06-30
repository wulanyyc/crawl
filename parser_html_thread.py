#!/bin/env python
import Queue
import threading
from HTMLParser import HTMLParser
import ConfigParser
import sys
import json
import time
from PIL import Image
from cStringIO import StringIO
from urllib import urlopen
import MySQLdb
import dbhelper
import logging
import logging.config
 
logging.config.fileConfig("/data/rss/conf/log.conf")
logger = logging.getLogger("root")

reload(sys)
sys.setdefaultencoding( "utf-8" )

queue = Queue.Queue()

class ThreadUrl(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        
    def run(self):
        while True:
            item_start_time = time.time() 
            #grabs host from queue
            id, content = self.queue.get()

            self.parser(id, content)
            use_time = time.time() - item_start_time
            self.insert_log(id, use_time, 'ok');
            
            #signals to queue job is done
            self.queue.task_done()
            
    def parser(self, id, content):
        if len(content) > 0:
            db = dbhelper.get_mysql()
            
            img_list, strip_content_list = self.parser_content(id, content)
            imgs_json = json.dumps(img_list)
            
            content_str = "".join(strip_content_list)
            date = time.strftime('%Y-%m-%d')
            
            update_data = {}
            update_data['imgs_json'] = imgs_json
            update_data['strip_content'] = content_str
            update_data['parse_flag'] = 1
            update_data['createdate'] = date
            where = "id=" + str(id)
            db.update('feed_content', update_data, where)
            db.commit()
            db.close()
    
    def parser_content(self, id, content):
        parser = MyHTMLParser()
        parser.feed(content)
        imgs_json = []      
        for img in parser.img_list:
            temp = {}
            if len(img) == 0:
                continue
            try:
                data = StringIO(urlopen(img).read())
                im = Image.open(data)
                x,y = im.size
                if x > 100 and y > 100:
                    temp['width'] = x 
                    temp['height'] = y 
                    temp['src'] = img 
                    imgs_json.append(temp)
            except:
                self.insert_log(id, 0, 'fail')
        content_list = parser.strip_content_list
        
        return imgs_json, content_list
    
    def insert_log(self, id, time, status):
        db = dbhelper.get_mysql()
        data = {}
        data['job_id'] = id
        data['job_name'] = 'parse'
        data['time'] = time
        data['status'] = status
        db.insert('feed_log', data)
        db.commit()
        db.close()

            
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.img_list = []
        self.strip_content_list = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            for attr in attrs:
                if attr[0] == 'src' and len(attr[1]) > 0:
                    self.img_list.append(attr[1])

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        self.strip_content_list.append(data.strip())


def main():
    start = time.time()
    #spawn a pool of threads, and pass them queue instance
    for i in range(5):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()
    #populate queue with data 
    db = dbhelper.get_mysql()
    sql = "select content,id from feed_content where parse_flag = 0"
    data = list(db.queryAll(sql))
    
    logger.info( 'parse total num:' + str(len(data)) )
    for item in data:
        queue.put((item['id'], item['content']), False, 1)
    #wait on the queue until everything has been processed
    queue.join()
    date = time.strftime('%Y-%m-%d')
    logger.info( 'parse thread total date:' +date+ ' time:' + str(time.time() - start) )

#if __name__ == '__main__':
#    try:
#        main()
#    except:
#        print sys.exc_info()

try:
    main()
except:
    print sys.exc_info()
    
