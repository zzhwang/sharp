from .base import BaseRedisQueue
import pickle

'''
桟
'''

class LifoResisQueue(BaseRedisQueue):

    def get_nowait(self):
        ret = self.redis.rpop(self.name)
        if ret is None:
            raise self.Empty
        return pickle.loads(ret)