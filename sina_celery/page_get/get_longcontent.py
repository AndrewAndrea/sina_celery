import requests
from sina_celery.config import settings

cookie = settings.cookie
headers = settings.HEADERS


def get_long_content(weibo_link):

    html = requests.get(weibo_link, cookies=cookie, headers=headers).content
    return html
