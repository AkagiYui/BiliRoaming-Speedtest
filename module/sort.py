"""
对server.txt进行字典序排序
"""
from pathlib import Path

file_path = Path(__file__).parent.parent / 'server.txt'

if __name__ == '__main__':
    # 读取server.txt
    with open(file_path, mode='r', encoding='utf-8') as f:
        servers = f.readlines()

    # 排序
    servers.sort()

    # 写入server.txt
    with open(file_path, mode='w', encoding='utf-8') as f:
        for server in servers:
            f.write(server)

    print('排序完成')
