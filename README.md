# SpiderSystem
基于async tornado redis 实现的分布式爬虫 

  主端 数据待爬取队列，过滤队列，请求队列，请求中队列，请求失败队列
  
  从端 任务异步爬取，任务进行中进入请求中，失败进入请求失败。任务结束：未发出的进入请求中队列

# 使用
##### 列子 template.py

### 导入
from Spidersystem.main import Master,Slave,Engine

from Spidersystem.request import Request

from Spidersystem.spider import BaseSpider

# 配置项目名字，reids配置

  项目名字

  PROJECT_NAME = 'test'

  请求管理配置（redis）

  REQUEST_MANAGER_CONFIG = {

    'queue_type': 'fifo',  # 请求队列的类型
    
    'queue_kwargs': {'host': '127.0.0.1', 'port': '6379'},  # 请求队列配置
    
    'filter_type': 'redis',  # 过滤队列的类型
    
    'filter_kwargs': {'redis_key': 'test', 'redis_host': '127.0.0.1'}  # 过滤队列的配置
    
}
  
  #### 请求中与请求失败采用redis hash结构 地址：默认采用请求管理的queue_kwargs参数
  
# 构建爬虫

##### 继承BaseSpider


    class BaiduSpider(BaseSpider):
    
        '''爬虫名字'''
        name = 'baidu'
    
        def start_requests(self):
            '''初次请求，构建Request对象'''
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'Cookie': 'PSTM=1576555259; BAIDUID=1DFEF2BDFB0386C4AE59070135DBE4CD:FG=1; delPer=0; BD_CK_SAM=1; PSINO=2; BD_UPN=123253; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BIDUPSID=F4AD87BBEFEBDBEAAD6C413280F9944A; H_PS_PSSID=1454_21115_30211_22158; COOKIE_SESSION=11_0_4_5_5_0_0_0_4_0_0_0_6234_0_0_0_1576491897_0_1576555271%7C5%230_0_1576555271%7C1; H_PS_645EC=e385t8SeKpA%2BBIhr%2FecbLOXsoRcWJlnl9IzbzUaq7qOO2%2FOB1yZqA9uh3xA'
            }
    
            yield Request('http://www.baidu.com/',headers=headers,name=self.name)
            yield Request('https://www.baidu.com/s?wd=tornado4',headers=headers,name=self.name)
            yield Request('https://www.baidu.com/s?wd=tornado8',headers=headers,name=self.name)
            yield Request('https://www.google.com/search?q=f&oq=f&aqs=chrome..69i57j69i60l3j69i61j69i60.795j0j8&sourceid=chrome&ie=UTF-8',headers=headers,name=self.name)
    
        def parse(self, response):
            '''解析数据，返回数据或构建的Request对象'''
            print(response)
            print(response.url)
            print(response.body)
    
            yield response.body
    
        def data_clean(self, data):
            '''数据清洗，提交到data_save'''
            return data
    
        def data_save(self,data):
            '''数据保存'''
            pass
        
# 启动任务
Sleave端执行任务依据 spider.name 去执行解析，储存逻辑。

## 爬虫任务
spiders = {BaiduSpider.name:BaiduSpider}
# 主端启动
master = Master(spiders, project_name=PROJECT_NAME, request_manger_config=REQUEST_MANAGER_CONFIG)
Engine().start(master)
# 从端启动
slave = Slave(spiders, project_name=PROJECT_NAME, request_manger_config=REQUEST_MANAGER_CONFIG)
Engine().start(slave)

  
