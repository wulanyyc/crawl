#-*- coding:utf-8 –*-
import urllib,urllib2,gzip,StringIO
import sys,json
from lxml.html import parse

reload(sys)
sys.setdefaultencoding( "utf-8" )

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

jsonDict = {
    "xzqname": "贵州-贵阳市",
    "keywords": "贵州大学",
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
#print resData
#sys.exit(0)

resData = json.loads(resData)
status = resData['status']

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


if status == 200:
    coList = resData['coList']
    for item in coList:
        guid =  item['guid']
        detail = getDetailInfo(guid, url, headers)
#print detail
        detailList = json.loads(detail)
#print detailList
#print type(detailList)
#print detailList['status']
        status = detailList['status']
        if status == 200:
            courier = detailList['courier']
            guid = courier['courierName']
            phone = courier['courierTel']
            print phone
        sys.exit(0)
