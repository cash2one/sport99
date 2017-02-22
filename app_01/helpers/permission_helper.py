# coding=utf-8
__author__ = 'Van'
from permission import Permission
from permission import Rule
from flask import request, abort
from ..mredis import RedisClient
from .util_helper import is_manager


class NotUserException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UserRule(Rule):
    def check(self):
        try:
            # user_id = int(request.args.get("user_id"))
            # token = request.args.get("token")
            # return RedisClient.check_token(token, user_id)
            return True
        except TypeError, e:
            print e
            return self.deny()

    def deny(self):
        # flash('请先登录')
        return abort(403)


class AdminRule(Rule):
    def base(self):
        return UserRule()

    def check(self):
        try:
            # user_id = int(request.args.get("user_id"))
            # club_id = int(request.args.get("club_id"))
            # return is_manager(club_id, user_id)
            return True
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