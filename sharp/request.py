from urllib.parse import urlparse,parse_qsl,urlencode

'''
构造的请求对象
'''

class Request(object):
    def __init__(self,url,method='get',query={},body={},cookie={},meta={},name='porject_name',headers=None,id=None):
        '''
        :param url: url
        :param method: 默认 get
        :param query: dict
        :param body: dict
        :param name: 所属项目名称
        :param headers: 请求头
        :param meta: 向内传入参数
        :param id: 请求对象指纹 唯一ID
        '''
        self.url = url
        self.method = method

        if not isinstance(query,dict):
            raise Exception('query is only dict')
        self.query = query

        if not isinstance(body,dict):
            raise Exception('body is only dict')
        self.body = body

        if not isinstance(cookie,dict):
            raise Exception('cookie is only dict')
        self.cookie = cookie

        if not isinstance(meta,dict):
            raise Exception('item is only dict')
        self.meta = meta

        self.name = name # 传入参数

        self.headers = headers

        self.id = id  # 请求对象指纹

    # 转属性
    @property
    def url_with_query(self):
        '''query dict merge to request url'''
        url = self.url
        _ = urlparse(url)

        url_without_query = _.scheme + '://' + _.netloc + _.path + _.params
        url_query = parse_qsl(_.query)
        url_fragment = _.fragment

        all_query = sorted(set(list(self.query) + url_query))

        return url_without_query + '?' + urlencode(all_query) + url_fragment
