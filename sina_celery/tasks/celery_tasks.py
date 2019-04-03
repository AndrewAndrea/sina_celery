from get_username import get_user
from getuserinfo import get_user_info
from get_weibo_info import get_weibo_info
import traceback


get_user.delay()
get_user_info.delay()
get_weibo_info.delay()




