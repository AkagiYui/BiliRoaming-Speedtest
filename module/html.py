import time

from module.constant import HTML_TEMPLATE, HTML_TITLE


def make_html(result: list[dict], duration: int) -> str:
    """
    生成html

    :param result: 测速结果
    :param duration: 测速耗时
    :return: html字符串
    """
    html_output = HTML_TEMPLATE.replace('%CAPTION%', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    html_output = html_output.replace('%TITLE%', HTML_TITLE)

    print(f'{"cn":^7}|{"hk":^7}|{"tw":^7}|{"th":^7}| |{"cn":^7}|{"hk":^7}|{"tw":^7}| |{"avg":^7}| server')

    for r in result:
        text = ''

        def add_row(server: dict) -> None:
            nonlocal html_output, text
            if server['code'] == 0:
                html_output += f'<td scope="ping" style="color: {_ping_color(server["ping"])};">{server["ping"]}ms</td>'
                text += f'{server["ping"]:>5}ms|'
            elif server['code'] == -412 or server['http_code'] == 412:
                html_output += '<td style="color: red;">BAN</td>'
                text += f'{"BAN":^7}|'
            elif server['code'] == -10403 or server['http_code'] == 10403:
                html_output += '<td></td>'
                text += '       |'
            else:
                html_output += f'<td style="color: red;">{server["code"] if server["code"] != -1 else server["http_code"] if server["http_code"] != 404 else ""}</td>'
                text += '       |'

        for server in r['status']['android']:
            add_row(server)
        text += ' |'
        for server in r['status']['web']:
            add_row(server)
        html_output += f'<td scope="ping" style="color: {_ping_color(r["status"]["avg"])};">{r["status"]["avg"]}ms</td><td scope="server">{r["server"]}</td></tr>'
        text += f' |{r["status"]["avg"]:>5}ms| {r["server"]}'
        print(text)

    html_output += f'</table><center><a>测速完成, 共耗时: {str(duration)}秒</a></center></body></html>'
    html_output = html_output.replace('陈睿', '**').replace('死', '*').replace('妈', '*')
    return html_output


def _ping_color(ping: int) -> str:
    """根据ping值获取颜色"""
    if ping < 150:
        return 'green'
    elif ping < 300:
        return 'orange'
    else:
        return 'red'
