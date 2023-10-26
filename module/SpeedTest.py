import time
from multiprocessing import Manager, Process

import requests
from loguru import logger
from requests.exceptions import ConnectionError, ReadTimeout
from simplejson.errors import JSONDecodeError

from module.config import get_parameter, get_server_list
from module.constant import APP_KEY_TH, APP_SEC_TH, AREA_LIST, USER_AGENT
from module.login import appsign

PLATFORM_INFO = get_parameter('platform_info')
VERSION_CODE = PLATFORM_INFO['version_code']
VERSION_NAME = PLATFORM_INFO['version_name']

ACCESS_KEY = get_parameter('user_info', 'access_token')
APP_KEY = PLATFORM_INFO['appkey']
APP_SEC = PLATFORM_INFO['appsec']
PLATFORM = PLATFORM_INFO['platform']


def speedtest() -> tuple[list[dict], int]:
    """
    测速

    :return: (测速结果, 用时 秒)
    """
    platform = get_parameter('platform_info', 'platform')
    session = requests.Session()
    session.headers.update({'user-agent': USER_AGENT})
    session.headers.update({'Build': VERSION_CODE})
    session.headers.update({'x-from-biliroaming': VERSION_NAME})
    session.headers.update({'platform-from-biliroaming': platform})

    start_time = time.time()

    mgr = Manager()
    result = mgr.list()

    server_list = mgr.list(get_server_list())

    p = Process(target=_loop, args=(session, result, server_list))
    p.start()
    p.join()

    result = sorted(result, key=lambda r: r['status']['avg'])
    duration = int(time.time() - start_time)
    return result, duration


def _loop(session, result, server_list):
    for server in server_list:
        server_result: dict = {
            'server': server,
            'status': {
                'web': [],
                'android': []
            }
        }
        Process(target=_processing, args=(
            server, server_result, session, result)).start()


def _processing(server, server_result, session, result):
    try:
        session.head(f'https://{server}', timeout=15)
    except Exception as e:
        logger.debug(e)
        return
    count = 0
    total = 0
    test_url = ""
    for area_data in AREA_LIST:
        area = list(area_data.keys())[0]
        ep_id = list(area_data.values())[0]

        if area != 'th':
            params = {
                'access_key': ACCESS_KEY,
                'area': area,
                'ep_id': ep_id,
                'fnver': 0,
                'fnval': 464,
                'platform': PLATFORM,
                'fourk': 1,
                'qn': 125
            }
            params = appsign(params, APP_KEY, APP_SEC)
            test_url = f'https://{server}/pgc/player/api/playurl'
        else:
            params = {
                'access_key': ACCESS_KEY,
                'area': area,
                'ep_id': ep_id,
                'fnver': 0,
                'fnval': 464,
                'fourk': 1,
                'platform': PLATFORM,
                'qn': 125,
                's_locale': 'zh_SG'
            }
            params = appsign(params, APP_KEY_TH, APP_SEC_TH)
            test_url = f'https://{server}/intl/gateway/v2/ogv/playurl'
        try:
            time.sleep(1.5)
            session.get(test_url, timeout=10)
            time.sleep(1.5)
            response: requests.Response = session.get(test_url, params=params, timeout=10)
            ping = int(response.elapsed.total_seconds() * 1000)
            if not response.ok:
                logger.debug((response.text[:64] + '..') if len(response.text) > 64 else response.text)
                server_result['status']['android'].append(
                    {
                        'area': area,
                        'ping': ping,
                        'http_code': response.status_code,
                        'code': -1,
                    }
                )
                continue
        except ConnectionError as e:
            logger.debug(e)
            server_result['status']['android'].append(
                {
                    'area': area,
                    'ping': -1,
                    'http_code': -1,
                    'code': -1,
                }
            )
            continue
        except ReadTimeout as e:
            logger.debug(e)
            server_result['status']['android'].append(
                {
                    'area': area,
                    'ping': -1,
                    'http_code': -1,
                    'code': -1,
                }
            )
            continue
        try:
            data = response.json()
            if data['code'] == 0:
                count += 1
                total += ping
            if data['code'] != 0:
                logger.debug((response.text[:64] + '..') if len(response.text) > 64 else response.text)
            server_result['status']['android'].append(
                {
                    'area': area,
                    'ping': ping,
                    'http_code': response.status_code,
                    'code': data['code'],
                }
            )
        except JSONDecodeError as e:
            if '"code":0,' in response.text:
                count += 1
                total += ping
                server_result['status']['android'].append(
                    {
                        'area': area,
                        'ping': ping,
                        'http_code': response.status_code,
                        'code': 0,
                    }
                )
                continue
            if '"code":-412,' in response.text:
                count += 1
                total += ping
                server_result['status']['android'].append(
                    {
                        'area': area,
                        'ping': ping,
                        'http_code': response.status_code,
                        'code': -412,
                    }
                )
                continue
            logger.debug(e)
            logger.debug(response.headers['content-type'])
            logger.debug((response.text[:64] + '..') if len(response.text) > 64 else response.text)
            server_result['status']['android'].append(
                {
                    'area': area,
                    'ping': ping,
                    'http_code': -1,
                    'code': -1,
                }
            )
            continue

    for area_data in AREA_LIST:
        area = list(area_data.keys())[0]
        ep_id = list(area_data.values())[0]

        test_url = ''
        if area != 'th':
            params = {
                'access_key': ACCESS_KEY,
                'area': area,
                'ep_id': ep_id,
                'fnver': 0,
                'fnval': 464,
                'platform': PLATFORM,
                'fourk': 1,
                'qn': 125
            }
            params = appsign(params, APP_KEY, APP_SEC)
            test_url = f'https://{server}/pgc/player/web/playurl'
        else:
            continue
        try:
            time.sleep(1.5)
            session.get(test_url, timeout=10)
            time.sleep(1.5)
            response: requests.Response = session.get(test_url, params=params, timeout=10)
            ping = int(response.elapsed.total_seconds() * 1000)
            if not response.ok:
                logger.debug((response.text[:64] + '..') if len(response.text) > 64 else response.text)
                server_result['status']['web'].append(
                    {
                        'area': area,
                        'ping': ping,
                        'http_code': response.status_code,
                        'code': -1,
                    }
                )
                continue
        except ConnectionError as e:
            logger.debug(e)
            server_result['status']['web'].append(
                {
                    'area': area,
                    'ping': -1,
                    'http_code': -1,
                    'code': -1,
                }
            )
            continue
        except ReadTimeout as e:
            logger.debug(e)
            server_result['status']['web'].append(
                {
                    'area': area,
                    'ping': -1,
                    'http_code': -1,
                    'code': -1,
                }
            )
            continue
        try:
            data = response.json()
            if data['code'] == 0:
                count += 1
                total += ping
            if data['code'] != 0:
                logger.debug((response.text[:64] + '..') if len(response.text) > 64 else response.text)
            server_result['status']['web'].append(
                {
                    'area': area,
                    'ping': ping,
                    'http_code': response.status_code,
                    'code': data['code'],
                }
            )
        except JSONDecodeError as e:
            if '"code":0,' in response.text:
                count += 1
                total += ping
                server_result['status']['web'].append(
                    {
                        'area': area,
                        'ping': ping,
                        'http_code': response.status_code,
                        'code': 0,
                    }
                )
                continue
            if '"code":-412,' in response.text:
                count += 1
                total += ping
                server_result['status']['web'].append(
                    {
                        'area': area,
                        'ping': ping,
                        'http_code': response.status_code,
                        'code': -412,
                    }
                )
                continue
            logger.debug(e)
            logger.debug(response.headers['content-type'])
            logger.debug((response.text[:64] + '..') if len(response.text) > 64 else response.text)
            server_result['status']['web'].append(
                {
                    'area': area,
                    'ping': ping,
                    'http_code': -1,
                    'code': -1,
                }
            )
            continue
    avg = 15000
    if count > 0:
        avg = int(total / count)
    server_result['status']['avg'] = avg
    result.append(server_result)
