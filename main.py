import sys
import time

from loguru import logger

from module.config import get_config
from module.SpeedTest import speedtest
from module.html import make_html
from module.login import refresh_key

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
        appkey: str = config['platform_info']['appkey']
        appsec: str = config['platform_info']['appsec']
        refresh_key(access_token, refresh_token, appkey, appsec)

    logger.info('开始测速')
    result, duration = speedtest()
    make_html(result, duration)

