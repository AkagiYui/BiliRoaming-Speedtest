import time

from module.config import get_parameter
from module.constant import HTML_TEMPLATE


def make_html(result: list[dict], duration: int) -> None:
    html_output = HTML_TEMPLATE.replace('%CAPTION%', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    html_output = html_output.replace('%TITLE%', get_parameter('image_output', 'title'))

    print(f'{"cn":^7}|{"hk":^7}|{"tw":^7}|{"th":^7}| |{"cn":^7}|{"hk":^7}|{"tw":^7}| |{"avg":^7}| server')

    for r in result:
        text = ''
        for android in r['status']['android']:
            if android['code'] == 0:
                html_output += f'<td scope="ping" style="color: {_ping_color(android["ping"])};">{android["ping"]}ms</td>'
                text += f'{android["ping"]:>5}ms|'
            elif android['code'] == -412 or android['http_code'] == 412:
                html_output += '<td style="color: red;">BAN</td>'
                text += f'{"BAN":^7}|'
            elif android['code'] == -10403 or android['http_code'] == 10403:
                html_output += '<td></td>'
                text += '       |'
            else:
                html_output += f'<td style="color: red;">{android["code"] if android["code"] != -1 else android["http_code"] if android["http_code"] != 404 else ""}</td>'
                text += '       |'
        text += ' |'
        for web in r['status']['web']:
            if web['code'] == 0:
                html_output += f'<td scope="ping" style="color: {_ping_color(web["ping"])};">{web["ping"]}ms</td>'
                text += f'{web["ping"]:>5}ms|'
            elif web['code'] == -412 or web['http_code'] == 412:
                html_output += '<td style="color: red;">BAN</td>'
                text += f'{"BAN":^7}|'
            elif web['code'] == -10403 or web['http_code'] == 10403:
                html_output += '<td></td>'
                text += '       |'
            else:
                html_output += f'<td style="color: red;">{web["code"] if web["code"] != -1 else web["http_code"] if web["http_code"] != 404 else ""}</td>'
                text += '       |'
        html_output += f'<td scope="ping" style="color: {_ping_color(r["status"]["avg"])};">{ r["status"]["avg"]}ms</td><td scope="server">{r["server"]}</td></tr>'
        text += f' |{r["status"]["avg"]:>5}ms| {r["server"]}'
        print(text)

    html_output += f'</table><center><a>测速完成, 共耗时: {str(duration)}秒</a></center></body></html>'
    html_output = html_output.replace('陈睿', '**').replace('死', '*').replace('妈', '*')

    # 写出html文件
    with open('result.html', 'w') as f:
        f.write(html_output)


def _ping_color(ping: int) -> str:
    """根据ping值获取颜色"""
    if ping < 150:
        return 'green'
    elif ping < 300:
        return 'orange'
    else:
        return 'red'
