import time

HTML_TITLE = '哔哩漫游公共解析服务器测速'
HTML_TEMPLATE = '''<html>
<head>
  <style>
    table {
        width: 100%;
    }
    td, th {
        border: 1px solid rgb(190, 190, 190);
        text-align: center;
        padding : 4px;
    }
    td[scope="server"] {
        text-align: left;
    }
    tr:nth-child(even) {
        background-color: #eee;
    }
    tr[scope="header"] > th {
        background-color: #ddd;
    }
    td[scope="ping"] {
        text-align: right;
    }
  </style>
</head>
<body>
<table>
<center><a>%TITLE%</a></center>
<caption>%CAPTION%</caption>
<tr scope="header">
  <th colspan="4">安卓</th>
  <th colspan="3">WEB</th>
  <th rowspan="2">平均</th>
  <th rowspan="2">地址</th>
</tr>
<tr scope="header">
  <th>CN</th>
  <th>HK</th>
  <th>TW</th>
  <th>TH</th>
  <th>CN</th>
  <th>HK</th>
  <th>TW</th>
</tr>
<tr>
'''


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
