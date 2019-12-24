# bollm 过滤器
import hashlib
import six
import redis

class Hash_Engine(object):
    def __init__(self,hash_func_name='md5',hash_k = [1,2,3]):
        self.hash_func = getattr(hashlib,hash_func_name)
        self.hash_k = hash_k

    def get_hash_valuse(self,data):
        '''得到hash值'''
        self._safe_data(data)
        hash_values = []
        for k in self.hash_k:
            self.hash_func().update(str(k).encode())
            self.hash_func().update(data.encode())
            hash_value = int(self.hash_func().hexdigest(),16)
            hash_values.append(hash_value)
        return hash_values

    def _safe_data(self,data):
        '''
        :param data: 给定的原始数据
        :return: 二进制类型的字符串
        '''
        if six.PY3:
            if isinstance(data,bytes):
                return data
            elif isinstance(data,str):
                return data.encode()
            else:
                raise Exception("Please into str or bytes")
        else:
            if isinstance(data,str):
                return data
            elif isinstance(data,unicode):
                return data.encode()
            else:
                raise Exception("Please into str or unicode")

class BloomFilter(object):
    def __init__(self,
                 redis_host='localhost',
                 redis_port=6379,
                 redis_db=0,
                 redis_key='bool_filer',
                 *args,
                 **kwargs):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_key = redis_key
        self.storage = self._get_storage()
        self.hash_engine = Hash_Engine()

    def _get_storage(self):
        '''返回一个redis连接对象'''
        pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        client = redis.StrictRedis(connection_pool=pool)
        return client

    def save(self,data):
        '''
        保存hash映射
        :param data: 存储值
        :return:
        '''
        offset_values = self._get_offset_value(data)
        for offset_value in offset_values:
            self.storage.setbit(self.redis_key,offset=offset_value,value=1)

    def is_exist(self,data):
        '''
        判断值是否存在
        :param data: 判断存储值
        :return: 有 返回False  无 返回 True
        '''
        offset_values = self._get_offset_value(data)
        for offset_value in offset_values:
            v = self.storage.getbit(self.redis_key,offset=offset_value)
            if v == 0:
                return False
        return True

    def _get_offset_value(self,data):
        '''
        计算偏移值
        :param data: 存储值
        :return: 偏移量
        '''
        # 512 * 2 ** 10 * 2 ** 10 * 2 ** 8
        offset = 512 * 2 ** 10 * 2 ** 10 * 2 ** 8
        hash_values = self.hash_engine.get_hash_valuse(data)
        offset_values = []
        for hash_value in hash_values:
            offset_values.append(offset // hash_value)
        return offset_values



