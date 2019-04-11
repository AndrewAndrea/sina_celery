from mongoengine import *
from .init_database import *


class WeiBoContentUser(Document):
    userId = IntField(required=True)
    contentId = StringField(required=True, unique=True)
    content = StringField(default='')
    publishTime = StringField(default='')
    retweetNumber = IntField(default=0)
    likeNumber = IntField(default=0)
    commentNumber = IntField(default=0)
    publistTool = StringField(default='')
    weiBoPlace = StringField(default='')

    meta = {
        'collection': 'weibo_content_user',
        'indexes': ['contentId']
    }

    @classmethod
    def add(cls, user_id, content_id, content, publish_time, retweet_number, like_number, comment_number, publist_tool,
            weibo_place):
        item = WeiBoContentUser.objects(contentId=content_id).first()
        if not item:
            weibocontent = dict()
            weibocontent['userId'] = user_id
            weibocontent['contentId'] = content_id
            weibocontent['content'] = content
            weibocontent['publishTime'] = publish_time
            weibocontent['retweetNumber'] = retweet_number
            weibocontent['likeNumber'] = like_number
            weibocontent['commentNumber'] = comment_number
            weibocontent['publistTool'] = publist_tool
            weibocontent['weiBoPlace'] = weibo_place
            item = cls(**weibocontent)
            try:
                item.save()
            except Exception as e:
                print(str(e) + '保存到数据库出错')
