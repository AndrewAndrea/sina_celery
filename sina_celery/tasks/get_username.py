import requests
import traceback

from lxml import etree
from .celery_config import app
cookie = {
    "Cookie": "你的cookie"
}


# 获取用户昵称
@app.task(ignore_result=True)
def get_user():
    try:
        url = "https://weibo.cn/%d/info" % 6193466450
        html = requests.get(url, cookies=cookie).content
        selector = etree.HTML(html)
        username = selector.xpath("//title/text()")[0]
        username = username[:-3]
        print(u"用户名: " + username)
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()
