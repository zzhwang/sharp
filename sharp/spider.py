from sharp.request import Request

'''
基类爬虫
'''

class BaseSpider(object):

    # 爬虫的名字
    name = 'demo'

    def start_requests(self):
        '''
        初始请求
        :yield: Request对象
        '''
        yield

    def parse(self,response):
        '''
        解析数据
        :param response: 响应对象
        :yield: Request对象or解析数据 不能无返回
        '''
        yield


    def data_clean(self,data):
        '''
        数据清洗
        :param data: 数据
        :return: 清洗的数据
        '''
        return data

    def data_save(self,data):
        '''
        数据保存
        :param data:
        :return:
        '''
        pass