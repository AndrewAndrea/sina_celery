import requests
from sina_celery.db.redis_conn import urlredis
from sina_celery.config import settings

cookie = settings.cookie
headers = settings.HEADERS

user_id = 1594199381
filter = 1


def get_content():

    url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
        user_id, filter)
    html = requests.get(url, cookies=cookie, headers=headers).content
    return html


def get_page_content(page):
    url2 = "https://weibo.cn/u/%d?filter=%d&page=%d" % (
        user_id, filter, page)
    # 保存到redis的set集合数据库
    urlredis.save_set_url(url2)
    print(urlredis.is_null())
    if urlredis.is_null() == 0:
        url2 = urlredis.get_url()
        html2 = requests.get(url2, cookies=cookie, headers=headers).content
        if html2:
            # 该url已请求
            print('请求完成，保存到已响应')
            urlredis.save_redis(url2, 'u')
        return html2
    if not urlredis.get_res_url(url2):
        url2 = urlredis.get_url()
        html2 = requests.get(url2, cookies=cookie, headers=headers).content
        if html2:
            # 该url已请求
            print('请求完成，保存到已响应')
            urlredis.save_redis(url2, 'u')
        return html2
    else:
        return
