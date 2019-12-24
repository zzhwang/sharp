from sharp.main import Master,Slave,Engine
from sharp.request import Request
from sharp.spider import BaseSpider

# 项目名字
PROJECT_NAME = 'test'

# 请求管理配置
REQUEST_MANAGER_CONFIG = {
    'queue_type': 'fifo',  # 请求队列的类型
    'queue_kwargs': {'host': '127.0.0.1', 'port': '6379'},  # 请求队列配置
    'filter_type': 'redis',  # 过滤队列的类型
    'filter_kwargs': {'redis_key': 'test', 'redis_host': '127.0.0.1'}  # 过滤队列的配置
}

# 爬虫
'''继承BaseSpider'''
class BaiduSpider(BaseSpider):

    '''爬虫名字'''
    name = 'baidu'

    def start_requests(self):
        '''初次请求，构建Request对象'''
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Cookie': 'PSTM=1576555259; BAIDUID=1DFEF2BDFB0386C4AE59070135DBE4CD:FG=1; delPer=0; BD_CK_SAM=1; PSINO=2; BD_UPN=123253; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BIDUPSID=F4AD87BBEFEBDBEAAD6C413280F9944A; H_PS_PSSID=1454_21115_30211_22158; COOKIE_SESSION=11_0_4_5_5_0_0_0_4_0_0_0_6234_0_0_0_1576491897_0_1576555271%7C5%230_0_1576555271%7C1; H_PS_645EC=e385t8SeKpA%2BBIhr%2FecbLOXsoRcWJlnl9IzbzUaq7qOO2%2FOB1yZqA9uh3xA'
        }

        yield Request('http://www.baidu.com/',headers=headers,name=self.name,meta=headers)
        yield Request('https://www.baidu.com/s?wd=tornado4',headers=headers,name=self.name,meta=headers)
        yield Request('https://www.baidu.com/s?wd=tornado8',headers=headers,name=self.name,meta=headers)
        yield Request('https://www.google.com/search?q=f&oq=f&aqs=chrome..69i57j69i60l3j69i61j69i60.795j0j8&sourceid=chrome&ie=UTF-8',headers=headers,name=self.name,meta=headers)

    def parse(self, response):
        '''解析数据，返回数据或构建的Request对象'''
        print(response)
        print(response.url)
        print(response.body)

        yield response.body

        hrefs = response.lxml('//@href')
        for href in hrefs:
            print(href)
            yield Request(href,headers=response.request.meta,name=BaiduSpiderLink.name)

    def data_clean(self, data):
        '''数据清洗，提交到data_save'''
        return data

    def data_save(self,data):
        '''数据保存'''
        pass

class BaiduSpiderLink(BaseSpider):
    '''爬虫名字'''
    name = 'baidu_link'

    def parse(self, response):
        '''解析数据，返回数据或构建的Request对象'''
        print(response.body)
        yield response.body

    def data_clean(self, data):
        '''数据清洗，提交到data_save'''
        return data

    def data_save(self,data):
        '''数据保存'''
        pass

if __name__ == '__main__':

    spiders = {
        # 第一层
        BaiduSpider.name:BaiduSpider,
        # 第二层
        BaiduSpiderLink.name:BaiduSpiderLink
    }

    master = Master(spiders, project_name=PROJECT_NAME, request_manger_config=REQUEST_MANAGER_CONFIG)
    Engine().start(master)

    slave = Slave(spiders, project_name=PROJECT_NAME, request_manger_config=REQUEST_MANAGER_CONFIG)
    Engine().start(slave)
