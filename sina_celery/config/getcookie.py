import requests
from settings import HEADERS


cookie = {
    'Cookie': '_T_WM=d918d57b34bd39c1a86baaa7bf0c0b13; login=f307b93959f45c1c0f0ff1ca6bca5b9a; WEIBOCN_FROM=1110005030'
}

data = {
    'username': 'zhao.jia.andrew@gmail.com',
    'password': 'wjzj1217',
    'savestate': '1',
    'r': 'https://m.weibo.cn/',
    'ec': '0',
    'pagerefer': 'https://m.weibo.cn/login?backURL=https%253A%252F%252Fm.weibo.cn%252F',
    'entry': 'mweibo',
}
res = requests.post('https://passport.weibo.cn/sso/login',
                   headers=HEADERS, cookies=cookie, data=data)
print(res.status_code)
print(res.cookies)
cookies = requests.utils.dict_from_cookiejar(res.cookies)
print(cookies)

