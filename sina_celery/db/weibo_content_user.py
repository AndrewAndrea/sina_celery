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
    # isDisable = IntField(default=0)

    meta = {
        'collection': 'weibo_content_user',
        'indexes': ['contentId']
    }

    @classmethod
    def add(cls, content_fild):
        print(content_fild['contentId'], 'content_id888888888888888888888888888')
        item = WeiBoContentUser.objects(contentId=content_fild['contentId']).first()
        print(item, 'item内容ID')
        if not item:
            item = cls(**content_fild)
            item.save()
        return item