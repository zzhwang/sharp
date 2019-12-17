import requests
from Spidersystem.response import Response
from tornado.httpclient import HTTPClient,HTTPRequest,AsyncHTTPClient

'''
基于request tornado 构造的下载器
'''

class RequestsDownloader(object):
    def fetch(self,request):
        '''downloader:requst'''
        if request.method.upper() == 'GET':
            resp = requests.get(url=request.url_with_query,headers=request.headers)
        elif request.method.upper() == 'POST':
            resp = requests.post(url=request.url_with_query,headers=request.headers,body=request.body)
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

