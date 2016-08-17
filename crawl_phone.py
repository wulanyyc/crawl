#-*- coding:utf-8 –*-
import urllib,urllib2,gzip,StringIO
import sys,json,os,ConfigParser,time
from lxml.html import parse

sys.path.append('./libs/')
import mysql

reload(sys)
sys.setdefaultencoding( "utf-8" )

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

def getDetailInfo(guid, url, headers):
    jsonDict = {
        "guid": guid,
    }

    jsonStr = json.dumps(jsonDict)
    data = {
        'method': 'courierdetail',
        'json': jsonStr,
    }

    data = urllib.urlencode(data)

    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    compressedData = response.read()

    compressedStream=StringIO.StringIO(compressedData)
    gzipper=gzip.GzipFile(fileobj=compressedStream)
    resData=gzipper.read()
    return resData

def checkTaskNum():
    db = getMysql()
    sql = "select count(*) as num from kuaidi100_task where task_flag = 0"
    taskResult = db.queryRow(sql)

    task = 0
    if len(taskResult) > 0:
        task = taskResult[0]

    return task

def main():
    while checkTaskNum() > 0:
        url = 'http://www.kuaidi100.com/courier/searchapi.do'
        headers = {
            'Host': 'www.kuaidi100.com',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'http://www.kuaidi100.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'http://www.kuaidi100.com/courier/search.jsp',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',      
            'X-Requested-With': 'XMLHttpRequest',             
            'Cookie': '__gads=ID=e1804ad3b9b2f4fb:T=1471256036:S=ALNI_MYlAaADwLk1yKPiMKC-RTV-wd64Lg; JSESSIONID=CA4015886B5A177866068AE32CFEF9A9; Hm_lvt_22ea01af58ba2be0fec7c11b25e88e6c=1471256027,1471407188; Hm_lpvt_22ea01af58ba2be0fec7c11b25e88e6c=1471407188',
        }

        db = getMysql()
        sql = "select id, province,city,search from kuaidi100_task where task_flag = 0 order by id asc limit 1"
        result = db.queryRow(sql)

        if len(result) == 0:
            sys.exit(0)
        else:
            db.update('kuaidi100_task', {'task_flag': 1}, 'id=' + str(result[0]))
            db.commit()

        #print type(result)
        #sys.exit(0)

        jsonDict = {
            "xzqname": result[1] + "-" + result[2],
            "keywords": result[3],
        }

        jsonStr = json.dumps(jsonDict)
        data = {
            'method': 'courieraround',
            'json': jsonStr,
        }

        data = urllib.urlencode(data)

        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        compressedData = response.read()

        compressedStream=StringIO.StringIO(compressedData)
        gzipper=gzip.GzipFile(fileobj=compressedStream)
        resData=gzipper.read()

        resData = json.loads(resData)
        status = resData['status']

        if status == 200:
            coList = resData['coList']
            for item in coList:
                guid =  item['guid']
                detail = getDetailInfo(guid, url, headers)
                detailList = json.loads(detail)
                status = detailList['status']
                if status == 200:
                    courier = detailList['courier']

                    record = {}
                    record['name'] = courier['courierName']
                    record['guid'] = courier['guid']
                    record['phone'] = courier['courierTel']
                    record['company'] = courier['companyName']
                    record['search_text'] = jsonDict['keywords']
                    record['detail'] = detail

                    db = getMysql()
                    db.insert('kuaidi100_courier', record)
                    db.commit()
                time.sleep(1)

try:
    main()
except:
    print sys.exc_info()
