# -*- coding:utf-8 -*-
__author__ = 'zhaojm'

import time, random
from permission import Permission
from permission import Rule
from flask import request, abort
from ..mredis import RedisClient


def get_admin_token(admin_id):
    t = time.time()
    r = random.uniform(100000, 200000)
    a = str(t) + str(admin_id)  # 保证唯一
    a += str(r)  # 保证安全
    return a


class NotUserException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AdminUserRule(Rule):
    # def base(self):
    #     return True

    def check(self):
        try:
            # print "in check admin user rule"
            admin_id = int(request.args.get("admin_id"))
            token = request.args.get("token")
            # print admin_id, token
            return RedisClient.check_admin_token(token, admin_id)
        except TypeError, e:
            print e
            return self.deny()

    def deny(self):
        print "deny..403"
        abort(403)


class AdminUserPermission(Permission):
    def rule(self):
        return AdminUserRule()


        # def test():
        #     print get_admin_token(1)
        #
        # test()
