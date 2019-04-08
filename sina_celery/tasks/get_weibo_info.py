import sys
import re

import requests
import traceback

from datetime import datetime
from datetime import timedelta

from lxml import etree
from tqdm import tqdm

from .celery_config import app
from sina_celery.db.weibo_content_user import WeiBoContentUser
from sina_celery.db.weibo_comment import WeiBoComment

cookie = {
    "Cookie": "SCF=Ah_hPPeAWzsVcWNL_hXTKlsY02uyImln6rRA5SjNV56b_rHKl8Qlq2qoeioZKpC8l2B5u8aYfZlD5BXAbmPCGxM.; _T_WM=d918d57b34bd39c1a86baaa7bf0c0b13; SUB=_2A25xn1d5DeRhGeNI61EQ8y3PzD2IHXVTYHkxrDV6PUJbkdAKLXKgkW1NSKGyUHU_XrMyQ6xqPs0W-tCCkfZgJbGt; SUHB=0gHiHrZqqLocQC; MLOGIN=1; XSRF-TOKEN=5177db; WEIBOCN_FROM=1110006030; M_WEIBOCN_PARAMS=luicode%3D20000174%26uicode%3D20000174"
}


# 获取用户微博信息
@app.task(ignore_result=True)
def get_weibo_info():
    weibo_num2 = 0
    weibo_num = 0
    up_num_list = []
    comment_num_list = []
    retweet_num_list = []
    weibocontent = dict()
    user_id = 1805357121
    filter = 1
    try:
        url = "https://weibo.cn/u/%d?filter=%d&page=1" % (
            user_id, filter)
        html = requests.get(url, cookies=cookie).content
        selector = etree.HTML(html)
        if selector.xpath("//input[@name='mp']") == []:
            page_num = 1
        else:
            page_num = (int)(selector.xpath(
                "//input[@name='mp']")[0].attrib["value"])
        pattern = r"\d+\.?\d*"
        for page in tqdm(range(1, page_num + 1), desc=u"进度"):
            url2 = "https://weibo.cn/u/%d?filter=%d&page=%d" % (
                user_id, filter, page)
            # requests.get(url2, cookies=cookie)
            html2 = requests.get(url2, cookies=cookie).content
            selector2 = etree.HTML(html2)
            info = selector2.xpath("//div[@class='c']")
            is_empty = info[0].xpath("div/span[@class='ctt']")
            if is_empty:
                for i in range(0, len(info) - 2):
                    # 微博内容
                    content, weibo_id = get_weibo_content(info[i])
                    # 微博位置
                    palce = get_weibo_place(info[i])
                    # 微博发布时间
                    publish_time = get_publish_time(info[i])
                    # 微博发布工具
                    publish_tool = get_publish_tool(info[i])
                    str_footer = info[i].xpath("div")[-1]
                    str_footer = str_footer.xpath("string(.)")
                    str_footer = str_footer[str_footer.rfind(u'赞'):]
                    guid = re.findall(pattern, str_footer, re.M)
                    # 点赞数
                    up_num = int(guid[0])
                    up_num_list.append(up_num)
                    # 转发数
                    retweet_num = int(guid[1])
                    retweet_num_list.append(retweet_num)
                    # 评论数
                    comment_num = int(guid[2])
                    comment_num_list.append(comment_num)
                    if comment_num != 0:
                        app.send_task('tasks.get_weibo_info.get_comment',
                                      args=(user_id, weibo_id, ),
                                      queue='weiboinfo',
                                      routing_key='for_weiboinfo')
                        # get_comment(user_id, weibo_id)
                    weibo_num2 += 1
                    weibocontent['userId'] = user_id
                    weibocontent['contentId'] = weibo_id + str(user_id)
                    weibocontent['content'] = content
                    weibocontent['publishTime'] = publish_time
                    weibocontent['retweetNumber'] = retweet_num
                    weibocontent['likeNumber'] = up_num
                    weibocontent['commentNumber'] = comment_num
                    weibocontent['publistTool'] = publish_tool
                    weibocontent['weiBoPlace'] = palce
                    item = WeiBoContentUser.add(weibocontent)
                    print(item)
        if not filter:
            print(u"共" + str(weibo_num2) + u"条微博")
        else:
            print(u"共" + str(weibo_num) + u"条微博，其中" +
                  str(weibo_num2) + u"条为原创微博"
                  )
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
    weibo_place_list = []
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

        weibo_place_list.append(weibo_place)
        print(u"微博位置: " + weibo_place)
        return weibo_place
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取微博发布时间
def get_publish_time(info):
    publish_time_list = []
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
        publish_time_list.append(publish_time)
        print(u"微博发布时间: " + publish_time)
        return publish_time
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


# 获取微博发布工具
def get_publish_tool(info):
    publish_tool_list = []
    try:
        str_time = info.xpath("div/span[@class='ct']")
        str_time = str_time[0].xpath("string(.)")
        if len(str_time.split(u'来自')) > 1:
            publish_tool = str_time.split(u'来自')[1]
        else:
            publish_tool = u"无"
        publish_tool_list.append(publish_tool)
        print(u"微博发布工具: " + publish_tool)
        return publish_tool
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()

# 获取"长微博"全部文字内容
def get_long_weibo(weibo_link):
    try:
        html = requests.get(weibo_link, cookies=cookie).content
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
def get_comment(user_id, weibo_id):
    """
    获取评论内容
    :param user_id:
    :param weibo_id:
    :return:
    """
    comment_field = dict()
    res = requests.get('https://weibo.cn/comment/%s?uid=%d&rl=0#cmtfrm' % (weibo_id, user_id), cookies=cookie).content
    selector = etree.HTML(res)
    urls = selector.xpath("//div[@class='c']/a[1]/@href")
    for url in urls:
        if 'filter' in url:
            urls.remove(url)
    ids = selector.xpath("//div[@class='c']/@id")
    for m_id in ids:
        if 'M_' in m_id:
            ids.remove(m_id)
    contents = selector.xpath('//div[@class="c"]/span[@class="ctt"]')
    for comm in range(len(ids)):
        comment_content = contents[comm].xpath('string(.)')
        comment_field['userId'] = user_id
        comment_field['weibo_id'] = weibo_id
        comment_field['comment_id'] = ids[comm]
        comment_field['comment_content'] = comment_content
        comment_field['comment_userid'] = urls[comm].split('/')[-1]
        WeiBoComment.add(comment_field)

