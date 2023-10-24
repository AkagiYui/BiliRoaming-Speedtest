import time

import imgkit
from loguru import logger

from constant import HTML_TEMPLATE
from utils.Parameter import get_parameter


def draw_img(result, duration):
    html_output = HTML_TEMPLATE.replace(
        "%CAPTION%", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    html_output = html_output.replace(
        "%TITLE%", get_parameter('image_output', 'title'))

    print('{:^7}|{:^7}|{:^7}|{:^7}| |{:^7}|{:^7}|{:^7}| |{:^7}| {}'.format(
        'cn', 'hk', 'tw', 'th', 'cn', 'hk', 'tw', 'avg', 'server'))

    for r in result:
        text = ''
        for android in r['status']['android']:
            if android['code'] == 0:
                html_output += '<td scope="ping" style="color: {};">{}ms</td>'.format(
                    ping_color(android['ping']), android['ping'])
                text += '{:>5}ms|'.format(android['ping'])
            elif android['code'] == -412 or android['http_code'] == 412:
                html_output += '<td style="color: red;">BAN</td>'
                text += '{:^7}|'.format('BAN')
            elif android['code'] == -10403 or android['http_code'] == 10403:
                html_output += '<td></td>'
                text += '       |'
            else:
                html_output += '<td style="color: red;">{}</td>'.format(
                    android['code'] if android['code'] != -1 else android['http_code'] if android['http_code'] != 404 else '')
                text += '       |'
        text += ' |'
        for web in r['status']['web']:
            if web['code'] == 0:
                html_output += '<td scope="ping" style="color: {};">{}ms</td>'.format(
                    ping_color(web['ping']), web['ping'])
                text += '{:>5}ms|'.format(web['ping'])
            elif web['code'] == -412 or web['http_code'] == 412:
                html_output += '<td style="color: red;">BAN</td>'
                text += '{:^7}|'.format('BAN')
            elif web['code'] == -10403 or web['http_code'] == 10403:
                html_output += '<td></td>'
                text += '       |'
            else:
                html_output += '<td style="color: red;">{}</td>'.format(
                    web['code'] if web['code'] != -1 else web['http_code'] if web['http_code'] != 404 else '')
                text += '       |'
        html_output += '<td scope="ping" style="color: {};">{}ms</td><td scope="server">{}</td></tr>'.format(
            ping_color(r['status']['avg']), r['status']['avg'], r['server'])
        text += ' |{:>5}ms| {}'.format(r['status']['avg'], r['server'])
        print(text)

    html_output += "</table><center><a>测速完成, 共耗时: " + str(duration) + "秒</a></center></body></html>"
    html_output = html_output.replace("陈睿", "**").replace("死", "*").replace("妈", "*")
    if get_parameter('image_output', 'enable'):
        logger.info("开始生成测速图")
        imgkit.from_string(html_output, get_parameter('image_output', 'file_name'), options={'quiet': ''})
        # path_wk = r'D:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
        # config = imgkit.config(wkhtmltoimage=path_wk)
        # imgkit.from_string(html_output, get_parameter('image_output', 'file_name'), config=config, options={'quiet': ''})


def ping_color(ping: int) -> str:
    if ping < 150:
        return 'green'
    elif ping < 300:
        return 'orange'
    else:
        return 'red'
