import time
from json import JSONDecodeError
from multiprocessing import Manager, Process

from httpx import (Client, ConnectTimeout, ReadTimeout, RemoteProtocolError,
                   Response)
from loguru import logger

from module.config import get_parameter, get_server_list
from module.constant import (APP_KEY_CN, APP_KEY_TH, APP_SEC_CN, APP_SEC_TH,
                             USER_AGENT)
from module.login import appsign

ACCESS_KEY = get_parameter('user_info', 'access_token')
PLATFORM = 'android'
VERSION_CODE = '1100'
VERSION_NAME = '1.6.10'
AREA_EP_ID: dict[str, int] = {  # 各个地区用于解析的剧集
    'cn': 266323,  # 刀剑神域 第一季
    'hk': 425578,  # 鬼灭之刃 無限列車篇（僅港澳）
    'tw': 285951,  # 刀剑神域 War of Under
    'th': 377544
}


def speedtest() -> tuple[list[dict], int]:
    """
    测速

    :return: (测速结果, 用时 秒)
    """
    result_list: list[dict] = Manager().list()  # 测速结果集

    # 多进程测速
    processes: list[Process] = list()
    for server in get_server_list():
        processes.append(Process(target=_processing, args=(server, result_list)))
    start_time: float = time.time()
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    duration: int = int(time.time() - start_time)

    sorted_result: list[dict] = sorted(result_list, key=lambda r: r['avg'])
    return sorted_result, duration


def _processing(server_host: str, whole_result_list: list[dict]) -> None:
    """
    测速进程

    :param server_host: 服务器域名
    :param whole_result_list: 测速结果集
    :return:
    """

    session = Client()
    session.headers.update({
        'user-agent': USER_AGENT,
        'Build': VERSION_CODE,
        'x-from-biliroaming': VERSION_NAME,
        'platform-from-biliroaming': PLATFORM
    })

    # 测试服务器是否可用
    timeout = 15  # 超时时间, 秒
    try:
        logger.debug(f'尝试连接服务器 {server_host}')
        session.head(f'https://{server_host}', timeout=timeout)
    except Exception as e:
        logger.error(f'服务器 {server_host} 连接失败: {e}')
        return

    # 该服务器测试结果
    server_result: dict = {
        'server': server_host,  # 服务器域名
        'avg': -1,  # 平均延迟
        'android': [],  # android端测试结果
        'web': [],  # web端测试结果
    }
    valid_count: int = 0  # 有效次数
    total_time: int = 0  # 总耗时, 毫秒
    base_url = f'https://{server_host}'  # 基础url

    def add_ping(_ping: int) -> None:
        """添加延迟"""
        nonlocal valid_count, total_time
        valid_count += 1
        total_time += _ping

    def go_test(_test_url: str, _params: dict) -> dict:
        # 本次测试结果
        new_result = {
            'area': area,  # 地区
            'ping': -1,  # 延迟, 毫秒
            'http_code': -1,  # http状态码
            'code': -1,  # todo 响应码
        }

        # 发送请求
        try:
            time.sleep(1.5)
            session.get(_test_url, timeout=10)  # 预热, 构造缓存
            time.sleep(1.5)
            response: Response = session.get(_test_url, params=_params, timeout=10)
        except (ConnectTimeout, ReadTimeout, RemoteProtocolError) as _e:
            logger.error(f'请求 {_test_url} 异常: {_e}')
        else:
            # 请求成功
            content_text = f'{response.text[:64]}...' if len(response.text) > 64 else response.text
            ping = int(response.elapsed.total_seconds() * 1000)  # 延迟, 毫秒
            new_result.update({
                'ping': ping,
                'http_code': response.status_code,
            })
            if response.status_code < 400:
                # 资源可用, 尝试解析内容
                try:
                    data = response.json()  # 解析json
                except JSONDecodeError as _e:
                    # json解析失败, 回退到文本解析
                    data = {'code': -1}
                    if '"code":0,' in response.text:
                        data['code'] = 0
                    elif '"code":-412,' in response.text:
                        data['code'] = -412
                    else:
                        logger.debug(f'请求 {_test_url} json解析失败: {_e}')
                        logger.debug(f'content-type: {response.headers["content-type"]}')

                # 记录数据
                if data['code'] == 0:
                    add_ping(ping)  # 仅当内容解析成功时才计入延迟
                if data['code'] != 0:
                    logger.debug(f'code != 0, content: {content_text}')
                new_result.update({'code': data['code']})
            else:
                # 资源不可用, 仅记录延迟和http状态码
                logger.debug(f'请求 {_test_url} 失败: {content_text}')
        return new_result

    # 请求参数
    params: dict[str | int] = {
        'access_key': ACCESS_KEY,
        'fnver': 0,
        'fnval': 464,
        'platform': PLATFORM,
        'fourk': 1,
        'qn': 125
    }

    # android 端
    for area, ep_id in AREA_EP_ID.items():
        test_url: str = f'{base_url}/pgc/player/api/playurl'  # 测试url
        params.update({'area': area, 'ep_id': ep_id})
        if area == 'th':
            test_url = f'{base_url}/intl/gateway/v2/ogv/playurl'
            params.update({'s_locale': 'zh_SG'})
            params = appsign(params, APP_KEY_TH, APP_SEC_TH)
        else:
            params = appsign(params, APP_KEY_CN, APP_SEC_CN)
        server_result['android'].append(go_test(test_url, params))

    # web
    for area, ep_id in AREA_EP_ID.items():
        if area == 'th':
            continue  # web端不支持泰区

        test_url = f'{base_url}/pgc/player/web/playurl'
        params.update({'area': area, 'ep_id': ep_id})
        params = appsign(params, APP_KEY_CN, APP_SEC_CN)
        server_result['web'].append(go_test(test_url, params))

    avg = int(total_time / valid_count) if valid_count > 0 else timeout * 1000
    server_result['avg'] = avg
    whole_result_list.append(server_result)
