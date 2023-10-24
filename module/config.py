import json
from pathlib import Path

from loguru import logger


def get_config() -> dict | None:
    """获取配置"""
    path = Path(__file__).parent.parent / 'config.json'
    try:
        with open(path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
    except Exception as e:
        logger.error(f'获取配置文件失败: {e}')
        return None


def get_parameter(*parameters) -> any:
    """
    获取指定参数

    :param parameters: 参数路径
    """
    try:
        value = get_config()
        for parameter in parameters:
            value = value.get(parameter)
        return value
    except Exception as e:
        logger.error(f'获取指定参数失败: {e}')
        return None


def update_config(new_config: dict) -> None:
    """更新配置文件"""
    final_config = get_config().update(new_config)
    path = Path(__file__).parent.parent / 'config.json'
    try:
        with open(path, 'w', encoding='utf-8') as json_file:
            json.dump(final_config, json_file, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f'更新配置文件失败: {e}')


def get_server_list() -> list[str]:
    """获取服务器列表"""
    path = Path(__file__).parent.parent / 'server.txt'
    server_list = list()
    with open(path, mode='r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith("#") and line.strip() != "":
                continue
            server_list.append(line.strip())
    return server_list
