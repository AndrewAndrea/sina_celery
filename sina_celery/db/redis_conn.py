import redis


class URL_redis():
    def __init__(self):
        self.r = redis.Redis(host='127.0.0.1', port=6488, db=0, password='wjzj1217')

    def save_redis(self, key, value):
        # 使用redis的hash
        print(dict)
        self.r.hset("url_hash", key, value)

    def get_res_url(self, url):
        return self.r.hexists("url_hash", url)

    def save_set_url(self, url):
        self.r.sadd("set_url", url)

    def get_url(self):
        return self.r.spop('set_url')

    def is_null(self):
        return self.r.hlen('url_hash')


# 使用单例模式，避免多次创建对象
urlredis = URL_redis()
