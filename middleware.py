import datetime
import time
import jwt
from django.http import QueryDict

from response import AESJsonResponse
from utils import verify_sign, overwrite_request, RedisUtil


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.method == 'PUT':
            request.PUT = QueryDict(request.body).dict()
        elif request.method == 'DELETE':
            request.DELETE = QueryDict(request.body).dict()
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response


class SignAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        method = request.method
        m = getattr(request, method, None)
        if m:
            uaid = m.get('uaid')
            if uaid:
                try:
                    app = App.objects.get(uaid=uaid)
                    request.app = app
                except App.DoesNotExist:
                    pass
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        app_name = request.resolver_match.app_name
        if app_name in [apps.DgzConfig.name]:
            if getattr(view_func, 'sign_exempt', False):
                return
            if request.method in getattr(view_func.view_class, 'sign_exempt_methods', []):
                return
        else:
            return
        params = dict(QueryDict(request.body).dict(), **request.GET.dict())
        timestamp = params.get('timestamp')  # type:str
        if '/api/pay/' in request.path_info:
            key = request.app.pay_key
        else:
            key = settings.PRIVATE_KEY
        if not timestamp or not timestamp.isdigit():
            return AESJsonResponse(status=415, msg='timestamp required')
        if int(time.time()) - int(timestamp) > 3600:
            return AESJsonResponse(status=412, msg='请检查设备时间')
        if not verify_sign(params, key):
            return AESJsonResponse(status=412, msg='sign incorrect')
        overwrite_request(request)


class JwtAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        app_name = request.resolver_match.app_name
        key = settings.SECRET_KEY
        token = request.META.get('HTTP_AUTHORIZATION')
        if app_name in ['dgz']:
            if getattr(view_func, 'jwt_exempt', False):
                return
            if request.method in getattr(view_func.view_class, 'jwt_exempt_methods', []) and not token:
                return
        else:
            return
        try:
            decoded = jwt.decode(token, key, algorithms='HS256')
            user_id = decoded.get('user_id')
            app = getattr(request, 'app', None)
            if app:
                user = get_object_or_404(User, pk=user_id, app=app)
                uaid = app.uaid
            else:
                user = get_object_or_404(User, pk=user_id)
                uaid = user.app.uaid
            request.user = user
            request.user.is_active = True
            request.user.is_authenticated = True
            # 统计实时在线人数
            now = int(datetime.datetime.now().timestamp())
            RedisUtil.conn.zadd(cache.ONLINE_USERS_KEYS.format(uaid=uaid), {user_id: now})
            if request.path == reverse('api:receive_task') and request.method == 'POST':
                # 统计实时在线做任务人数
                now = int(datetime.datetime.now().timestamp())
                RedisUtil.conn.zadd(cache.ONLINE_TASK_USERS_KEYS.format(uaid=uaid), {user_id: now})
        except jwt.PyJWTError as e:
            return AESJsonResponse(status=401, msg='登录已过期')
