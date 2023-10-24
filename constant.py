USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

APP_KEY_TH = '7d089525d3611b1c'
APP_SEC_TH = 'acd495b248ec528c2eed1e862d393126'

AREA_LIST = [
    {'cn': 266323},
    {'hk': 425578},
    {'tw': 285951},
    {'th': 377544}
]

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
