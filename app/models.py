# coding=utf-8
__author__ = 'zhaojm'

from app import db,db_session
from app.utils.common import require_value_from_dict,get_value_from_dict
from flask.ext.login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from . import login_manager
import time

# 活动地点
class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))  # 场馆名称
    address = db.Column(db.String(128))  # 场馆地点
    coordinate_lng = db.Column(db.String(20))  # 坐标经度
    coordinate_lat = db.Column(db.String(20))  # 坐标纬度
    category = db.Column(db.String(6))  # 场馆类别
    province = db.Column(db.String(15))  # 省
    city = db.Column(db.String(15))  # 市
    region = db.Column(db.String(15))  # 区域
    link_man_name = db.Column(db.String(10))  # 联系人
    link_man_mobile = db.Column(db.String(13))  # 联系方式

    status = db.Column(db.Integer, default=0)

    def __init__(self, venue_arr):
        self.name = require_value_from_dict(venue_arr,"venue_title")
        self.address = require_value_from_dict(venue_arr,"venue_address")
        self.coordinate_lng = float(require_value_from_dict(venue_arr,"venue_lng"))
        self.coordinate_lat = float(require_value_from_dict(venue_arr,"venue_lat"))
        self.category = require_value_from_dict(venue_arr,"category")
        self.province = get_value_from_dict(venue_arr,"province",'')
        self.city = get_value_from_dict(venue_arr,"venue_city",'')
        self.region = get_value_from_dict(venue_arr,"region",'')
        self.link_man_name = get_value_from_dict(venue_arr,"link_man_name",'')
        self.link_man_mobile = get_value_from_dict(venue_arr,"link_man_mobile",'')


# 活动实体
class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(15))  # 类别
    name = db.Column(db.String(30), index=True)  # 标题
    start_time = db.Column(db.INT)  # 开始时间
    end_time = db.Column(db.INT)  # 结束时间
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))  # 场馆
    fee = db.Column(db.Integer)  # 花费
    is_aa = db.Column(db.Integer)  # 是否aa
    member_count_limit = db.Column(db.INT)  # 活动人数
    place_num = db.Column(db.String(50))  # 场地号
    mobile = db.Column(db.String(50))  # 电话
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'))  # 俱乐部
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建者

    sign = db.Column(db.String(5))  # 报名标示
    status = db.Column(db.Integer, default=0)  # 活动状态 0：正常 1：结束 2：取消

    # 业务冗余
    member_count = db.Column(db.INT)  # 当前报名人数
    week = db.Column(db.Integer)  # 星期几，用于排序

    def __init__(self, activity_arr):
        if activity_arr:
            self.id = int(require_value_from_dict(activity_arr,"id"))
            self.category = require_value_from_dict(activity_arr,"category")
            self.name = require_value_from_dict(activity_arr,"name")
            self.start_time = int(time.mktime(time.strptime(require_value_from_dict(activity_arr,"start_time"),'%Y-%m-%d %H:%M')))
            self.end_time = int(time.mktime(time.strptime(require_value_from_dict(activity_arr,"end_time"),'%Y-%m-%d %H:%M')))
            self.fee = int(require_value_from_dict(activity_arr,"fee"))
            is_aa = get_value_from_dict(activity_arr,"is_aa",None)
            if is_aa == "true":
                self.is_aa = 0
            else:
                self.is_aa = 1
            self.member_count_limit = int(require_value_from_dict(activity_arr,"members_count_limit"))
            self.place_num = require_value_from_dict(activity_arr,"place_num")
            self.mobile = get_value_from_dict(activity_arr,"mobile",'')
            self.club_id = int(require_value_from_dict(activity_arr,"club_id"))
            #self.creator_id = int(require_value_from_dict(activity_arr,"creator_id"))



# 周期活动
class CycleActivity(db.Model):
    __tablename__ = 'cycle_activities'
    id = db.Column(db.Integer, primary_key=True)  # id
    category = db.Column(db.String(15))  # 类别
    name = db.Column(db.String(30), index=True)  # 标题
    start_time = db.Column(db.INT)  # 开始时间
    end_time = db.Column(db.INT)  # 结束时间
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))  # 地点
    foo = db.Column(db.Integer)  # 花费
    is_aa = db.Column(db.Boolean, default=False)  # 是否aa
    member_count = db.Column(db.Integer)  # 活动人数
    place_num = db.Column(db.String(50))  # 场地号
    mobile = db.Column(db.String(50))  # 电话
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'))  # 俱乐部
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建者

    week = db.Column(db.Integer)  # 星期
    enable = db.Column(db.Integer)  # 是否可用

    status = db.Column(db.Integer)


# 俱乐部
class Club(db.Model):
    __tablename__ = 'clubs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    head_url = db.Column(db.String(90))
    tags = db.Column(db.String(30))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    status = db.Column(db.Integer, default=0)  # 0: 正常可用, -1: 已删除

    def __init__(self, club_arr):
        if club_arr:
            self.name = require_value_from_dict(club_arr,"name")
            self.tags = require_value_from_dict(club_arr,"tags")
            self.head_url = get_value_from_dict(club_arr,"head_url",'')
            self.creator_id = require_value_from_dict(club_arr,"user_id")

# 俱乐部成员
class ClubMember(db.Model):
    __tablename__ = 'club_members'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), index=True)

    status = db.Column(db.Integer, default=0)  # 0: 正常可用, -1: 已删除


# 活动报名人员
class ActivityMember(db.Model):
    __tablename__ = 'activity_members'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), index=True)  # 活动id

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 报名用户
    user_temp = db.Column(db.String(90), default='')  # 报名用户临时（只有一个名称标示）

    num = db.Column(db.Integer, default=0)  # 报名总人数
    help_qq = db.Column(db.String(12), default=-1)  # 帮忙报名的人

    channel = db.Column(db.String(10))  # 渠道    qq 或者  weixin

    status = db.Column(db.Integer, default=0)


# 活动关联QQ群
class ActivityCluster(db.Model):
    __tablename__ = 'activity_clusters'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), index=True)
    cluster_id = db.Column(db.String(12), db.ForeignKey('clusters.external_id'), index=True)

    status = db.Column(db.Integer, default=0)
    pass


# 平台用户
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    head_url = db.Column(db.String(300))
    nick = db.Column(db.String(15), index=True)
    sex = db.Column(db.String(1))
    interest = db.Column(db.String(15))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    mobile = db.Column(db.String(11))
    qq = db.Column(db.String(12))
    email = db.Column(db.String(30))
    password = db.Column(db.String(100))

    status = db.Column(db.Integer, default=0)

    # 关联微信用户
    openid = db.Column(db.String(32))

    def __init__(self, user_arr):
        self.name = require_value_from_dict(user_arr,"name")
        self.head_url = require_value_from_dict(user_arr,"head_url")
        self.nick = require_value_from_dict(user_arr,"nick")
        self.sex = int(require_value_from_dict(user_arr,"sex"))
        self.interest = require_value_from_dict(user_arr,"interest")
        self.height = int(require_value_from_dict(user_arr,"height"))
        self.weight = int(require_value_from_dict(user_arr,"weight"))
        self.mobile = require_value_from_dict(user_arr,"mobile")
        self.qq = require_value_from_dict(user_arr,"qq")
        self.email = require_value_from_dict(user_arr,"email")
        self.password = require_value_from_dict(user_arr,"password")
        self.openid = require_value_from_dict(user_arr,"openid")

    @login_manager.user_loader
    def load_user(userid):
        return db_session.query(User).filter(User.id == userid)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def hash_password(self):
        return generate_password_hash(self.password)


# **********************************************about QQ begin*********************************************


class Robot(db.Model):
    __tablename__ = 'robots'
    id = db.Column(db.Integer, primary_key=True)
    qq = db.Column(db.String(12), unique=True, index=True)

    status = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Robot id=%r, qq=%r>' % (self.id, self.qq)

    pass


class Cluster(db.Model):
    __tablename__ = 'clusters'
    external_id = db.Column(db.String(12), primary_key=True, index=True)  # cluster number
    robot1_id = db.Column(db.Integer, db.ForeignKey('robots.id'))
    robot2_id = db.Column(db.Integer, db.ForeignKey('robots.id'))
    name = db.Column(db.String(15))
    creator_qq = db.Column(db.String(12), index=True)

    status = db.Column(db.Integer, default=0)

    # description = db.Column(db.String(15))
    # g_crt_time = db.Column(db.INT)
    # g_level = db.Column(db.Integer)
    # g_max_mem = db.Column(db.Integer)
    # g_mem_num = db.Column(db.Integer)
    # group_id = db.Column(db.Integer)
    # last_members_time = db.Column(db.INT)

    def __repr__(self):
        return '<Cluster %r>' % self.name


class ClusterMember(db.Model):
    __tablename__ = 'cluster_members'
    id = db.Column(db.Integer, primary_key=True)
    qq = db.Column(db.String(12), index=True)
    external_id = db.Column(db.String(12), db.ForeignKey('clusters.external_id'), index=True)
    nick = db.Column(db.String(15))
    is_admin = db.Column(db.Boolean, default=False)
    # q_age = db.Column(db.Integer)
    card = db.Column(db.String(15), nullable=True)
    # black = db.Column(db.Boolean)
    # join_time = db.Column(db.INT)
    # last_time = db.Column(db.INT)
    # level = db.Column(db.Integer)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    status = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<ClusterMember %r>' % self.nick

    pass


class QQUser(db.Model):
    __tablename__ = 'qq_users'
    qq = db.Column(db.String(12), primary_key=True)
    nick_name = db.Column(db.String(15))
    # address = db.Column(db.String(30))
    # age = db.Column(db.Integer)
    # area = db.Column(db.String)
    birthday = db.Column(db.Date)
    # email = db.Column(db.String(30))
    # en_name = db.Column(db.String(15))
    # gender = db.Column(db.String(1))
    # group_id = db.Column(db.Integer)
    # gu_xiang = db.Column(db.String(15))
    # header = db.Column(db.String(15))
    # home_page = db.Column(db.String(30))
    # intro = db.Column(db.String(30))
    # ip = db.Column(db.String(30))
    # level = db.Column(db.Integer)
    # mobile = db.Column(db.Integer)
    # name = db.Column(db.String(15))
    # phone = db.Column(db.Integer)
    # qq_age = db.Column(db.Integer)
    # qq_status = db.Column(db.Integer)
    # remark = db.Column(db.String(15))
    # school = db.Column(db.String(15))
    # sheng_xiao = db.Column(db.String(2))
    # signature = db.Column(db.String(15))
    # tag = db.Column(db.Integer)
    # work = db.Column(db.String(15))
    # xing_zuo = db.Column(db.Integer)
    # xue_li = db.Column(db.String)
    # zip_code = db.Column(db.Integer)

    status = db.Column(db.Integer, default=0)
    pass


class QQBindCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qq = db.Column(db.String(12))
    uid = db.Column(db.Integer)
    code = db.Column(db.String(10))
    create_time = db.Column(db.String(13))


# **********************************************about QQ end*********************************************

# **********************************************about dict begin*********************************************

# 活动类别
class ActivityCategory(db.Model):
    __tablename__ = 'activity_category'
    code = db.Column(db.String(32), primary_key=True)  # 编码
    name = db.Column(db.String(32))  # 名称
    status = db.Column(db.Integer)  # 状态 0：可用 -1：不可用
    venue_name = db.Column(db.String(32))  # 地点展示名称
    is_cycle = db.Column(db.Integer)  # 是否周期  0：周期 1：非周期
    days = db.Column(db.Integer)  # 周期长度
    pass


# 活动等级
class ActivityLevel(db.Model):
    __tablename__ = 'activity_level'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32))  # 类别
    name = db.Column(db.String(32))  # 标题
    summary = db.Column(db.String(256))  # 描述
    sort = db.Column(db.Integer)  # 排序
    is_default = db.Column(db.Integer)  # 是否默认
    pass


# 城市列表
class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)  # 根节点
    code = db.Column(db.String(6))  # 邮编
    name = db.Column(db.String(20))  # 名称
    pin_yin = db.Column(db.String(50))  # 拼音
    short_name = db.Column(db.String(10))  # 简称
    sort = db.Column(db.Integer)  # 分类用

    def __repr__(self):
        return '<Area %r>' % self.pin_yin

    pass


# **********************************************about dict begin*********************************************

# **********************************************about weixin begin*********************************************
# 微信菜单
class WeixinMenu(db.Model):
    __tablename__ = 'weixin_menu'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32))  # 类别
    name = db.Column(db.String(16))  # 名称
    type = db.Column(db.String(10))  # 类别
    pid = db.Column(db.String(32))  # 根节点id
    url = db.Column(db.String(256))  # 链接
    update_time = db.Column(db.INT)  # 更新时间
    key_word = db.Column(db.String(32))  # 关键字
    code = db.Column(db.String(10))  # 编码
    state = db.Column(db.String(32))  # 状态


# 微信用户
class WeixinUser(db.Model):
    __tablename__ = 'weixin_user'
    openid = db.Column(db.String(32), primary_key=True)  # 微信用户标示
    nickname = db.Column(db.String(32))  # 昵称
    sex = db.Column(db.Integer)  # 性别  1：男 0：女
    pic = db.Column(db.String(256))  # 头像
    create_time = db.Column(db.String(13))  # 创建时间
    subscribe = db.Column(db.Integer)  # 是否关注  0：未关注 1：关注
    coordinate_lng = db.Column(db.DECIMAL(15, 12))  # 坐标经度
    coordinate_lat = db.Column(db.DECIMAL(15, 12))  # 坐标纬度
    update_time = db.Column(db.String(13))  # 最后更新时间

    def __init__(self, weixinUser_arr):
        self.openid = require_value_from_dict(weixinUser_arr,"openid")
        self.nickname = require_value_from_dict(weixinUser_arr,"nickname")
        self.sex = int(require_value_from_dict(weixinUser_arr,"sex"))
        self.pic = require_value_from_dict(weixinUser_arr,"pic")
        self.subscribe = int(require_value_from_dict(weixinUser_arr,"subscribe"))
        self.coordinate_lng = require_value_from_dict(weixinUser_arr,"coordinate_lng")
        self.coordinate_lat = require_value_from_dict(weixinUser_arr,"coordinate_lat")


# 授权地址
class OauthUrl(db.Model):
    __tablename__ = 'oauth_url'
    id = db.Column(db.String(32), primary_key=True)
    url = db.Column(db.String(255))  # 授权回调地址


class TokenTemp(db.Model):
    __tablename__ = 'w_token_temp'
    token = db.Column(db.String(255))  # token值
    update_time = db.Column(db.String(13))  # 更新时间戳
    name = db.Column(db.String(32), primary_key=True)  # key

    def __init__(self, tokenTemp_arr):
        self.name = require_value_from_dict(tokenTemp_arr,"name")
        self.update_time = require_value_from_dict(tokenTemp_arr,"update_time")
        self.token = require_value_from_dict(tokenTemp_arr,"token")

# **********************************************about wexin begin*********************************************
