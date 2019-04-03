from mongoengine import *
from .init_database import *


class WeiBoUser(Document):
    userId = IntField(required=True, unique=True)
    userNickName = StringField()
    weiBoNum = StringField()
    following = StringField()
    followers = StringField()
    filter = IntField()

    meta = {
        'collection': 'weibo_user',
        'indexes': ['userId']
    }

    @classmethod
    def add(cls, user_fild):
        # 使用 first() 方法在数据不存在的时候会返回 None
        item = WeiBoUser.objects(userId=user_fild['userId']).first()
        if not item:
            item = cls(**user_fild)
            item.save()
        return item