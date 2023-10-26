import hashlib
import json
import time
import urllib.parse

import requests
from loguru import logger

from module.config import update_config
from module.constant import APP_KEY_CN, APP_SEC_CN, USER_AGENT

CID = 86  # 国际电话区号
HEADER = {
    'Host': 'passport.bilibili.com',
    'buvid': 'XU4B4E44813CCE878BC2D965745433AB55B06',
    'env': 'prod',
    'app-key': 'android64',
    'user-agent': USER_AGENT,
    'x-bili-trace-id': '7a709e7790e6e76a7de8c8e48c640c77:7de8c8e48c640c77:0:0',
    'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
    # "accept-encoding": "gzip, deflate, br"
}


def appsign(params: dict, appkey: str, appsec: str) -> dict:
    """
    为参数签名

    :param params: 参数
    :param appkey: appkey
    :param appsec: appsec
    :return: 签名后的参数
    """
    params.update({'appkey': appkey})
    params = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params)
    sign = hashlib.md5((query + appsec).encode()).hexdigest()
    params.update({'sign': sign})
    return params


def refresh_key(access_token: str, refresh_token: str,
                appkey: str = APP_KEY_CN, appsec: str = APP_SEC_CN) -> tuple[str, str, int]:
    """
    刷新access_token

    :param access_token: 原access_token
    :param refresh_token: refresh_token
    :param appkey: appkey
    :param appsec: appsec
    """
    url = 'https://passport.bilibili.com/x/passport-login/oauth2/refresh_token'
    current_timestamp = int(time.time())
    params = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'ts': current_timestamp
    }
    params = appsign(params, appkey, appsec)
    headers = {'User-Agent': USER_AGENT}
    response = requests.post(url, params=params, headers=headers)
    info_data = response.json()
    logger.debug(info_data)

    try:
        if info_data['code'] != 0:
            raise Exception(info_data['message'])
        token_info = info_data.get('data').get('token_info')
        new_access_token = token_info['access_token']
        new_refresh_token = token_info['refresh_token']
        expires_in = token_info['expires_in']
        logger.success('access_token 刷新成功')
        logger.debug(f'access_token: {new_access_token}, refresh_token: {new_refresh_token}, expires_in: {expires_in}')
        return new_access_token, new_refresh_token, expires_in + current_timestamp
    except Exception as e:
        logger.error(f'发生错误: {e}, access_token 刷新失败')


def _sms_send(_phone: str) -> tuple[int, str, str]:
    """
    发送验证码

    :param _phone: 手机号
    :return: 状态码, 信息, 登录token
    """
    url = 'https://passport.bilibili.com/x/passport-login/sms/send'
    data = {'cid': CID, 'tel': _phone, 'ts': int(time.time())}
    data = appsign(params=data, appkey=APP_KEY_CN, appsec=APP_SEC_CN)
    r = requests.post(url=url, data=data, headers=HEADER)
    return r.json()['code'], r.json()['message'], r.json()['data']['captcha_key']


def _sms_login(_captcha_key: str, _code: str, _phone: str) -> dict:
    """
    通过验证码登录

    :param _captcha_key: 登录token
    :param _code: 验证码
    :param _phone: 手机号
    :return: 登录信息
    """
    url = 'https://passport.bilibili.com/x/passport-login/login/sms'
    data = {
        'captcha_key': _captcha_key,
        'cid': CID,
        'code': _code,
        'tel': _phone,
        'ts': int(time.time())
    }
    data = appsign(params=data, appkey=APP_KEY_CN, appsec=APP_SEC_CN)
    r = requests.post(url=url, data=data, headers=HEADER)
    return r.json()


def _update_info(_login_info: dict) -> None:
    """更新账号信息"""
    token_info = _login_info['data']['token_info']
    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']
    expires_in = token_info['expires_in']
    current_timestamp = int(time.time())
    expires_date = expires_in + current_timestamp
    update_config({
        'user_info': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_date': expires_date
        }
    })


if __name__ == '__main__':
    # 手动更新账号信息
    phone: str = input('请输入手机号: ')
    status_code, msg, captcha_key = _sms_send(_phone=phone)
    if msg != '0':
        print(msg)
    if status_code != 0:
        exit()

    code: str = input('请输入验证码: ')
    login_info: dict = _sms_login(_captcha_key=captcha_key, _code=code, _phone=phone)
    print(login_info['data']['message'])
    # 登录信息存档
    with open('login_info.json', 'w', encoding='utf-8') as w:
        json.dump(login_info, w, ensure_ascii=False, indent=2)

    if login_info['data']['status'] == 0:
        print('登录成功!')
        _update_info(login_info)
    else:
        print('登录失败...')
