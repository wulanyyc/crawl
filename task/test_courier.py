import urllib,urllib2,gzip,StringIO
import sys
from lxml.html import parse

reload(sys)
sys.setdefaultencoding( "utf-8" )

url = 'http://ucms.sudiyi.cn/admin/couriers'
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

data = None
req = urllib2.Request(url, data, headers)
response = urllib2.urlopen(req)
compressedData = response.read()
#print compressedData

compressedStream=StringIO.StringIO(compressedData)
gzipper=gzip.GzipFile(fileobj=compressedStream)
data=gzipper.read()
#print data

#print StringIO.StringIO(data)
#page = parse("courier.html")
page = parse(StringIO.StringIO(data))
rows = page.xpath("//table[@id='datatable']/tbody")[0].findall('tr')
table_data = list()
for row in rows:
    table_data.append([c.text for c in row.getchildren()])

print table_data
