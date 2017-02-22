# -*- coding:utf-8 -*-
__author__ = 'Van'

from utils import get_value_from_dict, require_value_from_dict
import time
from datetime import date


class BaseO():
    def as_json(self):
        pass


class User(BaseO):
    def __init__(self, user_arr, user_id):
        self.id = user_id
        self.mobile = require_value_from_dict(user_arr, "mobile")
        self.name = require_value_from_dict(user_arr, "name")
        self.sex = require_value_from_dict(user_arr, "sex")
        self.birthday = get_value_from_dict(user_arr, "birthday", None)
        self.city = get_value_from_dict(user_arr, "city", None)
        self.head_img_url = get_value_from_dict(user_arr, "head_img_url", None)
        self.password = ''
        self.clubs = []
        self.clusters = []
        self.devices = []
        self.messages = []
        self.wechat = {}
        self.create_time = int(time.time())

    def set_psw(self, p):
        self.password = p


class Club(BaseO):
    def __init__(self, club_arr, user_id):
        # self.id = int(require_value_from_dict(club_arr, "id"))  # 数字id，为关系型数据库
        self.name = require_value_from_dict(club_arr, "name")
        self.logo_url = get_value_from_dict(club_arr, "logo_url", "")
        self.bg_img_url = get_value_from_dict(club_arr, "bg_img_url", "")
        self.tags = get_value_from_dict(club_arr, "tags", "足球")
        # self.city = get_value_from_dict(club_arr, "city", "")
        self.bind_qq = get_value_from_dict(club_arr, "bind_qq", "")
        # 俱乐部创建者
        self.creator_id = user_id
        self.create_time = int(time.time())

        self.status = 0

        self.members_count = 1
        self.members = [{"id": user_id, "role": 0, "join_time": int(time.time())}]  # 俱乐部创始人

        self.events_count = 0
        self.follow_members_count = 0


class Event(BaseO):
    def __init__(self, arr, user_id, is_update=False):
        if not is_update:
            self.id = int(require_value_from_dict(arr, "id"))  # 数字id，为关系型数据库
            self.club_id = int(require_value_from_dict(arr, "club_id"))

            self.status = 0
            self.creator_id = user_id
            self.create_time = int(time.time())
            self.members_count = 0
            self.members_count_limit = int(get_value_from_dict(arr, "members_count_limit", 0))
            self.members = []  # 开始为空，创建者不一定是参加者
            self.type = "event"
        # 以下信息可修改
        self.name = require_value_from_dict(arr, "name")
        # 默认开放
        self.category = get_value_from_dict(arr, "category", u"足球")
        self.is_cycle = get_value_from_dict(arr, "is_cycle", "false")
        self.start_time = int(require_value_from_dict(arr, "start_time"))
        self.end_time = int(require_value_from_dict(arr, "end_time"))
        self.weekday = date.weekday(date.fromtimestamp(float(self.start_time)))
        if self.is_cycle == "true" and get_value_from_dict(arr, "days", False):
            self.days = []
            days = get_value_from_dict(arr, "days", "").split(',')
            for day in days:
                self.days.append(int(day))
        # 场馆信息
        self.venue = {
            "title": get_value_from_dict(arr, "venue_title", ""),
            "address": get_value_from_dict(arr, "venue_address", ""),
            "phone": get_value_from_dict(arr, "venue_phone", ""),
            "city": get_value_from_dict(arr, "venue_city", ""),
            "coordinate": [
                get_value_from_dict(arr, "venue_lng", 0),
                get_value_from_dict(arr, "venue_lat", 0)
            ]
        }
        self.fee = int(get_value_from_dict(arr, "fee", 0))
        self.is_aa = get_value_from_dict(arr, "is_aa", "true")
        self.place_num = get_value_from_dict(arr, "place_num", "")
        self.mobile = get_value_from_dict(arr, "mobile", 0)
        self.members_count_limit = int(get_value_from_dict(arr, "members_count_limit", 0))
        if arr.get("clusters"):
            self.clusters = arr.get("clusters").split(',')
        else:
            self.clusters = []
        self.introduce = get_value_from_dict(arr, "introduce", "")


class Venue():
    def __init__(self, arr, user_id):
        self.creator_id = user_id
        self.name = require_value_from_dict(arr, "name")
        self.area = require_value_from_dict(arr, "area")
        self.address = require_value_from_dict(arr, "address")
        self.city = get_value_from_dict(arr, "city", "北京")
        self.lat = require_value_from_dict(arr, "lat")
        self.lng = require_value_from_dict(arr, "lng")
        self.phone = get_value_from_dict(arr, "phone", "")
        self.way = get_value_from_dict(arr, "way", "")


# # 活动关联QQ群
# class EventCluster():
#     __tablename__ = 'activity_clusters'
#     id = db.Column(db.Integer, primary_key=True)
#     activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), index=True)
#     cluster_id = db.Column(db.String(12), db.ForeignKey('clusters.external_id'), index=True)
#
#     status = db.Column(db.Integer, default=0)
#     pass


# class Robot(db.Model):
#     __tablename__ = 'robots'
#     id = db.Column(db.Integer, primary_key=True)
#     qq = db.Column(db.String(12), unique=True, index=True)
#
#     status = db.Column(db.Integer, default=0)
#
#     def __repr__(self):
#         return '<Robot id=%r, qq=%r>' % (self.id, self.qq)
#
#     pass


class Cluster(BaseO):
    def __init__(self, arr, qq):
        self.external_id = require_value_from_dict(arr, 'external_id')
        self.robots = []
        # self.robot1_id = require_value_from_dict('robots_id')
        # self.robot2_id = require_value_from_dict('robots_id')
        self.name = require_value_from_dict('name')
        self.creator_qq = qq
        self.members = []
        # self.events = []
        self.status = 0

        # description = db.Column(db.String(15))
        # g_crt_time = db.Column(db.INT)
        # g_level = db.Column(db.Integer)
        # g_max_mem = db.Column(db.Integer)
        # g_mem_num = db.Column(db.Integer)
        # group_id = db.Column(db.Integer)
        # last_members_time = db.Column(db.INT)

    def __repr__(self):
        return '<Cluster %r>' % self.name


# class ClusterMember(db.Model):
#     __tablename__ = 'cluster_members'
#     id = db.Column(db.Integer, primary_key=True)
#     qq = db.Column(db.String(12), index=True)
#     external_id = db.Column(db.String(12), db.ForeignKey('clusters.external_id'), index=True)
#     nick = db.Column(db.String(15))
#     is_admin = db.Column(db.Boolean, default=False)
#     # q_age = db.Column(db.Integer)
#     card = db.Column(db.String(15), nullable=True)
#     # black = db.Column(db.Boolean)
#     # join_time = db.Column(db.INT)
#     # last_time = db.Column(db.INT)
#     # level = db.Column(db.Integer)
#     # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
#
#     status = db.Column(db.Integer, default=0)
#
#     def __repr__(self):
#         return '<ClusterMember %r>' % self.nick
#
#     pass


# class QQUser(BaseO):
#
#     def __init__(self, arr, qq):
#         self.qq = qq
#         self.nick_name = require_value_from_dict(arr, 'nick_name')
#         # address = db.Column(db.String(30))
#         # age = db.Column(db.Integer)
#         # area = db.Column(db.String)
#         self.birthday = require_value_from_dict(arr, 'birthday')
#         # email = db.Column(db.String(30))
#         # en_name = db.Column(db.String(15))
#         # gender = db.Column(db.String(1))
#         # group_id = db.Column(db.Integer)
#         # gu_xiang = db.Column(db.String(15))
#         # header = db.Column(db.String(15))
#         # home_page = db.Column(db.String(30))
#         # intro = db.Column(db.String(30))
#         # ip = db.Column(db.String(30))
#         # level = db.Column(db.Integer)
#         # mobile = db.Column(db.Integer)
#         # name = db.Column(db.String(15))
#         # phone = db.Column(db.Integer)
#         # qq_age = db.Column(db.Integer)
#         # qq_status = db.Column(db.Integer)
#         # remark = db.Column(db.String(15))
#         # school = db.Column(db.String(15))
#         # sheng_xiao = db.Column(db.String(2))
#         # signature = db.Column(db.String(15))
#         # tag = db.Column(db.Integer)
#         # work = db.Column(db.String(15))
#         # xing_zuo = db.Column(db.Integer)
#         # xue_li = db.Column(db.String)
#         # zip_code = db.Column(db.Integer)
#
#         self.status = 0


class QQBindCode():
    def __init__(self, arr, qq):
        self.qq = qq
        self.user_id = require_value_from_dict(arr, 'user_id')
        self.code = require_value_from_dict(arr, 'code')  # "YD99"
        self.create_time = require_value_from_dict(arr, 'create_time')


class Area(BaseO):
    def __init__(self, arr):
        self.pin_yin = require_value_from_dict(arr, 'pin_yin')
        self.code = require_value_from_dict(arr, 'cdoe')
        self.name = require_value_from_dict(arr, 'name')


# =========admin==========
class AdminUser(BaseO):
    def __init__(self, arr):
        self.id = int(require_value_from_dict(arr, 'id'))
        self.username = require_value_from_dict(arr, 'username')
        self.password = require_value_from_dict(arr, 'password')
        self.club_id_list = []
