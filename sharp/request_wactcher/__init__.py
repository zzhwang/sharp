import redis
import json

# 请求监视着
class RequestWatcher(object):
    '''请求监视，redis——hash'''
    def __init__(self,host,port,db):
        self.redis_client = redis.StrictRedis(host=host,port=port,db=db)

    def json_serializer(self,request,error=None):
        '''转json字符串'''
        _ = {
            "url": request.url,
            "method": request.method,
            "query": request.query,
            "body": request.body,
            "name": request.name,
            "headers": request.headers,
            "id": request.id,
            "error":error
        }
        return json.dumps(_)

    def mark_processing_requests(self, request):
        '''标记正在请求'''
        self.redis_client.hset('processing_requests', request.id,self.json_serializer(request))

    def unmark_processing_requests(self, request):
        '''取消标记请求'''
        self.redis_client.hdel('processing_requests', request.id)

    def mark_fail_requests(self, request, error):
        '''标记失败'''
        self.redis_client.hset('faile_requests', request.id, self.json_serializer(request,error))