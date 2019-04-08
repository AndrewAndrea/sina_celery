import requests
import traceback

from lxml import etree
from .celery_config import app
cookie = {
    "Cookie": "SCF=Ah_hPPeAWzsVcWNL_hXTKlsY02uyImln6rRA5SjNV56b_rHKl8Qlq2qoeioZKpC8l2B5u8aYfZlD5BXAbmPCGxM.; _T_WM=d918d57b34bd39c1a86baaa7bf0c0b13; SUB=_2A25xn1d5DeRhGeNI61EQ8y3PzD2IHXVTYHkxrDV6PUJbkdAKLXKgkW1NSKGyUHU_XrMyQ6xqPs0W-tCCkfZgJbGt; SUHB=0gHiHrZqqLocQC; MLOGIN=1; XSRF-TOKEN=5177db; WEIBOCN_FROM=1110006030; M_WEIBOCN_PARAMS=luicode%3D20000174%26uicode%3D20000174"
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