from django.http import HttpResponse

def api_auth(func):
    def inner(request, *args, **kwargs):
        response = HttpResponse()
        response.status_code = 666
        response.content = "超时，禁止访问"
        return response

    #return func(request, *args, **kwargs)
    return inner