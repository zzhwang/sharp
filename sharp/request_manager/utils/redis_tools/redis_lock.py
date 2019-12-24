import redis
import pickle
import time

class RedisLock(object):
    '''
    Redis LOCK
    '''
    def __init__(self,lock_name,host='localhost',port=6379,db=0):
        self.redis = redis.StrictRedis(host=host, port=port, db=db)
        self.lock_name = lock_name

    def _get_thread_id(self):
        '''
        构造唯一ID
        :return: 唯一id
        '''
        import socket
        import os
        import threading

        # 主机名 + 进程号 + 线程id
        thread_id = socket.gethostname() + str(os.getpid()) + threading.current_thread().name
        return thread_id

    def acquire_lock(self,thread_id=None,block=True,expire=10):
        '''
        设置锁
        :param thread_id: 唯一ID
        :param block: 阻塞
        :param expire: 过期时间
        :return:
        '''

        # 得到线程id
        if thread_id is None:
            thread_id = self._get_thread_id()

        # 阻塞
        while block:
            # 设置 redis字符串对象值（无可设置锁名，序列化id）
            ret = self.redis.setnx(self.lock_name,pickle.dumps(thread_id))
            if ret == 1:
                print('sucess lock')
                self.redis.expire(self.lock_name,expire)
                return True
            time.sleep(0.001)

        # 非阻塞
        ret = self.redis.setnx(self.lock_name, pickle.dumps(thread_id))
        if ret == 1:
            print('sucess lock')
            return True
        else:
            print('fail lock')
            return False

    def relase_lock(self,thread_id=None):
        '''
        释放锁
        :param thread_id: 唯一ID
        :return: True or False
        '''
        if thread_id is None:
            thread_id = self._get_thread_id()

        # 取出字符串对象 锁名与自身唯一ID对应
        ret = self.redis.get(self.lock_name)
        if pickle.loads(ret) == thread_id:
            # 释放锁
            self.redis.delete(self.lock_name)
            print('sucess relaease lock')
            return True
        else:
            print('faile relaease lock')
            return False

