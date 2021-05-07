import os.path
import re

class SimpleMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        print(f'request路径为{request.path}')
        #  重写url 到静态 零宽负向先行断 正则表达式匹配"非"，以及"非"字符串的匹配 或者 (?<!pattern) 零宽负向后行断言 均可。
        if re.match(r'^((?!job).)+$', request.path):
            request.path = request.headers['Host'] + '/static' + request.path if request.path.startswith('/') else os.path.join(request.headers['Host'] + '/static', request.path)
        print(f'修改后request路径为{request.path}')
        response = self.get_response(request)
        # print(f'返回response 之后 {response.path}')
        # Code to be executed for each request/response after
        # the view is called.

        return response
