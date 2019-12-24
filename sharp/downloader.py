import asyncio
import requests
from functools import partial
import tornado.ioloop
from sharp.response import Response
from tornado.httpclient import HTTPClient,HTTPRequest,AsyncHTTPClient
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

'''
基于request tornado 构造的下载器
'''

class RequestsDownloader(object):
    async def fetch(self,request):
        '''downloader:requst'''
        ioloop = tornado.ioloop.IOLoop.current()
        if request.method.upper() == 'GET':
            # 构建partial对象，字典传入
            partial_obj = partial(requests.get, url=request.url_with_query, headers=request.headers)
            resp = await ioloop.run_in_executor(None,partial_obj)
        elif request.method.upper() == 'POST':
            partial_obj = partial(requests.get, url=request.url_with_query,headers=request.headers,body=request.body)
            resp = await ioloop.run_in_executor(None, partial_obj)
        else:
            raise Exception('only support GET or POST')
        return Response(request,status_code=resp.status_code,url=resp.url,headers=resp.headers,body=resp.content)

class TornadoDownloader(object):
    def __init__(self):
        self.httpclint = HTTPClient()

    def fetch(self,request):
        tornado_request = HTTPRequest(request.url_with_query,method=request.method.upper(),headers=request.headers)
        tornado_response = self.httpclint.fetch(tornado_request)
        return Response(request=request,status_code=tornado_response.code,url=tornado_response.effective_url,headers=tornado_response.headers,body=tornado_response.buffer.read())

    def __del__(self):
        self.httpclint.close()

class AsyncTornadoDownloader(object):
    '''
    异步tornado下载器
    '''
    def __init__(self):
        self.async_http_clint = AsyncHTTPClient()

    async def fetch(self,request):
        tornado_request = HTTPRequest(request.url_with_query,
                                      method=request.method.upper(),
                                      headers=request.headers,
                                      validate_cert=False)

        tornado_response = await self.async_http_clint.fetch(tornado_request)

        return Response(request=request,
                        status_code=tornado_response.code,
                        url=tornado_response.effective_url,
                        headers=tornado_response.headers,
                        body=tornado_response.buffer.read())

class ChromeHeadlessDownloader(object):

    def __init__(self, max=3, add_optons={}, hub=False, hub_url=None):
        '''
        队列构建chrome请求池
        :param max: 最大浏览器个数
        :param add_optons: chrome添加配置
        :param hub: 是否 selenium-hub 启动 推荐 selenium——hub集群
        :param hub_url: hub 地址
        '''
        if not isinstance(add_optons,dict):
            raise Exception('add_optons type must dict')
        self.options = self._config_options(add_optons)

        if hub == True:
            self.driver_pool = [self._get_hub_driver(hub_url) for i in range(max)]
        else:
            self.driver_pool = [self._get_driver() for i in range(max)]

    def _config_options(self,add_optons):
        '''
        构建options 并添加配置
        :param add_optons: 添加配置参数
        :return: options
        '''
        options = webdriver.ChromeOptions()
        # 添加 无头
        options.add_argument('--headless')
        for value in add_optons.values():
            options.add_argument(value)
        return options

    def _get_hub_driver(self,hub_url):
        '''得到 hub chrome ,需要 docker启动selenium_hub or 安装jar包启动'''
        driver = webdriver.Remote(command_executor=hub_url,desired_capabilities=DesiredCapabilities,options=self.options)
        return driver

    def _get_driver(self):
        driver = webdriver.Chrome(options=self.options)
        return driver

    def _fetch(self, request, driver):
        '''chrome请求'''
        driver.get(request.url_with_query)
        return Response(
            request=request,
            status_code=200,
            url=driver.current_url,
            headers=driver.get_cookies(),
            body=driver.page_source
        )

    async def fetch(self,request):
        '''异步请求'''
        while True:
            if len(self.driver_pool) >= 1:
                driver = self.driver_pool.pop()
                break
            await asyncio.sleep(0.5)

        ioloop = tornado.ioloop.IOLoop.current()

        try:
            response = await ioloop.run_in_executor(None,self._fetch,request,driver)
        except:
            raise
        finally:
            self.driver_pool.append(driver)

        return response

    def __del__(self):
        '''销毁chrome'''
        for driver in self.driver_pool:
            driver.quit()


