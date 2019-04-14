from mongoengine import *
from .init_database import *


class WeiBoComment(Document):

    userId = IntField(required=True)
    weibo_id = StringField(required=True)
    comment_id = StringField(required=True, unique=True)
    comment_content = StringField(default='')
    comment_userid = StringField(required=True)
    comment_username = StringField(default='')
    comment_like = StringField(default='')
    comment_time = StringField(default='')
    meta = {
        'collection': 'weibo_comment',
        'indexes': ['comment_id']
    }

    @classmethod
    def add(cls, comment_fild):
        item = WeiBoComment.objects(comment_id=comment_fild['comment_id']).first()
        print(item, 'item内容ID')
        if not item:
            item = cls(**comment_fild)
            item.save()
        return item