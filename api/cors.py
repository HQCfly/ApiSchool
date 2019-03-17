from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response


class MiddlewareMixin:
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class CORSMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # 添加响应头

        # 允许你的域名来获取我的数据
        # response['Access-Control-Allow-Origin'] = "*"


        # 允许你携带Content-Type
        # response['Access-Control-Request-Headers'] = "Content-Type"


        # 允许你发送delete,put
        # response['Access-Control-Request-Method'] = "GET,POST"
        response['Access-Control-Allow-Origin'] = "*"

        if request.method == "OPTIONS":
            response['Access-Control-Allow-Headers'] = "Content-Type"
            response['Access-Control-Allow-Methods'] = "PUT,DELETE"

        return response
