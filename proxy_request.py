def get_proxy(proxies_type):
    """
    获取代理
    :param proxies_type:
    :return:
    """
    assert proxies_type in ['zhima', 'mogu']
    proxies = {}
    if proxies_type == 'zhima':
        proxy = RedisUtil.get(RedisUtil.PROXY_IP_KEYS)
        if not proxy:
            url = settings.ZHIMA_URL
            ret = requests.get(url).json()
            if ret.get('code') == 0 and ret.get('success'):
                data = ret.get('data')[0]
                ip = data.get('ip')
                port = data.get('port')
                proxy = f'{ip}:{port}'
                RedisUtil.set(RedisUtil.PROXY_IP_KEYS, proxy, 300)
                proxy = f'http://{proxy}'
                proxies = {
                    'https': proxy,
                    'http': proxy
                }
    elif proxies_type == 'mogu':
        proxies = {
            'https': 'https://transfer.mogumiao.com:9001',
            'http': 'http://transfer.mogumiao.com:9001'
        }
    return proxies


def proxy_request(url, method, params=None, data=None, json=None, headers=None, is_proxies=False, proxies_type='mogu'):
    # 代理请求封装
    assert method in ['post', 'get']
    proxies = {}
    headers = {}
    if headers:
        headers = headers
    if is_proxies:
        proxies = get_proxy(proxies_type)
        if proxies_type == 'mogu':
            headers['Proxy-Authorization'] = 'Basic ' + settings.MOGU_PROXY_KEY
    if method == 'get':
        ret = requests.get(url, params=params, proxies=proxies, headers=headers, verify=False,
                           allow_redirects=False, timeout=6)
    else:
        ret = requests.post(url, params=params, data=data, json=json, proxies=proxies, headers=headers,
                            verify=False,
                            allow_redirects=False, timeout=6)
    return ret