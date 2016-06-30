#!/bin/env python
# -*- coding: utf-8 -*-
import urllib,urllib2,gzip,StringIO
import sys,urlparse
from lxml.html import parse
sys.path.append('./../libs/')
import dbhelper

reload(sys)
sys.setdefaultencoding( "utf-8" )

url = 'http://ucms.sudiyi.cn/admin/couriers/59'
headers = {
    'Host': 'ucms.sudiyi.cn',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'http://ucms.sudiyi.cn/admin/couriers',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Cookie': 'sudiyi.cas=BAh7DkkiD3Nlc3Npb25faWQGOgZFVEkiRTEyMzEwMzY5NzJlNjEzYjYzYzgx%0AMzcxOTA0ZDIyZmQ5NTg5ZjU5OGFmMzUwMTc2MDRiYTE1OWQ2Yzk0MzU2OTUG%0AOwBGSSIIdWlkBjsARmkDoZcESSIJbmFtZQY7AEZJIg7mnY7pu47mmI4GOwBU%0ASSINdXNlcm5hbWUGOwBGSSIJbGlsbQY7AFRJIgt0aWNrZXQGOwBGSSIlNzhj%0AZDAyNDE2YjEwMTUwOWE2ZTNjMzRhNDQ0YzQzZjkGOwBGSSILYXZhdGFyBjsA%0ARkkiNWh0dHBzOi8vaG9tZS5zdWRpeWkuY24vdXBsb2FkL2F2YXRhci9kZWZh%0AdWx0LnBuZwY7AFRJIg1tb2RfbGlzdAY7AEZbCnsJOgdpZGkGOgluYW1lSSIT%0AdXNlcl9jZW50ZXJfbXMGOwBUOgxuYW1lX3poSSIX55So5oi3566h55CG57O7%0A57ufBjsAVDoIdXJsSSIaaHR0cDovL3VjbXMuc3VkaXlpLmNuBjsAVHsJOwZp%0ABzsHSSIQc3VkaXlpX2VwbXMGOwBUOwhJIhfkurrlkZjnrqHnkIbns7vnu58G%0AOwBUOwlJIhpodHRwOi8vZXBtcy5zdWRpeWkuY24GOwBUewk7BmkIOwdJIhVz%0AdWRpeWlfb3BlcmF0aW9uBjsAVDsISSIX6L%2BQ57u0566h55CG57O757ufBjsA%0AVDsJSSIZaHR0cDovL29tcy5zdWRpeWkuY24GOwBUewk7BmkJOwdJIhNzdWRp%0AeWlfYm1zX3dlYgY7AFQ7CEkiF%2BS4muWKoeeuoeeQhuezu%2Be7nwY7AFQ7CUki%0AGWh0dHA6Ly9ibXMuc3VkaXlpLmNuBjsAVHsJOwZpCjsHSSIPc3VkaXlpX3Zt%0AcwY7AFQ7CEkiF%2BeJiOacrOeuoeeQhuezu%2Be7nwY7AFQ7CUkiGWh0dHA6Ly92%0AbXMuc3VkaXlpLmNuBjsAVEkiCmZsYXNoBjsARnsASSINcm9sZV9pZHMGOwBG%0AWwZpaA%3D%3D%0A--01a86d4fb030f92f6ef9beab41890974bedf2d41',
}

try:
    data = None
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
except urllib2.URLError, e:
    if hasattr(e, 'code'):
        print e.code

sys.exit(0)

compressedData = response.read()

compressedStream=StringIO.StringIO(compressedData)
gzipper=gzip.GzipFile(fileobj=compressedStream)
data=gzipper.read()

compressedStream=StringIO.StringIO(compressedData)
gzipper=gzip.GzipFile(fileobj=compressedStream)
html=gzipper.read()
#print data

#print StringIO.StringIO(data)
#page = parse("courier.html")

# main info
page = parse(StringIO.StringIO(html))
table = page.xpath("//table[@class='detail-table-basic']/tbody")
#print len(rows)

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
#print photos[j].get('src')

#print table_data
def mapDbKey(key):
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

def formatTableData(table_data):
    formatDict = {}
    for t in table_data:
        if len(t) >= 2:
            if type(t[0]) is unicode:
                key = unicode.decode(t[0]).replace(':', '').encode()
                key = mapDbKey(key)
                if len(key) == 0:
                    continue
            else:
                key = mapDbKey(t[0])

            if type(t[1]) is unicode:
                val = unicode.decode(t[1]).strip()
            else:
                val = t[1]

            formatDict[key] = val

    return formatDict

dict = formatTableData(table_data)
dict['audit_flag'] = status
if len(photo_urls) >= 1:
    dict['front_card_photo'] = photo_urls[0]

if len(photo_urls) >= 2:
    dict['back_card_photo'] = photo_urls[1]

if len(photo_urls) >= 3:
    dict['work_card_photo'] = photo_urls[2]

url_info = urlparse.urlparse(url)
dict['third_id'] = url_info.path.split('/').pop()
# print dict

db = dbhelper.get_mysql()
db.insert('third_courier', dict)
db.commit()
db.close()
