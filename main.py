import feedparser
from feedgen.feed import FeedGenerator
from readabilipy import simple_json_from_html_string
import requests
import lmdb
import json
import os
import schedule
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

env = lmdb.open("./data", map_size=1024 * 1024 * 1024 * 2)

def get_article_from_url(url):
    with env.begin(write=True) as txn:
        cursor = txn.cursor()
        if cursor.get(url.encode('utf-8')) is not None:
            print("from cache")
            article = json.loads(cursor.get(url.encode('utf-8')).decode('utf-8'))
        else:
            # 获取全文
            req = requests.get(url)
            print("from request")
            article = simple_json_from_html_string(req.text, use_readability=True)
            cursor.put(url.encode('utf-8'), json.dumps(article).encode('utf-8'))
    return article

def add_entry_to_rss(entry, fg):
    url = entry.link
    article = get_article_from_url(url)
    if (article is None) or (article.get('content') is None):
        return
    # 添加到全文RSS中
    fe = fg.add_entry()
    fe.id(url)
    fe.title(entry.title)
    fe.published(entry.published)
    fe.description(article.get('content'))
    auther = article.get('author')
    if (auther is not None):
        fe.author(auther)
    fe.link(href=url)

def gen_full_rss():
    rss_sources = get_rss_source()
    for feed_url in rss_sources:
        feed = feedparser.parse(feed_url)
        title = feed.feed.title
        print(title)
        # 生成全文RSS
        fg = FeedGenerator()
        href = f"http://127.0.0.1/{title}"
        fg.id(href)
        fg.title(feed.feed.title)
        fg.link(href=href, rel='self')
        fg.language('zh')
        fg.description(feed.feed.title)

        for entry in feed.entries:
            print(entry.link)
            add_entry_to_rss(entry, fg)

        # 保存全文RSS
        fg.rss_file(f"./rss/{title}.xml")


def get_rss_source():
    # 打开文件
    rss_sources = []
    with open('rss-source.txt', 'r') as f:
        # 逐行读取文件内容并遍历
        for line in f:
            # 处理每一行的内容
            print(line.strip())
            rss_sources.append(line.strip())
    return rss_sources


# 按间距中的绿色按钮以运行脚本。


def job():
    gen_full_rss()



class RSSRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="./rss", **kwargs)

import threading

if __name__ == '__main__':
    # set workdir to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RSSRequestHandler)
    httpd_thread = threading.Thread(target=httpd.serve_forever)
    httpd_thread.start()

    schedule.every(2).hours.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助

