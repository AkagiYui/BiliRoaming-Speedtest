import sys
import time

from loguru import logger

from module.config import get_config
from module.html import make_html
from module.login import refresh_key
from module.speedtest import speedtest

if __name__ == '__main__':
    # 设置logger
    logger.remove()
    handler_id = logger.add(sys.stderr, level='INFO')
    logger.add(sink='run.log', format='{time} - {level} - {message}', level='INFO', rotation='20 MB', enqueue=True)

    # 检查access_token是否过期
    config: dict = get_config()
    expires_date: int = config['user_info']['expires_date']
    current_timestamp: int = int(time.time())
    maturity_criteria: int = 5 * 24 * 60 * 60  # 5天
    if current_timestamp + maturity_criteria >= expires_date:
        logger.info(f'access_token 已过期，尝试刷新')
        access_token: str = config['user_info']['access_token']
        refresh_token: str = config['user_info']['refresh_token']
        refresh_key(access_token, refresh_token)

    logger.info('开始测速')
    result, duration = speedtest()

    # 打印结果
    text = '  cn   |  hk   |  tw   |  th   | |  cn   |  hk   |  tw   | |  avg  | server\n'

    def add_row(_server: dict) -> None:
        global text
        if _server['code'] == 0:
            text += f'{_server["ping"]:>5}ms|'
        elif _server['code'] == -412 or _server['http_code'] == 412:
            text += '  BAN  |'
        else:
            text += '       |'

    for r in result:
        for server in r['android']:
            add_row(server)
        text += ' |'
        for server in r['web']:
            add_row(server)
        text += f' |{r["avg"]:>5}ms| {r["server"]}\n'
    print(text)
    # 结果打印完毕

    html_text = make_html(result, duration)
    with open('index.html', mode='w', encoding='utf-8') as f:
        f.write(html_text)
