# -*- coding:utf-8 -*-
__author__ = 'Van'

from flask import request, Blueprint, current_app, jsonify
from ..utils import require_value_from_dict, model2dict
from ..mredis import RedisClient
from ..mongo import ClubDB, UserDB, ClusterDB
from ..models import Club
from ..helpers.util_helper import get_user, user_role
from ..helpers.permission_helper import AdminPermission, UserPermission
import json
# from datetime import datetime
import time
import random

api = Blueprint('clubs_controller', __name__, url_prefix='')


@api.route('/has_club', methods=['GET', 'POST'])
def n_club_id():

    user_id = int(require_value_from_dict(request.args, "user_id"))
    # clubs = ClubDB.clubs_of_user_from_db(user_id, page_size, page_index)
    club = ClubDB.club_user_create_from_db(user_id)
    if club:
        return json.dumps({"code": 1})
    else:
        return json.dumps({"code": 0})


@UserPermission()
@api.route('/clubs', methods=['POST'])
def clubs_new():
    """
    新建俱乐部提交
    """
    try:
        args = request.args
        user_id = int(args.get("user_id", 0))
        club = Club(args, user_id)
        club.id = int(RedisClient.new_club_id())
        logo_arr = ["/static/app/img/headimgs/club1.png","/static/app/img/headimgs/club1.png","/static/app/img/headimgs/club3.png"]
        index = random.randint(0, 2)
        logo_url = getattr(club,"logo_url",logo_arr[index])
        setattr(club,"logo_url",logo_url)
        # 入库
        ClubDB.add_club(model2dict(club.__dict__))
        # 将俱乐部加入用户表
        role = 0
        UserDB.add_club_to_user_db(club.id, user_id, role, int(time.time()))
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})

    return json.dumps({"code": 1})


@api.route('/find_clubs', methods=['GET'])
@UserPermission()
def find_clubs():
    """显示俱乐部列表
    """
    try:
        page_size = int(request.args.get("page_size", 20))
        page_index = int(request.args.get("page_index", 1))
        clubs = ClubDB.clubs_from_db(page_size, page_index)
        clubs_copy = []
        for club in clubs:
            clubs_copy.append(club)

        r_d = {
            "code": 1,
            "clubs": clubs_copy
        }
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})
    return json.dumps(model2dict(r_d))


@UserPermission()
@api.route('/mine_clubs', methods=['GET'])
def mine_clubs():
    """
    显示我的俱乐部列表
    """
    try:
        user_id = int(require_value_from_dict(request.args, "user_id"))
        # clubs = ClubDB.clubs_of_user_from_db(user_id, page_size, page_index)
        club = ClubDB.club_user_create_from_db(user_id)
        if club:
            club["_id"] = None
        follow_clubs = ClubDB.follow_clubs_of_user_from_db(user_id)

        clubs_copy = []
        for c in follow_clubs:
            if c:
                c["_id"] = None
                clubs_copy.append(c)
        return jsonify({"code": 1, "club": club, "follow_clubs": clubs_copy})
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})


@UserPermission()
@api.route('/clubs/show/<c_id>', methods=['GET'])
def clubs_show(c_id):
    # 要告诉客户端用户的角色，以便决定用户可获取的内容
    try:
        user_id = int(require_value_from_dict(request.args, "user_id"))
        club = ClubDB.club_info_from_db(int(c_id))
        role = user_role(int(c_id), user_id)
        print role
        user = UserDB.user_by_id_from_db(user_id)
        if not user:
            raise Exception("user not found, user_id:=%r" % user_id)
        if "qq" in user:
            qq_bind = True
            clusters_count = ClusterDB.get_admin_clusters_by_qq_from_cluster_db(user["qq"]).count()

        else:
            qq_bind = False
            clusters_count = 1

        r_d = {
            "code": 1,
            "club": club,
            "role": role,
            "qq_bind": qq_bind,
            "clusters_count": clusters_count
        }
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})

    return json.dumps(model2dict(r_d))

@UserPermission()
@api.route('/clubs/<c_id>/members', methods=['GET'])
def members_of_club(c_id):
    try:
        club_id = int(c_id)  # int(request.args.get("club_id"))
        members = ClubDB.members_of_club_from_db(club_id)
        follow_members = ClubDB.follow_members_of_club_from_db(club_id)
        members_copy = []
        managers = []
        for member in members:
            if 0 <= member["role"] <= 1:
                user = get_user(int(member["id"]))
                # user = {"id": member["id"]}
                # user.update({"nickname":member["nickname"],"head_img_url":member["head_img_url"]})
                managers.append(user)
            # else:
            #     members_copy.append(user)
        for follow_member in follow_members:
            if follow_member["role"] == 3:
                # user = get_user(int(follow_member["id"]))
                user = {"id": follow_member.get("id"),
                        "nickname":follow_member.get("nickname"),
                        "head_img_url":follow_member.get("head_img_url")}
                members_copy.append(user)

        r_d = {
            "code": 1,
            "members": members_copy,
            "managers": managers
        }
    except Exception, e:
        current_app.logger.error(e.args)
        return json.dumps({"code": 0})
    return json.dumps(model2dict(r_d))


@UserPermission()
@api.route('/clubs/follow/<c_id>', methods=['POST'])
def clubs_join(c_id):
    club_id = int(c_id)
    user_id = int(require_value_from_dict(request.args, "user_id"))
    user = get_user(user_id)
    follow_time = int(time.time())
    try:
        ClubDB.add_follow_user_to_club_db(club_id, user_id, follow_time,user.get("nickname"),user.get("head_img_url"))
        UserDB.add_follow_club_to_user_db(club_id, user_id)
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})
    return json.dumps({"code": 1})


@UserPermission()
@api.route('/clubs/<c_id>/exit', methods=['POST'])
def clubs_exit(c_id):
    club_id = int(c_id)
    user_id = int(require_value_from_dict(request.args, "user_id"))

    try:
        UserDB.remove_club_from_user_db(club_id, user_id)

        club = ClubDB.club_info_from_db(club_id)
        if club["members_count"] > 1:
            ClubDB.remove_user_from_club_db(club_id, user_id)
        else:
            ClubDB.remove_club_from_db(club_id)

    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})
    return json.dumps({"code": 1})


@UserPermission()
@api.route('/clubs/<c_id>/cancel_follow', methods=['POST'])
def clubs_cancel_follow(c_id):
    club_id = int(c_id)
    user_id = int(require_value_from_dict(request.args, "user_id"))

    try:
        UserDB.remove_follow_club_to_user_db(club_id, user_id)
        ClubDB.remove_follow_user_to_club_db(club_id, user_id)
        return json.dumps({"code": 1})
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})



@AdminPermission()
@api.route('/club_setting/<c_id>', methods=['GET'])
def clubs_setting(c_id):
    # 要告诉客户端用户的角色，以便决定用户可获取的内容
    try:
        user_id = int(require_value_from_dict(request.args, "user_id"))
        club = ClubDB.club_setting_from_db(int(c_id))
        print club
        role = user_role(int(c_id), user_id)
        if role == -1:
            members = ClubDB.apply_join_members_of_club_from_db(int(c_id))
            for member in members:
                if member["id"] == user_id:
                    role = 4
        r_d = {
            "code": 1,
            "club": club,
            "role": role
        }
        return json.dumps(model2dict(r_d))
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})


@AdminPermission()
@api.route('/clubs/update/<c_id>', methods=['POST'])
def club_update(c_id):
    try:
        club_id = int(c_id)
        user_id = int(require_value_from_dict(request.args, "user_id"))
        role = user_role(club_id, user_id)
        if 0 <= role < 3:
            name = request.args.get("name", "俱乐部名")
            tags = request.args.get("tags", "其他")
            logo_url = request.args.get("logo_url", "")
            bg_img_url = request.args.get("bg_img_url", "")
            fields = {"name": name, "tags": tags, "logo_url": logo_url, "bg_img_url": bg_img_url}
            ClubDB.update_club_to_db(club_id, fields)
            return json.dumps({"code": 1})
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})


@AdminPermission()
@api.route('/club_company_update', methods=['POST'])
def club_company_update():
    try:
        club_id = int(require_value_from_dict(request.args, "club_id"))

        company = {
            "id": request.args.get("id", ""),
            "name": request.args.get("name", ""),
            "invoice": request.args.get("invoice", ""),
            "location": request.args.get("location", ""),
            "receiver_name": request.args.get("receiver_name", ""),
            "receiver_mobile": request.args.get("receiver_mobile", "")
        }
        print company
        ClubDB.update_club_company_to_db(club_id, company)
        return json.dumps({"code": 1})
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})