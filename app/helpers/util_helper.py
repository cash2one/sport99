# coding: utf-8
__author__ = 'Van'
from ..mongo import UserDB, ClubDB
from ..mredis import RedisClient
import json


def get_user(u_id):
    user_json = RedisClient.get_user_from_cache(u_id)

    if user_json:
        user_dict = json.JSONDecoder().decode(user_json)
    else:
        user_dict = UserDB.user_info_from_db_by_user_id(int(u_id))

    user = {"id": user_dict["id"]}

    if "name" in user_dict:
        user["name"] = user_dict["name"]
    else:
        if "wechat" in user_dict:
            user["name"] = user_dict["wechat"]["nickname"]

    if "head_img_url" in user_dict:
        user["head_img_url"] = user_dict["head_img_url"]
    else:
        if "wechat" in user_dict:
            user["head_img_url"] = user_dict["wechat"]["headimgurl"]
    if "sex" in user_dict:
        user["sex"] = user_dict["sex"]
    else:
        if "wechat" in user_dict:
            user["sex"] = user_dict["wechat"]["sex"]

    return user


def user_role(club_id, user_id):
    members = ClubDB.members_of_club_from_db(int(club_id))
    role = -1
    for m in members:
        if m["id"] == user_id:
            role = m["role"]
    return role


def is_member(club_id, user_id):
    role = user_role(club_id, user_id)
    if 0 <= role <= 3:
        return True
    else:
        return False


def is_manager(club_id, user_id):
    role = user_role(club_id, user_id)
    if 0 <= role < 3:
        return True
    else:
        return False
