import base64
import datetime
import hashlib
import json
import random
import re
import string
import time

from urllib.parse import parse_qs, quote
import alisms
from django.urls import reverse
from django_redis import get_redis_connection
from django.conf import settings
from django.utils import timezone
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class RedisUtil:
    """
    封装缓存方法
    """
    PROXY_IP_KEYS = 'proxy_ip'
    conn = get_redis_connection('pers')  # type:Redis

    @classmethod
    def _exp_of_none(cls, *args, exp_of_none, callback):
        if not cls.conn.exists(args[0]):
            ret = callback(*args)
            if exp_of_none:
                cls.conn.expire(args[0], exp_of_none)
        else:
            ret = callback(*args)
        return ret

    @classmethod
    def get_or_set(cls, key, default=None, value_fun=None):
        """
        获取或者设置缓存
        :param key:
        :param default: 默认值，优先于value_fun
        :param value_fun: 默认取值函数
        :return:
        """
        value = cls.conn.get(key)
        if value is None and default:
            return default
        if value is not None:
            return value.decode()
        if value_fun:
            value, exp = value_fun()
            cls.conn.set(key, value, exp)
        return value

    @classmethod
    def get(cls, key, default=None):
        value = cls.conn.get(key)
        if value is None:
            return default
        return value.decode()

    @classmethod
    def set(cls, key, value, exp=None):
        """
        设置缓存
        :param key:
        :param value:
        :param exp:
        :return:
        """
        return cls.conn.set(key, value, exp)

    @classmethod
    def delete(cls, key):
        """
        缓存清除，接收list or str
        :param key:
        :return:
        """
        return cls.conn.delete(key)

    @classmethod
    def sadd(cls, name, values, exp_of_none=None):
        return cls._exp_of_none(name, values, exp_of_none=exp_of_none, callback=cls.conn.sadd)

    @classmethod
    def hset(cls, name, key, value, exp_of_none=None):
        return cls._exp_of_none(name, key, value, exp_of_none=exp_of_none, callback=cls.conn.hset)

    @classmethod
    def hincrby(cls, name, key, value=1, exp_of_none=None):
        return cls._exp_of_none(name, key, value, exp_of_none=exp_of_none, callback=cls.conn.hincrby)

    @classmethod
    def hincrbyfloat(cls, name, key, value, exp_of_none=None):
        return cls._exp_of_none(name, key, value, exp_of_none=exp_of_none, callback=cls.conn.hincrbyfloat)

    @classmethod
    def hget(cls, name, key, default=0):
        """
        缓存清除，接收list or str
        :param name:
        :param default:
        :param key:
        :return:
        """
        v = cls.conn.hget(name, key)
        if v is None:
            return default
        return v.decode()


class AESUtil:
    key = str.encode(settings.PRIVATE_KEY)

    def __init__(self, key=None):
        if key:
            self.key = str.encode(key)

    def encrypt_data(self, data):
        data = data.encode()
        aes = AES.new(self.key, AES.MODE_ECB)
        pad_data = pad(data, AES.block_size, style='pkcs7')
        return str(base64.encodebytes(aes.encrypt(pad_data)), encoding='utf8').replace('\n', '')

    def decrypt_data(self, data):
        aes = AES.new(self.key, AES.MODE_ECB)
        pad_data = pad(data, AES.block_size, style='pkcs7')
        return str(unpad(aes.decrypt(base64.decodebytes(pad_data)), block_size=AES.block_size).decode('utf8'))


def join_params(params, key=None, filter_none=True, exclude_keys=None, sep='&'):
    """
    字典排序拼接参数
    :param sep:
    :param key: 签名key
    :param params:
    :param filter_none:
    :param exclude_keys: 排除参数
    :return:
    """
    tmp = []
    for p in sorted(params):
        value = params[p]
        if filter_none and value in [None, '']:
            continue
        if isinstance(value, dict):
            continue
        if exclude_keys:
            if p in exclude_keys:
                continue
        tmp.append('{0}={1}'.format(p, value))
    if key:
        tmp.append('key={}'.format(key))
    ret = sep.join(tmp)
    return ret


def md5_encode(s):
    """
    md5加密
    :param s:
    :return:
    """
    m = hashlib.md5(s.encode(encoding='utf-8'))
    return m.hexdigest()


def sha1_encode(s):
    """
    sha1加密
    :param s:
    :return:
    """
    m = hashlib.sha1(s.encode(encoding='utf-8'))
    return m.hexdigest()


def verify_sign(params, private_key):
    """
    校验sign
    :param params:
    :param private_key:
    :return:
    """
    sign = params.get('sign')
    sign_str = join_params(params, key=private_key, sep='', exclude_keys=['sign'])
    sign_tmp = md5_encode(sign_str)
    return sign == sign_tmp


def get_ip(request):
    """
    获取客户端真实ip
    :param request:
    :return:
    """
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip.split(',')[0]


def overwrite_request(request):
    """
    覆盖request方法，重写sign和timestamp参数以支持缓存
    :param request:
    :return:
    """
    if request.method == 'GET':
        query_string = request.META['QUERY_STRING']
        qs = parse_qs(query_string)
        qs.pop('sign', '')
        qs.pop('timestamp', '')
        qs.pop('token', '')
        qs_list = []
        for k in qs:
            qs_list.append(f'{k}={quote(qs.get(k)[0])}')
        request.META['QUERY_STRING'] = '&'.join(qs_list)
    return request


class VerifyCode:

    def __init__(self, phone, code=None):
        self.phone = phone
        self.code = code

    def _send_verify_code(self, params=None):
        raise NotImplementedError

    def send(self, params=None):
        ret = self._send_verify_code(params)
        return ret


class AliVerifyCode(VerifyCode):
    template_code = 'SMS_162496315'
    sign_name = '喵赞圈'

    def __init__(self, phone, code=None, sign_name=None, template_code=None):
        super(AliVerifyCode, self).__init__(phone, code)
        if sign_name:
            self.sign_name = sign_name
        if template_code:
            self.template_code = template_code

    def _send_verify_code(self, params=None):
        """
        发送短信验证码
        :param params:
        :return:是否发生成功，True：成功
        """
        client = alisms.AliyunSMS(access_key_id=settings.ALI_ACCESS_KEY,
                                  access_key_secret=settings.ALI_ACCESS_KEY_SECRET,
                                  region_id='cn-hangzhou')
        if not params:
            params = {
                'code': self.code
            }
        result = client.send_sms(self.phone, self.sign_name, self.template_code, params)
        result = json.loads(result.text)
        code = result.get('Code')
        if code == 'OK':
            return True
        else:
            if code != 'isv.BUSINESS_LIMIT_CONTROL':
                raise Exception(f'短信发送失败：{result.get("Message")}')
        return False


def send_verify_code(phone, code, cache_key, sign_name, **kwargs):
    verify = AliVerifyCode(phone, code, sign_name=sign_name)
    ret = verify.send(params=kwargs)
    if ret:
        RedisUtil.set(cache_key, code, 600)
    return ret, phone, code


def generate_random_string(length, is_digits=False, exclude=None):
    """
    生成任意长度字符串
    :param exclude:
    :param is_digits:
    :param length:
    :return:
    """
    if is_digits:
        all_char = string.digits
    else:
        all_char = string.ascii_letters + string.digits
    if exclude:
        for char in exclude:
            all_char.replace(char, '')
    return ''.join(random.sample(all_char, length))


def datetime_now(d=0, h=0, m=0):
    """
    取之前时间
    :param d: 天
    :param h: 小时
    :param m: 分钟
    :return:
    """
    tmp = timezone.now()
    if d:
        tmp += datetime.timedelta(days=d)
    if h:
        tmp += datetime.timedelta(hours=h)
    if m:
        tmp += datetime.timedelta(minutes=m)
    return tmp


def datetime2timestamp(time_):
    """
    时间转时间戳
    :param time_:
    :return:
    """
    return int(time.mktime(time_.timetuple()))


def today_rest_seconds():
    """
    获取今天剩下的秒数
    :return:
    """
    return datetime2timestamp(datetime_now(d=-1).date()) - datetime2timestamp(datetime_now())


def week_rest_seconds():
    """
    获取本周剩下的秒数
    :return:
    """
    now = datetime_now()
    offset = 7 - now.weekday()
    weekend = now.date() + datetime.timedelta(days=offset)
    return datetime2timestamp(weekend) - datetime2timestamp(now)


def month_rest_seconds():
    """
    获取本月剩下的秒数
    :return:
    """
    now = datetime_now()
    next_month = now.date().replace(day=28) + datetime.timedelta(days=4)
    return datetime2timestamp(next_month - datetime.timedelta(days=next_month.day - 1)) - datetime2timestamp(now)


def get_server_url(name, *args, **kwargs):
    """
    获取服务器链接
    :param name: 路由对应的name
    :return:
    """
    url = reverse(name, args=args, kwargs=kwargs)
    return settings.SERVER_URL + url


def is_phone(phone):
    """
    验证号码是否符合格式
    :param phone: 电话号码
    :return:
    """
    if phone:
        reg = r'^[1][0-9]{10}$'
        p = re.compile(reg)
        return p.match(phone)
    return False


def is_idcard_id(id):
    """
    验证是否符合身份证格式
    :param id:
    :return:
    """
    if id:
        reg_18 = r"^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$"
        reg_15 = r"^[1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{2}$"
        result_18 = re.compile(reg_18)
        result_15 = re.compile(reg_15)
        return result_18.match(id) or result_15.match(id)
    return False


def is_url(url):
    """
    校验是否合法的url
    :param url:
    :return:
    """
    return re.match(r'^https?:/{2}.+$', url)


def is_num(num):
    """
    判断是否是纯数字
    :param num:
    :return:
    """
    if num:
        reg = r"^[0-9]*$"
        re_num = re.compile(reg)
        return re_num.match(num)
    return False


def split_address(address):
    """
    提取地址中的 国家-省-市-区/县-其他
    :param address:
    :return:
    """
    reg = r'(中国){0,1}([\u4e00-\u9fa5]*?(?:省|自治区|特别行政区|市|新疆|广西|内蒙古|宁夏))([\u4e00-\u9fa5]*?(?:市|区|县|自治州|盟)){0,' \
          r'1}([\u4e00-\u9fa5]*?(?:市|区|县|旗)){0,1}(.*)'
    country = ""
    province = ""
    city = ""
    district = ""
    other = ""
    pattern = re.compile(reg)
    m = pattern.search(address)
    if m:
        if m.lastindex >= 1:
            country = m.group(1)
        # 地区信息分级
        if m.lastindex >= 2:
            province = m.group(2)
        if m.lastindex >= 3:
            city = m.group(3)
        if m.lastindex >= 4:
            district = m.group(4)
        if m.lastindex >= 5:
            other = m.group(5)
    if not country:
        country = "中国"
    if not province:
        province = "省/市/自治区"
    if not city:
        city = "市/区"
    if not district:
        district = "区/县"
    if not other:
        other = address
    return country, province, city, district, other
