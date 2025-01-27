from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import time
# 白名单，表示请求里面的路由时不验证登录信息
API_WHITELIST = ["/","/api/login"]

def check_token(token):
    if len(token)==32:
        return True
    return False


class AuthorizeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        #print(request.path)
        if request.path  not in API_WHITELIST:
            token = request.META.get('HTTP_TOKEN')
            try:
                if check_token(token):
                    print(token)
            except:
                return JsonResponse({'msg':'The Request has no token'})
            '''
            else:
                return JsonResponse({'error': 666,'msg': "登录信息错误或已过期"})
            '''