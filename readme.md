# 微信订阅号全文rss

依赖 [feed.org](https://feeddd.org) 提供的rss通知，将微信订阅号全文输出为rss。

## 使用方法
将要订阅的公众号的 feed org 链接放在 rss-source.txt 中，每行一个，然后运行 `python3 main.py` 即可。
生成的rss文件会在rss文件夹下，文件名为公众号的名称。

本地会启动一个http服务，端口为 8000，可以通过 http://localhost:8000/rss/公众号名称 来访问rss文件。
也会启动一个定时服务，两小时一次，自动更新rss文件。