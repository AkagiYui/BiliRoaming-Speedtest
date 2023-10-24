import hashlib
import json
import pathlib
import time
import urllib.parse

import requests
from loguru import logger

from module.config import update_config
from module.constant import APP_KEY_CN, APP_SEC_CN, CID, HEADER, USER_AGENT


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


def refresh_key(access_token: str, refresh_token: str, appkey: str, appsec: str) -> None:
    """刷新access_token"""
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
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        expires_in = token_info['expires_in']
        update_config({
            'user_info': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_date': expires_in + current_timestamp
            }
        })
        logger.success('access_token 刷新成功')
        logger.debug(f'access_token: {access_token}, refresh_token: {refresh_token}, expires_in: {expires_in}')
    except Exception as e:
        logger.error(f'发生错误: {e}, access_token 刷新失败')


def _sms_send(phone: str):
    """发送验证码"""
    url = 'https://passport.bilibili.com/x/passport-login/sms/send'
    data = {'cid': CID, 'tel': phone, 'ts': int(time.time())}
    data = appsign(params=data, appkey=APP_KEY_CN, appsec=APP_SEC_CN)
    r = requests.post(url=url, data=data, headers=HEADER)
    return r.json()['code'], r.json()['message'], r.json()['data']['captcha_key']


def _sms_login(captcha_key, code, phone) -> dict:
    """通过验证码登录"""
    url = 'https://passport.bilibili.com/x/passport-login/login/sms'
    data = {
        "captcha_key": captcha_key,
        "cid": CID,
        "code": code,
        "tel": phone,
        "ts": int(time.time())
    }
    data = appsign(params=data, appkey=APP_KEY_CN, appsec=APP_SEC_CN)
    r = requests.post(url=url, data=data, headers=HEADER)
    return r.json()


def _update_info():
    with open("login_info.json", "r", encoding="utf-8") as r:
        token_info = json.load(r)["data"]["token_info"]
    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]
    expires_in = token_info["expires_in"]
    current_timestamp = int(time.time())
    expires_date = expires_in + current_timestamp
    with open('Config/config.json', 'r+', encoding='utf-8') as json_file:
        data = json.load(json_file)
        data['user_info']['access_token'] = access_token
        data['user_info']['refresh_token'] = refresh_token
        data['user_info']['expires_date'] = expires_date
        data['platform_info']['appkey'] = APP_KEY_CN
        data['platform_info']['appsec'] = APP_SEC_CN
        json_file.seek(0)
        json.dump(data, json_file, ensure_ascii=False, indent=2)
        json_file.truncate()


if __name__ == '__main__':
    # 手动更新账号信息
    phone: str = input('请输入手机号: ')
    status_code, msg, captcha_key = _sms_send(phone=phone)
    if msg != '0':
        print(msg)
    if status_code != 0:
        exit()

    code: str = input('请输入验证码: ')
    login_info: dict = _sms_login(captcha_key=captcha_key, code=code, phone=phone)
    print(login_info['data']['message'])
    with open('login_info.json', 'w', encoding='utf-8') as w:
        json.dump(login_info, w, ensure_ascii=False, indent=2)

    if login_info['data']['status'] == 0:
        print('登录成功!')
        _update_info()
    else:
        print('登录失败...')
