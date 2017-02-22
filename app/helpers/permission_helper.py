# coding=utf-8
__author__ = 'Van'
from permission import Permission
from permission import Rule
from flask import request, current_app, abort
from .util_helper import is_manager
import time
import hashlib


class NotUserException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UserRule(Rule):
    def check(self):
        try:
            user_id = int(request.args.get("user_id"))
            token = request.args.get("token")
            return True
        except TypeError, e:
            return self.deny()

    def deny(self):
        # flash('请先登录')
        return abort(403)


class AdminRule(Rule):
    def base(self):
        return UserRule()

    def check(self):
        try:
            user_id = int(request.args.get("user_id"))
            club_id = int(request.args.get("club_id"))
            return is_manager(club_id, user_id)
        except TypeError, e:
            print e
            return self.deny()

    def deny(self):
        print "not manager"
        abort(403)


class UserPermission(Permission):
    def rule(self):
        return UserRule()


class AdminPermission(Permission):
    def rule(self):
        return AdminRule()


def create_token(user_id):
    # 生成Token
    timestamp = int(time.time())
    nonce = current_app.config.get("WECHAT_NONCE")
    token = current_app.config.get("WECHAT_TOKEN")

    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = "%s%s%s" % tuple(tmp_list)
    hash_sha1 = hashlib.sha1(tmp_str)
    user_token = hash_sha1.hexdigest()
    # 缓存token到user_id的映射
    # RedisClient.cache_token(user_token, user_id)
    return user_token