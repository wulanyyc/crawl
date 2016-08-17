#!/bin/env python
# -*- coding: utf-8 -*-
import urllib,urllib2,gzip,StringIO
import sys,urlparse,json
from lxml.html import parse

reload(sys)
sys.setdefaultencoding("utf-8")

class Courier:  
    def __init__(self, url, db):
        self.url = url 
        self.headers = {
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
        self.db = db

    #print table_data
    def mapDbKey(self, key):
        fields = {}
        fields['姓名'] = 'name'
        fields['手机'] = 'cellphone'
        fields['邮箱'] = 'email'
        fields['性别'] = 'sex'
        fields['身份证号'] = 'id_card_number'
        fields['快递品牌'] = 'company'
        fields['行政区域'] = 'region'
        fields['所属网点'] = 'service_place'
        
        if key in fields.keys():
            return fields[key]
        else:
            return ''

    def formatTableData(self, table_data):
        formatDict = {}
        for t in table_data:
            if len(t) >= 2:
                if type(t[0]) is unicode:
                    key = unicode.decode(t[0]).replace(':', '').encode()
                    key = self.mapDbKey(key)
                    if len(key) == 0:
                        continue
                else:
                    key = self.mapDbKey(t[0])

                if type(t[1]) is unicode:
                    val = unicode.decode(t[1]).strip()
                else:
                    val = t[1]

                formatDict[key] = val

        return formatDict

    def run(self):
        jsonDict = {
            "xzqname": "贵州-贵阳市",
            "keywords": "贵州大学",
        }

        jsonStr = json.dumps(jsonDict)

        data = {
            'method': 'courieraround',
            'json': jsonStr,
        }
        try:
            req = urllib2.Request(self.url, data, self.headers)
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if hasattr(e, 'code'):
                return e.code
            else:
                return sys.exc_info()

        compressedData = response.read()

        compressedStream=StringIO.StringIO(compressedData)
        gzipper=gzip.GzipFile(fileobj=compressedStream)
        html=gzipper.read()

        page = parse(StringIO.StringIO(html))
        print page
        sys.exit(0)

        # table table
        table = page.xpath("//table[@class='detail-table-basic']/tbody")
        table_data = list()
        for i in range(0, len(table)):
            item = table[i].findall('tr')
            for row in item:
                table_data.append([c.text for c in row.getchildren()])

        # audit status
        status = page.xpath("//span[@class='status-profile status-profile-pass']")
        if len(status) > 0:
            status = 1
        else:
            status = 0

        # id card photo
        photos = page.xpath("//img[@width='125px']")
        photo_urls = []
        for j in range(0, len(photos)):
            photo_urls.append(photos[j].get('src'))

        # output data combine
        output = self.formatTableData(table_data)

        output['audit_flag'] = status
        if len(photo_urls) >= 1:
            output['front_card_photo'] = photo_urls[0]

        if len(photo_urls) >= 2:
            output['back_card_photo'] = photo_urls[1]

        if len(photo_urls) >= 3:
            output['work_card_photo'] = photo_urls[2]

        url_info = urlparse.urlparse(self.url)
        output['third_id'] = url_info.path.split('/').pop()

        try:
            self.db.insert('third_courier', output)
            self.db.commit()
        except Exception, e:
            return sys.exc_info()

        return 'suc'

