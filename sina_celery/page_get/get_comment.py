#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
from sina_celery.config import settings

from sina_celery.db.redis_conn import urlredis
cookie = settings.cookie
headers = settings.HEADERS


def get_comment(url):
    if not urlredis.get_res_url(url):
        # url2 = urlredis.get_url()
        response = requests.get(url, cookies=cookie,
                                headers=headers)
        html = response.text
        if html:
            # 该url已请求
            print('请求完成，保存到已响应')
            urlredis.save_redis(url, 'c')
        return html
    else:
        return



