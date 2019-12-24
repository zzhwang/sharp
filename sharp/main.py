from sharp.request_manager.utils.redis_tools import get_redis_queue_cls
from sharp.downloader import AsyncTornadoDownloader,RequestsDownloader,ChromeHeadlessDownloader
from sharp.request import Request
from sharp.request_manager import RequestManger
from sharp.request_wactcher import RequestWatcher
from sharp.logger import Loggers
import asyncio
import tornado.ioloop
from threading import Thread

'''待过滤队列类型:默认fifio'''
FIFO_QUEUE = get_redis_queue_cls('fifo')

class Master(object):
    def __init__(self,spiders,request_manger_config,project_name):
        # 日志
        self.log = Loggers(level='info')
        # 待过滤的队列
        self.filter_queue = FIFO_QUEUE(project_name+'_fifo',
                                       host=request_manger_config['queue_kwargs']['host'],
                                       port=request_manger_config['queue_kwargs']['port'],
                                       db=0)
        # 请求管理
        self.request_manger = RequestManger(self.log,**request_manger_config)
        # 包含的爬虫
        self.spiders = spiders
        # 项目名字
        self.project_name = project_name

    def run_start_requests(self):
        # spiders {spider_1.name:spider_1,spider_2.name:spider_2}
        # 遍历所有爬虫对象
        for spider in self.spiders.values():
            # 所有初始 构造的请求对象
            for request in spider().start_requests():
                # 有初始请求
                if request is not None:
                    # 待过滤的队列添加 请求对象
                    self.filter_queue.put(request)
                    self.log.logger.info('添加待过滤请求：{}'.format(request.url))

    def run_filter_queue(self):
        while True:
            # 待过滤的队列取出 请求对象
            request = self.filter_queue.get()
            # 请求管理添加 请求对象
            self.request_manger.add_request(request,queue_name=self.project_name)

    def run(self):
        # 线程并发
        Thread(target=self.run_start_requests).start()
        Thread(target=self.run_filter_queue).start()

class Slave(object):
    def __init__(self,spiders,request_manger_config,project_name,downlodaer=AsyncTornadoDownloader()):
        # 日志
        self.log = Loggers(level='info')
        # 待过滤的队列
        self.filter_queue = FIFO_QUEUE(project_name+'_fifo',
                                       host=request_manger_config['queue_kwargs']['host'],
                                       port=request_manger_config['queue_kwargs']['port'],
                                       db=0)
        # 请求管理
        self.request_manger = RequestManger(self.log,**request_manger_config)
        # 请求监视
        self.request_watcher = RequestWatcher(host=request_manger_config['queue_kwargs']['host'],
                                              port=request_manger_config['queue_kwargs']['port'],
                                              db=0)
        # 项目名字
        self.project_name = project_name
        # 自身所有爬虫
        self.spiders = spiders
        # 自身下载器
        self.downlodaer = downlodaer

    async def handel_request(self):
        # 获取当前的事件循环
        ioloop = tornado.ioloop.IOLoop.current()
        # 任务放入线程池执行
        # 请求管理得到请求
        future = ioloop.run_in_executor(None,self.request_manger.get_request,self.project_name)
        request = await future
        # 放入请求中（redis hash 对象）
        self.request_watcher.mark_processing_requests(request)

        # 请求成功 丢失则保存请求中
        try:
            self.log.logger.info('发送请求：{}'.format(request.url))
            response = await self.downlodaer.fetch(request)
            # 通过request.name 找到对应的爬虫
            spider = self.spiders[request.name]()

            # 遍历爬虫解析的数据
            for result in spider.parse(response):
                if result is None:
                    raise Exception('NOT RETURN NONE')
                # 返回Request对象
                # 任务放入线程池执行（待过滤队列添加新的请求）
                elif isinstance(result, Request):
                    await ioloop.run_in_executor(None,self.filter_queue.put,result)
                # 返回解析数据
                # 数据保存
                else:
                    new_result = spider.data_clean(result)
                    await ioloop.run_in_executor(None, spider.data_save, new_result)
        # 请求失败
        except Exception as e:
            # 标记失败请求（加入redis hash 失败对象）
            self.log.logger.error('{}'.format(e))
            self.request_watcher.mark_fail_requests(request,str(e))
            raise

        finally:
            # 将进行中的request删除
            self.log.logger.info('请求删除:{}'.format(request.url))
            self.request_watcher.unmark_processing_requests(request)

    async def run(self):
        while True:
            # 并发16个任务
            await asyncio.wait(
                [(self.handel_request()) for i in range(16)]
            )

class Engine(object):
    '''启动器'''
    def start(self,task):
        if isinstance(task, Master):
            # 主端启动
            task.run()
        elif isinstance(task, Slave):
            # 从端启动
            ioloop = tornado.ioloop.IOLoop.current()
            ioloop.run_sync(task.run)
        else:
            raise Exception('must task class is Master or Slave')
