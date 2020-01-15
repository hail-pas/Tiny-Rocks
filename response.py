import json

from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.pagination import PageNumberPagination
from utils import AESUtil
ERR_MSG_DICT = {
    "status_code": 'Message',
}


class JSONResponse(JsonResponse):
    def __init__(self, data=None, msg=None, encoder=DjangoJSONEncoder, safe=False,
                 json_dumps_params=None, **kwargs):
        status = kwargs.get('status') or 200
        ret = {
            'code': status,
        }
        if status == 200:
            if data is not None:
                ret['data'] = data
        else:
            err = ERR_MSG_DICT.get(int(status))
            if msg:
                msg = '{}'.format(msg)
            else:
                msg = err
            ret['msg'] = msg
        super(JSONResponse, self).__init__(ret, encoder=encoder, safe=safe,
                                           json_dumps_params=json_dumps_params, **kwargs)


class AESJsonResponse(HttpResponse):
    def __init__(self, data=None, msg=None, *args, **kwargs):
        status = kwargs.get('status') or 200
        ret = {
            'code': status,
        }
        if status != 200:
            err = ERR_MSG_DICT.get(int(status))
            if msg:
                msg = '{}'.format(msg)
            else:
                msg = err
            ret['msg'] = msg
        if data is not None:
            ret['data'] = data
        content = json.dumps(ret, cls=DjangoJSONEncoder, ensure_ascii=False, )
        if not settings.DEBUG:
            content = AESUtil().encrypt_data(content)
            super(AESJsonResponse, self).__init__(content=content, *args,
                                                  **kwargs)
        else:
            super(AESJsonResponse, self).__init__(content=content, content_type='application/json', *args,
                                                  **kwargs)


class PageNumberSizePagination(PageNumberPagination):
    page_size_query_param = 'num'
