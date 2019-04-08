import os
from datetime import timedelta
import sys

sys.path.insert(0, '..')
from celery import Celery, platforms
# from config.conf import BROKER, BACKEND
from kombu import Exchange, Queue

BROKER = 'amqp://guest@localhost//'
# result_backend = 'db+mongoengine://andrew:wjzj1217@localhost/weibo'

platforms.C_FORCE_ROOT = True

tasks = [
    # 'tasks.get_username',
    'tasks.get_weibo_info',
    'tasks.getuserinfo',
]

app = Celery('sina_celery', include=tasks, broker=BROKER)

app.conf.update(
    CELERY_TIMEZONE='Asia/Shanghai',
    CELERY_ENABLE_UTC=True,

    # CELERY_RESULT_BACKEND='mongodb://andrew:wjzj1217@localhost:26178/weibo',
    # CELERY_RESULT_BACKEND_SETTINGS={
    #     # "host": "127.0.0.1",
    #     # "port": 26178,
    #     # "database": "weibo",
    #     # "username": "andrew",
    #     # "password": "wjzj1217",
    #     "taskmeta_collection": "weibo_user",
    # },

    CELERYBEAT_SCHEDULE={
        # 'user_task': {
        #     'task': 'tasks.get_username.get_user',
        #     'schedule': timedelta(seconds=10000),
        #     'options': {'queue': 'user_info', 'routing_key': 'for_userinfo'}
        # },
        'weiboinfo_task': {
            'task': 'tasks.get_weibo_info.get_weibo_info',
            'schedule': timedelta(seconds=10000),
            'options': {'queue': 'weiboinfo', 'routing_key': 'for_weiboinfo'}
        },
        'info_other_task': {
            'task': 'tasks.getuserinfo.get_user',
            'schedule': timedelta(seconds=10000),
            'options': {'queue': 'otherinfo', 'routing_key': 'for_otherinfo'}
        },
    },
    CELERY_QUEUES=(
        # Queue('user_info', exchange=Exchange('user_info', type='direct'),
        #       routing_key='for_userinfo'),
        Queue('weiboinfo', exchange=Exchange('weiboinfo', type='direct'),
              routing_key='for_weiboinfo'),
        Queue('otherinfo', exchange=Exchange('otherinfo', type='direct'),
              routing_key='for_otherinfo'),
    )
)
