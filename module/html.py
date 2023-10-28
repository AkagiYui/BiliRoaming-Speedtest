import time

HTML_TITLE = '哔哩漫游公共解析服务器测速'
HTML_TEMPLATE = '''<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
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
<tr>'''


def make_html(result: list[dict], duration: int) -> str:
    """
    生成html

    :param result: 测速结果
    :param duration: 测速耗时
    :return: html字符串
    """
    html_output = HTML_TEMPLATE.replace('%CAPTION%', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    html_output = html_output.replace('%TITLE%', HTML_TITLE)

    def add_row(_server: dict) -> None:
        nonlocal html_output
        if _server['code'] == 0:
            html_output += f'<td scope="ping" style="color: {_color(_server["ping"])};">{_server["ping"]}ms</td>'
        elif _server['code'] == -412 or _server['http_code'] == 412:
            html_output += '<td style="color: red;">BAN</td>'
        elif _server['code'] == -10403 or _server['http_code'] == 10403:
            html_output += '<td></td>'
        else:
            if _server["code"] != -1:
                server_code = _server["code"]
            elif _server["http_code"] != 404:
                server_code = _server["http_code"]
            else:
                server_code = ""
            html_output += f'<td style="color: red;">{server_code}</td>'

    for r in result:
        for server in r['android']:
            add_row(server)
        for server in r['web']:
            add_row(server)
        html_output += f'<td scope="ping" style="color: {_color(r["avg"])};">{r["avg"]}ms</td>'
        html_output += f'<td scope="server">{r["server"]}</td></tr>'

    html_output += f'</table><center><a>测速完成, 共耗时: {str(duration)}秒</a></center></body></html>'
    html_output = html_output.replace('陈睿', '**').replace('死', '*').replace('妈', '*')
    return html_output


def _color(ping: int) -> str:
    """根据ping值获取颜色"""
    if ping < 150:
        return 'green'
    elif ping < 300:
        return 'orange'
    else:
        return 'red'
