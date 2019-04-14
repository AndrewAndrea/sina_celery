#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import re

import requests
import traceback

from datetime import datetime
from datetime import timedelta

from lxml import etree
from bs4 import BeautifulSoup

from .celery_config import app
from sina_celery.db.weibo_content_user import WeiBoContentUser
from sina_celery.db.weibo_comment import WeiBoComment

from sina_celery.page_get.get_longcontent import get_long_content
from sina_celery.parse_content.content_parse import parse_content
from sina_celery.page_get.get_comment import get_comment


# 获取用户微博信息
@app.task(ignore_result=True)
def get_weibo_info():
    user_id = 1594199381
    try:
        pattern = r"\d+\.?\d*"
        infos = parse_content()
        for info in infos:
            # info = next(parse_content())
            # 微博内容
            content, weibo_id = get_weibo_content(info)
            # 微博位置
            palce = get_weibo_place(info)
            # 微博发布时间
            publish_time = get_publish_time(info)
            # 微博发布工具
            publish_tool = get_publish_tool(info)
            str_footer = info.xpath("div")[-1]
            str_footer = str_footer.xpath("string(.)")
            str_footer = str_footer[str_footer.rfind(u'赞'):]
            guid = re.findall(pattern, str_footer, re.M)
            # 点赞数
            up_num = int(guid[0])
            # 转发数
            retweet_num = int(guid[1])
            # 评论数
            comment_num = int(guid[2])
            print(comment_num, '评论数量-----------------------------')
            if comment_num != 0:
                print(user_id)
                comment_url = 'https://weibo.cn/comment/%s?uid=%d&rl=0#cmtfrm' % (weibo_id, user_id)
                app.send_task('tasks.get_weibo_info.parse_comment',
                              args=(comment_url, weibo_id, user_id,),
                              queue='weiboinfo',
                              routing_key='for_weiboinfo')
            WeiBoContentUser.add(user_id, weibo_id + str(user_id), content, publish_time, retweet_num, up_num,
                                 comment_num, publish_tool, palce)

    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取微博内容
def get_weibo_content(info):
    weibo_content_list = []
    try:
        str_t = info.xpath("div/span[@class='ctt']")
        weibo_content = str_t[0].xpath("string(.)").replace(u"\u200b", "")
        weibo_id = info.xpath("@id")[0][2:]
        a_link = info.xpath("div/span[@class='ctt']/a")
        is_retweet = info.xpath("div/span[@class='cmt']")
        # if a_link:
        #     if a_link[-1].xpath("text()")[0] == u"全文":
        #         weibo_link = "https://weibo.cn/comment/" + weibo_id
        #         wb_content = get_long_weibo(weibo_link)
        #         if wb_content:
        #             if not is_retweet:
        #                 wb_content = wb_content[1:]
        #             weibo_content = wb_content
        if is_retweet:
            weibo_content = get_retweet(
                is_retweet, info, weibo_content)
        weibo_content_list.append(weibo_content)
        return weibo_content, weibo_id
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取微博发布位置
def get_weibo_place(info):
    try:
        div_first = info.xpath("div")[0]
        a_list = div_first.xpath("a")
        weibo_place = u"无"
        for a in a_list:
            if ("place.weibo.com" in a.xpath("@href")[0] and
                    a.xpath("text()")[0] == u"显示地图"):
                weibo_a = div_first.xpath("span[@class='ctt']/a")
                if len(weibo_a) >= 1:
                    weibo_place = weibo_a[-1]
                    if u"的秒拍视频" in div_first.xpath("span[@class='ctt']/a/text()")[-1]:
                        if len(weibo_a) >= 2:
                            weibo_place = weibo_a[-2]
                        else:
                            weibo_place = u"无"
                    weibo_place = weibo_place.xpath("string(.)")
                    break

        print(u"微博位置: " + weibo_place)
        return weibo_place
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取微博发布时间
def get_publish_time(info):
    try:
        str_time = info.xpath("div/span[@class='ct']")
        str_time = str_time[0].xpath("string(.)")
        publish_time = str_time.split(u'来自')[0]
        if u"刚刚" in publish_time:
            publish_time = datetime.now().strftime(
                '%Y-%m-%d %H:%M')
        elif u"分钟" in publish_time:
            minute = publish_time[:publish_time.find(u"分钟")]
            minute = timedelta(minutes=int(minute))
            publish_time = (datetime.now() - minute).strftime(
                "%Y-%m-%d %H:%M")
        elif u"今天" in publish_time:
            today = datetime.now().strftime("%Y-%m-%d")
            time = publish_time[3:]
            publish_time = today + " " + time
        elif u"月" in publish_time:
            year = datetime.now().strftime("%Y")
            month = publish_time[0:2]
            day = publish_time[3:5]
            time = publish_time[7:12]
            publish_time = (year + "-" + month + "-" + day + " " + time)
        else:
            publish_time = publish_time[:16]
        print(u"微博发布时间: " + publish_time)
        return publish_time
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取微博发布工具
def get_publish_tool(info):
    try:
        str_time = info.xpath("div/span[@class='ct']")
        str_time = str_time[0].xpath("string(.)")
        if len(str_time.split(u'来自')) > 1:
            publish_tool = str_time.split(u'来自')[1]
        else:
            publish_tool = u"无"
        return publish_tool
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取"长微博"全部文字内容
def get_long_weibo(weibo_link):
    try:
        html = get_long_weibo(weibo_link)
        selector = etree.HTML(html)
        info = selector.xpath("//div[@class='c']")[1]
        wb_content = info.xpath("div/span[@class='ctt']")[0].xpath("string(.)").replace(u"\u200b", "")
        return wb_content
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取转发微博信息
def get_retweet(is_retweet, info, wb_content):
    try:
        original_user = is_retweet[0].xpath("a/text()")
        if not original_user:
            wb_content = u"转发微博已被删除"
            return wb_content
        else:
            original_user = original_user[0]
        retweet_reason = info.xpath("div")[-1].xpath("string(.)").replace(u"\u200b", "")
        retweet_reason = retweet_reason[:retweet_reason.rindex(u"赞")]
        wb_content = (retweet_reason + "\n" + u"原始用户: " +
                      original_user + "\n" + u"转发内容: " + wb_content)
        return wb_content
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

@app.task(ignore_result=True)
def parse_comment(comment_url, weibo_id, user_id):
    """
    获取评论内容
    :param user_id:
    :param weibo_id:
    :return:
    """
    comment_field = dict()
    try:
        html = get_comment(comment_url)

        soup = BeautifulSoup(html, "html.parser", from_encoding="utf8")
        comments = soup.find_all("div", {"class": "c"})
        for c in comments:
            try:
                comment_field['userId'] = user_id
                comment_field['weibo_id'] = weibo_id
                comment_field['userName'] = c.find("a").text
                comment_field['comment_userid'] = c.find("a").get("href").split('/')[-1]
                comment_field['comment_content'] = c.find("span", {"class": "ctt"}).get_text()
                comment_field['comment_id'] = str(c.get("id"))
                comment_field['commentLike'] = c.find("span", {"class": "cc"}).find("a").text
                comment_field['commentTime'] = c.find("span", {"class": "ct"}).text.strip()
                print(comment_field)
                WeiBoComment.add(comment_field)
            except:
                pass
            next_url = None
            try:
                next_url = soup.find("div", {"id": "pagelist"}).find("form").find("a", text=r'下页').get("href")
            except:
                pass
            print(next_url, '有没有下一页')
            if next_url:
                print('https://weibo.cn' + next_url, '88888888888888888888888')
                parse_comment('https://weibo.cn''有没有下一页', weibo_id, user_id)
                # app.send_task('tasks.get_weibo_info.parse_comment',
                #               args=('https://weibo.cn'.join(next_url), weibo_id, user_id,),
                #               queue='weiboinfo',
                #               routing_key='for_weiboinfo')
                # yield parse_comment('https://weibo.cn'.join(next_url), weibo_id, user_id)
            else:
                pass
    except Exception as e:
        print('出现异常' + str(e))
        print('微博id' + weibo_id)
        # res_text = requests.get('https://weibo.cn/comment/%s?uid=%d&rl=0#cmtfrm' % (weibo_id, user_id), cookies=cookie,
        #                         headers=headers)
        # # pattern = '<a.*?href="(.+)".*?>(.*?)</a>'
        # with open('commecnt.html', 'w', encoding='utf8') as f:
        #     f.write(res_text.text)
# for url in urls:
#     if 'filter' in url:
#         urls.remove(url)
# print(urls, '----------------------')
# ids = selector.xpath("//div[@class='c']/@id")
# for m_id in ids:
#     if 'M_' in m_id:
#         ids.remove(m_id)
# contents = selector.xpath('//div[@class="c"]/span[@class="ctt"]')
# for comm in range(len(ids)):
#     comment_content = contents[comm].xpath('string(.)')
#     comment_field['userId'] = user_id
#     comment_field['weibo_id'] = weibo_id
#     comment_field['comment_id'] = ids[comm]
#     comment_field['comment_content'] = comment_content
#     comment_field['comment_userid'] = urls[comm].split('/')[-1]
#     WeiBoComment.add(comment_field)
