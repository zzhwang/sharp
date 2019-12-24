class RequestManger(object):
    def __init__(
            self,
            log,
            queue_type='fifo',
            filter_type='redis',
            queue_kwargs={},
            filter_kwargs={}
    ):
        self.log = log

        self._filters = {}  # {过滤器名称：过滤对象}
        self._queues = {}   # {请求队列名称：请求队列对象}

        self._filter_kwargs = filter_kwargs
        self._queues_kwargs = queue_kwargs

        self.filter_cls = self._set_filter_cls(filter_type)
        self.queue_cls = self._set_queue_cls(queue_type)

    def _set_filter_cls(self,filter_type):
        from .utils.filter_class import get_redis_queue_cls
        return get_redis_queue_cls(filter_type)

    def _set_queue_cls(self,queue_type):
        from sharp.request_manager.utils.redis_tools import get_redis_queue_cls
        return get_redis_queue_cls(queue_type)

    def _get_request_filter(self,filter_name):
        # 如果过滤器名在_filters的字典里 返回过滤器对象
        if filter_name in self._filters:
            return self._filters[filter_name]
        else:
            # 创建 请求过滤对象
            from .request_filter import RequestFilter
            self._filter_kwargs['redis_key'] = filter_name
            self._filter_kwargs['mysql_table_name'] = filter_name
            filter_obj = self.filter_cls(**self._filter_kwargs)
            request_filter = RequestFilter(filter_obj)

            # 构造 self._filters
            self._filters[filter_name] = request_filter
            return request_filter

    def _get_request_queue(self,queue_name):
        # 如果过滤器名在__queues的字典里 返回请求对象
        if queue_name in self._queues:
            return self._queues[queue_name]
        else:
            # 构造请求队列对象
            queue_obj = self.queue_cls(name=queue_name)
            self._queues[queue_name] = queue_obj
            return queue_obj

    def add_request(self,request_obj,queue_name,filter_name=None):
        # 判断是否为元组
        if isinstance(request_obj,tuple):
            # 元组 请求对象
            priority,request = request_obj
        else:
            priority = None
            request = request_obj

        # 是否有过滤队列的名字
        if filter_name is None:
            filter_name = 'filter_' + queue_name

        # 过滤队列 请求队列
        request_filter = self._get_request_filter(filter_name)
        request_queue = self._get_request_queue(queue_name)

        # 请求对象是否存在
        if request_filter.is_exist(request):
            self.log.logger.warn('发现重复请求:{}'.format(request.url))
        else:
            # 标记过滤请求
            fp = request_filter.mark_request(request)
            request.id = fp

            if priority is None:
                request_queue.put(request)
            else:
                request_queue.put(priority,request)
            self.log.logger.info('添加请求:{}'.format(request.url))

    def get_request(self,queue_name,block=True):
        request_queue = self._get_request_queue(queue_name)
        request = request_queue.get(block=block)
        return request



