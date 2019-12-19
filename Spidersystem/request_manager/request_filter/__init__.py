from urllib.parse import urlparse,parse_qsl,urlencode

class RequestFilter(object):
    def __init__(self,filter_obj):
        self.filter_obj = filter_obj # 过滤对象

    def is_exist(self,request_obj):
        '''
        判断是否存在
        :param request_obj: 请求对象
        :return: True or False
        '''
        data = self.get_request_filter_data(request_obj)
        return self.filter_obj.is_exists(data)

    def mark_request(self,request_obj):
        '''
        标记已请求
        :param request_obj: 请求对象
        '''
        data = self.get_request_filter_data(request_obj)
        fp = self.filter_obj.save(data)
        return fp

    def get_request_filter_data(self,request_obj):
        '''
        得到请求过滤数据
        :param request_obj: 请求数据
        :return: 请求对象属性转换的url
        '''
        url = request_obj.url
        method = request_obj.method
        query = request_obj.query
        body = request_obj.body

        _ = urlparse(url)
        url_without_query = _.scheme + '://' + _.netloc + _.path + _.params
        url_query = parse_qsl(_.query)
        url_fragment = _.fragment
        all_query = sorted(set(list(query) + url_query))
        storage_url = url_without_query + '?' + urlencode(all_query) + url_fragment

        storage_body = ''
        list_body = sorted(body.items(),key=lambda x:x[1])
        for i in list_body:
            storage_body += i[0]
            storage_body += i[1]

        return storage_url + method + storage_body
