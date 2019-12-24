'''
change from pyspider pyspider/pyspider/message_queue/redis_queue.py
'''

import time
import redis
import pickle
from six.moves import queue as BaseQueue


class BaseRedisQueue(object):
    """
    A Queue like message built over redis
    """

    Empty = BaseQueue.Empty
    Full = BaseQueue.Full
    max_timeout = 0.3

    def __init__(self, name, host='localhost', port=6379, db=0,
                 maxsize=0, lazy_limit=True, password=None, cluster_nodes=None,lock=None,use_lock=False,redis_lock_config={}):
        """
        Constructor for RedisQueue
        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: redis queue is shared via instance, a lazy size limit is used
                    for better performance.
        redis_lock_config {lock_name,host='localhost',port=6379,db=0}
        """
        self.name = name
        if(cluster_nodes is not None):
            from rediscluster import StrictRedisCluster
            self.redis = StrictRedisCluster(startup_nodes=cluster_nodes)
        else:
            self.redis = redis.StrictRedis(host=host, port=port, db=db, password=password)
        self.maxsize = maxsize
        self.lazy_limit = lazy_limit
        self.last_qsize = 0
        self.lock = lock
        self.use_lock = use_lock
        self.redis_lock_config = redis_lock_config

    def qsize(self):
        self.last_qsize = self.redis.llen(self.name)
        return self.last_qsize

    def empty(self):
        if self.qsize() == 0:
            return True
        else:
            return False

    def full(self):
        if self.maxsize and self.qsize() >= self.maxsize:
            return True
        else:
            return False

    def put_nowait(self, obj):
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        self.last_qsize = self.redis.rpush(self.name, pickle.dumps(obj))
        return True

    def put(self, obj, block=True, timeout=None):
        if not block:
            return self.put_nowait(obj)

        start_time = time.time()
        while True:
            try:
                return self.put_nowait(obj)
            except self.Full:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

    def get_nowait(self):
        ret = self.redis.lpop(self.name)
        if ret is None:
            raise self.Empty
        return pickle.loads(ret)

    def get(self, block=True, timeout=None):
        if not block:
            return self.get_nowait()

        start_time = time.time()
        while True:
            try:
                return self.get_nowait()
            except self.Empty:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)
