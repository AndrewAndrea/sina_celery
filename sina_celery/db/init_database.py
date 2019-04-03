from mongoengine import connect


# init mongodb, redis
connect(host='127.0.0.1', port=26178, db='weibo', connect=False, username='andrew', password='wjzj1217')
