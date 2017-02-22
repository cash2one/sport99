# coding=utf-8
__author__ = 'Van'

from flask import current_app
import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", '127.0.0.1')
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=0)

# 向redis里缓存用户信息 key:user_info field:user_id value:name;head_img_url
# redis> HSET myhash field1 "Hello"

USER_INFO_KEY = "user_info"
USER_OPENID = "user_openid"
TOKEN = "token"
TOKEN_EXPIRE_SECONDS = 3600 * 24 * 90  # 三个月
USER_ID = "user_id"
CLUB_ID = "club_id"
EVENT_ID = "event_id"
POST_ID = "post_id"
VENUE_ID = "venue_id"
COMPANY_ID = "company_id"
SMS_ID = 'sms_id'
SMS_CODE = "sms_code"
SMS_USER_TIMES = "sms_user_times"

redis_client.expire(SMS_USER_TIMES, 3600*2)
redis_client.expire(SMS_CODE, 300)
redis_client.expire(TOKEN, TOKEN_EXPIRE_SECONDS)


class RedisClient():

    def __init__(self):
        pass

    @staticmethod
    def clear_redis():
        """
        清理缓存，慎用
        """
        fkeys = redis_client.keys()
        for key in fkeys:
            redis_client.delete(key)

    @staticmethod
    def cache_wx_params(app_id, timestamp, nonce, signature):
        redis_client.set("app_id", app_id)
        redis_client.set("timestamp", timestamp)
        redis_client.set("nonce", nonce)
        redis_client.set("signature", signature)

    @staticmethod
    def cache_user(u_id, value):
        """
        缓存用户基本信息  key:id value:
        """
        return redis_client.hset(USER_INFO_KEY, u_id, value)

    @staticmethod
    def new_user_id():
        return redis_client.incr(USER_ID)

    @staticmethod
    def new_club_id():
        return redis_client.incr(CLUB_ID)

    @staticmethod
    def new_event_id():
        return redis_client.incr(EVENT_ID)

    @staticmethod
    def new_post_id():
        return redis_client.incr(POST_ID)

    @staticmethod
    def new_venue_id():
        return redis_client.incr(VENUE_ID)

    @staticmethod
    def new_company_id():
        return redis_client.incr(COMPANY_ID)

    @staticmethod
    def new_sms_id():
        return redis_client.incr(SMS_ID)

    @staticmethod
    def cache_sms_code(mobile, code):
        """
        缓存短信，一分钟有效
        """
        redis_client.hset(SMS_CODE, mobile, code)

    @staticmethod
    def get_sms_code(mobile):
        """
        缓存短信，一分钟有效
        """
        return redis_client.hget(SMS_CODE, mobile)

    @staticmethod
    def inc_user_sms_times(mobile):
        """
        限制用户10次发送验证码后两小时内不能再发
        """
        return redis_client.hincrby(SMS_USER_TIMES, mobile, 1)

    @staticmethod
    def get_user_from_cache(u_id):
        return redis_client.hget(USER_INFO_KEY, u_id)

    @staticmethod
    def cache_openid(open_id, value):
        """
        缓存用户微信信息  key:openid value: id|wx_nickname|wx_sex|wx_head_img_url
        """
        return redis_client.hset(USER_OPENID, open_id, value)

    @staticmethod
    def get_openid_from_cache(openid):
        return redis_client.hget(USER_OPENID, openid)

    @staticmethod
    def cache_token(token, user_id):
        """
        缓存用户token  key:token value: user_id
        """
        redis_client.hset(TOKEN, token, user_id)

    @staticmethod
    def check_token(token, user_id):
        return user_id == int(redis_client.hget(TOKEN, token))

    @staticmethod
    def get_wx_jsapi_ticket_from_cache():
        return redis_client.get("wx_jsapi_ticket")

    @staticmethod
    def set_wx_jsapi_ticket_from_cache(token, s):
        redis_client.set("wx_jsapi_ticket", token)
        redis_client.expire("wx_jsapi_ticket", s)