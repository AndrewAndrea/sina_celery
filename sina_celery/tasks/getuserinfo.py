#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import re
import requests
import traceback

from lxml import etree
from .celery_config import app
from sina_celery.db.weibo_user import WeiBoUser


cookie = {
    "Cookie": "你的cookie"
}


# 获取用户昵称
@app.task(ignore_result=True)
def get_user():
    user_id = 1549364094
    fiter = 1
    weibo_user = dict()
    try:
        url = "https://weibo.cn/%d/info" % user_id
        html = requests.get(url, cookies=cookie).content
        selector = etree.HTML(html)
        username = selector.xpath("//title/text()")[0]
        username = username[:-3]
        print(u"用户名: " + username)
        weibo_user['userId'] = user_id
        weibo_user['userNickName'] = username
        weibo_user['filter'] = fiter
        app.send_task('tasks.getuserinfo.get_user_info',
                      args=(weibo_user,),
                      queue='otherinfo',
                      routing_key='for_otherinfo')

    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取用户微博数、关注数、粉丝数
@app.task(ignore_result=True)
def get_user_info(weibo_user):
    try:
        url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
            weibo_user['userId'], weibo_user['filter'])
        html = requests.get(url, cookies=cookie).content
        selector = etree.HTML(html)
        pattern = r"\d+\.?\d*"

        # 微博数
        str_wb = selector.xpath(
            "//div[@class='tip2']/span[@class='tc']/text()")[0]
        guid = re.findall(pattern, str_wb, re.S | re.M)
        for value in guid:
            num_wb = int(value)
            break
        weibo_num = num_wb
        print(u"微博数: " + str(weibo_num))

        # 关注数
        str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
        guid = re.findall(pattern, str_gz, re.M)
        following = int(guid[0])
        print(u"关注数: " + str(following))

        # 粉丝数
        str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
        guid = re.findall(pattern, str_fs, re.M)
        followers = int(guid[0])
        print(u"粉丝数: " + str(followers))
        print(
            "===========================================================================")
        weibo_user['weiBoNum'] = str(weibo_num)
        weibo_user['following'] = str(following)
        weibo_user['followers'] = str(followers)
        WeiBoUser.add(weibo_user)
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()
