# -*- coding:utf-8 -*-
__author__ = 'zhaojm'

from flask import Blueprint, current_app, request, jsonify, render_template, url_for, redirect
import json
from ..mongo import EventDB, ClusterDB, UserDB, QQBindCodeDB, AdminUserDB, ClubDB, AdminDB
from threading import Thread
import time, datetime, random
from ..utils import model2dict, require_value_from_dict, get_value_from_dict
from ..mredis import RedisClient
from ..models import Event
from ..helpers.admin_helper import get_admin_token, AdminUserPermission

api = Blueprint('admin_controller', __name__, url_prefix='/admin')


@api.route('/', methods=['GET'])
# @AdminUserPermission()
def index():
    return render_template("admin.html")


@api.route('/login', methods=['POST'])
def login_post():
    username = request.args.get('username')
    password = request.args.get('password')
    try:
        admin_user = AdminUserDB.check_user_access(username, password)
        if admin_user:
            token = get_admin_token(int(admin_user.get("id")))
            RedisClient.cache_admin_token(token, int(admin_user.get("id")))
            admin_info = {
                "token": token,
                "id": admin_user.get("id"),
                "username": admin_user.get("username"),
            }
            return jsonify({"retcode": 0, "result": admin_info})
        else:
            return jsonify({"retcode": 1, "errmsg": "username or password not currect"})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/club/new', methods=['POST'])
@AdminUserPermission()
def club_new():
    for key in request.args:
        print key, request.args[key]
    # new user and new club
    mobile = require_value_from_dict(request.args, "mobile")
    nickname = require_value_from_dict(request.args, "nickname")
    club_name = require_value_from_dict(request.args, "club_name")
    tags = require_value_from_dict(request.args, "tags")
    admin_id = int(require_value_from_dict(request.args, "admin_id"))

    try:
        user_id = RedisClient.new_user_id()
        club_id = RedisClient.new_club_id()

        create_user(user_id, club_id, mobile, nickname)
        create_club(user_id, club_id, club_name, tags)
        AdminUserDB.add_user_id(admin_id, user_id)
        return jsonify({"retcode": 0, "result": "success"})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/club/list', methods=['GET'])
@AdminUserPermission()
def club_list():
    admin_id = int(require_value_from_dict(request.args, "admin_id"))
    try:
        club_list_from_db = AdminDB.get_club_list(admin_id)
        club_list_json = []
        if club_list_from_db:
            for club in club_list_from_db:
                print "club", club
                club_list_json.append(model2dict(club))
        return jsonify({"retcode": 0, "result": club_list_json})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/club/detail/<id>', methods=['GET'])
@AdminUserPermission()
def club_detail(id):
    id = int(id)
    try:
        club = AdminDB.get_club_detail(id)
        if not club:
            raise Exception("club not found, id:=" + id)
        user_id = club.get("creator_id")
        user = AdminDB.get_user_detail(user_id)
        if not user:
            raise Exception("user not found, id:=" + user_id)
        ret = {
            "club_id": club.get("id"),
            "club_name": club.get("name"),
            "tags": club.get("tags"),
            "user_id": user_id,
            "nickname": user.get("nickname"),
            "mobile": user.get("mobile"),
        }
        return jsonify({"retcode": 0, "result": ret})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/club/modify', methods=['PUT'])
@AdminUserPermission()
def club_modify():
    # new user and new club
    club_id = int(require_value_from_dict(request.args, "club_id"))
    user_id = int(require_value_from_dict(request.args, "user_id"))
    mobile = require_value_from_dict(request.args, "mobile")
    nickname = require_value_from_dict(request.args, "nickname")
    club_name = require_value_from_dict(request.args, "club_name")
    tags = require_value_from_dict(request.args, "tags")
    try:
        ClubDB.update_club_to_db(club_id, {"name": club_name, "tags": tags})
        UserDB.update_user_to_db(user_id, {"nickname": nickname, "mobile": mobile})
        return jsonify({"retcode": 0, "result": "success"})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/club/delete/<id>', methods=["DELETE"])
@AdminUserPermission()
def club_delete(id):
    pass


@api.route('/event/new', methods=['POST'])
@AdminUserPermission()
def event_new():
    for key in request.args:
        print key, request.args[key]
    try:
        user_id = int(require_value_from_dict(request.args, "creator_id"))
        club_id = int(require_value_from_dict(request.args, "club_id"))
        event_id = RedisClient.new_event_id()
        create_event(club_id, user_id, event_id, request.args)
        return jsonify({"retcode": 0, "result": "success"})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/event/modify', methods=['PUT'])
@AdminUserPermission()
def event_modify():
    for key in request.args:
        print key, request.args[key]

    try:
        user_id = int(require_value_from_dict(request.args, "creator_id"))
        event_id = int(require_value_from_dict(request.args, "id"))
        print user_id, event_id
        event = Event(request.args, user_id, True)
        EventDB.update_event_to_db(event_id, event.__dict__)
        return jsonify({"retcode": 0, "result": "success"})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/event/list', methods=['GET'])
@AdminUserPermission()
def event_list():
    admin_id = int(require_value_from_dict(request.args, "admin_id"))
    try:
        event_list_from_db = AdminDB.get_event_list(admin_id)
        event_list_json = []
        if event_list_from_db:
            for event in event_list_from_db:
                event_list_json.append(model2dict(event))
        return jsonify({"retcode": 0, "result": event_list_json})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/event/list_of_club/<club_id>', methods=['GET'])
@AdminUserPermission()
def events_of_club(club_id):
    try:
        club_id = int(club_id)
        admin_id = int(require_value_from_dict(request.args, "admin_id"))
        event_list_from_db = AdminDB.get_event_list_by_club_id(club_id)
        event_list_json = []
        if event_list_from_db:
            # print " for begin"
            # print event_list_from_db
            for event in event_list_from_db:
                # print event.get("id")
                event_list_json.append(model2dict(event))
        # print event_list_from_db[0]
        # print event_list_json
        return jsonify({"retcode": 0, "result": event_list_json})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/event/detail/<id>', methods=['GET'])
@AdminUserPermission()
def event_detail(id):

    try:
        id = int(id)
        event = EventDB.event_by_id_from_db(id)
        return jsonify({"retcode": 0, "result": model2dict(event)})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


@api.route('/event/delete/<id>', methods=["DELETE"])
@AdminUserPermission()
def event_delete(id):
    try:
        id = int(id)
        delete_event(id)
        return jsonify({"retcode": 0, "result": "success"})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"retcode": -1, "errmsg": e.message})


def create_user(user_id, club_id, mobile, nickname):
    images_arr = [
        '/static/app/img/headimgs/user1.png',
        '/static/app/img/headimgs/user2.png',
        '/static/app/img/headimgs/user3.png',
        '/static/app/img/headimgs/user4.png',
        '/static/app/img/headimgs/user5.png'
    ]

    openid = "xuniyonghu_" + str(user_id)

    head_img_url = images_arr[random.randint(0, 4)]

    user = {
        "events": [],
        "events_count": 0,
        "follow_clubs": [],
        "follow_clubs_count": 0,
        "head_img_url": head_img_url,
        "height": "123",
        "id": user_id,
        "interest": "123",
        "clubs": [{
            "role": 0,
            "id": club_id,
            "join_time": int(time.time())
        }],
        "clubs_count": 1,
        "mobile": mobile,
        "nickname": nickname,
        "sex": "男",
        "status": 0,
        "user_id": str(user_id),
        "wechat": {
            "province": "北京",
            "openid": openid,
            "headimgurl": head_img_url,
            "language": "en",
            "city": "海淀",
            "country": "中国",
            "sex": 1,
            "privilege": [],
            "nickname": nickname
        }
    }

    UserDB.add_user_to_db(user)


def create_club(user_id, club_id, club_name, tags):
    logo_arr = ["/static/app/img/headimgs/club1.png",
                "/static/app/img/headimgs/club1.png",
                "/static/app/img/headimgs/club3.png"
                ]
    logo_url = logo_arr[random.randint(0, 2)]

    club = {
        "bg_img_url": "/static/app/img/bgimgs/club/P5.png",
        "bind_qq": "",
        "create_time": int(time.time()),
        "creator_id": user_id,
        "events_count": 0,
        "follow_members": [],
        "follow_members_count": 0,
        "id": club_id,
        "logo_url": logo_url,
        "members": [{
            "role": 0,
            "id": user_id,
            "join_time": int(time.time())
        }],
        "members_count": 1,
        "name": club_name,
        "status": 0,
        "tags": tags
    }

    ClubDB.add_club(club)


def create_event(club_id, user_id, event_id, params):
    is_cycle = require_value_from_dict(params, "is_cycle")
    is_aa = require_value_from_dict(params, "is_aa")
    event = {
        "category": require_value_from_dict(params, "category"),
        "club_id": club_id,
        "clusters": [],
        "create_time": int(time.time()),
        "creator_id": user_id,
        "end_time": int(require_value_from_dict(params, "end_time")),
        "fee": int(require_value_from_dict(params, "fee")),
        "id": event_id,
        "is_aa": is_aa,
        "is_cycle": is_cycle,
        "members": [],
        "members_count": 0,
        "introduce": require_value_from_dict(params, "introduce"),
        "members_count_limit": int(require_value_from_dict(params, 'members_count_limit')),
        "mobile": require_value_from_dict(params, "mobile"),
        "name": require_value_from_dict(params, "name"),
        "place_num": require_value_from_dict(params, "place_num"),
        "signs": {},
        "start_time": int(require_value_from_dict(params, "start_time")),
        "status": 0,
        "type": "template" if is_cycle == "true" else "event",
        "venue": {
            "coordinate": [0, 0],
            "phone": "",
            "title": require_value_from_dict(params, "venue_title"),
            "city": "北京市",
            "address": require_value_from_dict(params, "venue_address")
        },
        "weekday": 1,  # ???

    }
    # print is_cycle
    if is_cycle == "true":
        event.update({
            "days": require_value_from_dict(params, "days")
        })
    if is_aa == "true":
        event.update({
            "fee": 0
        })

    EventDB.add_event_to_db(event)
    # UserDB.add_event_to_user_db(event_id, user_id)


def delete_event(event_id):
    EventDB.remove_event_from_db({"id": event_id})
    pass
