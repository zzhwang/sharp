from .base import BaseRedisQueue
import pickle

class PriorityRedisQueue(BaseRedisQueue):
    '''
    优先级redis队列
    redis_lock_config {lock_name,host='localhost',port=6379,db=0}
    '''

    def qsize(self):
        '''
        得到数据大小
        :return: 数据大小
        '''
        self.last_qsize = self.redis.zcard(self.name)
        return self.last_qsize

    def put_nowait(self, obj):
        # 与最大尺寸对比
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        # 已满
        elif self.full():
            raise self.Full
        # 添加
        self.last_qsize = self.redis.zadd(self.name, {pickle.dumps(obj[0]),obj[1]})
        return True

    def get_nowait(self):
        # 是否用锁
        if self.use_lock:
            from .redis_lock import RedisLock
            # 无 构建锁对象
            if self.lock is None:
                # redis_lock_config {lock_name,host='localhost',port=6379,db=0}
                self.lock = RedisLock(**self.redis_lock_config)
            # 加锁
            if self.lock.acquire_lock():
                # 取最大值数据
                ret = self.redis.zrange(self.name, -1, -1)
                if ret is None:
                    raise self.Empty
                self.redis.zrem(ret[0])
                # 释放锁
                self.lock.relase_lock()
                # 返回数据
                return pickle.loads(ret[0])

        # # 取最大值数据
        ret = self.redis.zrange(self.name,-1,-1)
        if ret is None:
            raise self.Empty
        self.redis.zrem(ret[0])
        return pickle.loads(ret[0])

