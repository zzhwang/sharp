# 基于信息摘要算法进行数据的去重判断和存储

# 1 基于内存的存储
# 2 基于redis的存储
# 3 基于mysql的存储

import hashlib
import six

class BaseFiltet(object):
    """基于信息摘要算法进行数据的去重判断和存储"""

    def __init__(self,
                 hash_func_name='md5',
                 redis_host='localhost',
                 redis_port=6379,
                 redis_db=0,
                 redis_key='filter',
                 mysql_url=None,
                 mysql_table_name='filter'):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_key = redis_key
        self.hash_func = getattr(hashlib,hash_func_name)
        # mysql_url = mysql+pymysql://root:password@172.17.0.4:3305/data?charset=utf8
        self.mysql_url = mysql_url
        self.mysql_table_name = mysql_table_name
        self.storage = self._get_storage()


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

    def _get_hash_value(self,data):
        '''
        根据给定的数据，返回对应信息摘要hash值
        :param data:给定的原始数据（二进制类型字符串数据）
        :return:hash值
        '''
        hash_obj = self.hash_func()
        hash_obj.update(self._safe_data(data))
        hash_value = hash_obj.hexdigest()
        return hash_value

    def save(self,data):
        """
        根据data计算出对应的指纹进行存储
        :param data: 给定的原始数据（二进制类型字符串数据）
        :return:存储结果
        """
        hash_value = self._get_hash_value(data)
        self._save(hash_value)
        return hash_value

    def _save(self,hash_value):
        '''
        存储对应的hash值（交给对应的子类继承）
        :param hash_value:算出的hash值
        :return:存储结果
        '''

    def is_exists(self,data):
        '''
        判断给定数据对应的指纹是否存在
        :param data:给定的原始数据（二进制类型字符串数据）
        :return:True or False
        '''
        hash_value = self._get_hash_value(data)
        return self._is_exists(hash_value)

    def _is_exists(self,hash_value):
        '''
        判断对应的hash值（交给对应的子类）是否存在
        :param hash_value: 算出的hash值
        :return: 判断结果（True or false）
        '''
        pass

    def _get_storage(self):
        '''返回对应的存储度对象'''
        pass

