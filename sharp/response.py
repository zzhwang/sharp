import re
from lxml import etree
from bs4 import BeautifulSoup

'''
构造的响应对象
'''

class Response(object):
    def __init__(self,request,status_code,url,headers,body):
        self.request = request
        self.status_code = status_code
        self.url = url
        self.headers = headers
        self.body = body

    def lxml(self,rule):
        html = etree.HTML(self.body)
        return html.xpath(rule)

    def select(self,rule):
        soup = BeautifulSoup(self.body,'lxml')
        return soup.select(rule)

    def re_match(self,rule):
        return re.match(rule,self.body)

    def re_search(self,rule):
        return re.search(rule,self.body)

    def re_findall(self,rule):
        return re.findall(rule,self.body)

    def re_sub(self,rule,text):
        return re.sub(rule,self.body,text)