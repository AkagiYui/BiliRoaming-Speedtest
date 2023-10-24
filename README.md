# 哔哩漫游测速报告生成

原库: https://github.com/KimmyXYC/BiliRoaming-Speedtest

[生成效果示例](https://github.com/yujincheng08/BiliRoaming/wiki/%E5%85%AC%E5%85%B1%E8%A7%A3%E6%9E%90%E6%9C%8D%E5%8A%A1%E5%99%A8#%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%8A%B6%E6%80%81)

## 特性

- 移除了 sftp 上传部分
- 移除了图片生成部分

## 使用

### 安装依赖

```shell
pip install -r requirements.txt
```

### 登录哔哩哔哩账号

```shell
python -m module.login
```

### 生成报告

```shell
python main.py
```
