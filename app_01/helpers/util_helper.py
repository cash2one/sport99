# coding: utf-8
__author__ = 'Van'
from ..mongo import UserDB, ClubDB
from ..mredis import RedisClient
import json
import time
import random

# def create_token(user_id):
#     # 生成Token
#     timestamp = int(time.time())
#     nonce = current_app.config.get("WECHAT_NONCE")
#     token = current_app.config.get("WECHAT_TOKEN")
#
#     tmp_list = [token, timestamp, nonce]
#     tmp_list.sort()
#     tmp_str = "%s%s%s" % tuple(tmp_list)
#     hash_sha1 = hashlib.sha1(tmp_str)
#     user_token = hash_sha1.hexdigest()
#     # 缓存token到user_id的映射
#     RedisClient.cache_token(user_token, user_id)
#     return user_token


def get_user(u_id):
    # user_json = RedisClient.get_user_from_cache(u_id)
    images_arr = ['/static/app/img/headimgs/user1.png','/static/app/img/headimgs/user2.png','/static/app/img/headimgs/user3.png','/static/app/img/headimgs/user4.png','/static/app/img/headimgs/user5.png']

    user_json = None
    if user_json:
        return json.JSONDecoder().decode(user_json)
    else:
        user_dict = UserDB.user_info_from_db_by_user_id(int(u_id))
        if not user_dict:
            return {}
        user = {"id": user_dict["id"]}

        nickname = ""
        if "nickname" in user_dict and not nickname:
            nickname = user_dict["nickname"]
        if "wechat" in user_dict and not nickname:
            nickname = user_dict["wechat"]["nickname"]
        user["nickname"] = nickname

        head_img_url = ""
        if "head_img_url" in user_dict and not head_img_url:
            head_img_url = user_dict["head_img_url"]
        if "wechat" in user_dict and not head_img_url:
            head_img_url = user_dict["wechat"].get("headimgurl")
        if not head_img_url:
            index = random.randint(0, 4)
            head_img_url = images_arr[index]
        user["head_img_url"] = head_img_url
        if "sex" in user_dict:
            user["sex"] = user_dict["sex"]
        else:
            if "wechat" in user_dict:
                user["sex"] = user_dict["wechat"]["sex"]

        return user


def user_role(club_id, user_id):
    members = ClubDB.members_of_club_from_db(int(club_id))
    follow_members = ClubDB.follow_members_of_club_from_db(int(club_id))
    role = -1
    for m in members:
        if m["id"] == user_id:
            role = m["role"]
    if role  -1:
        for m in follow_members:
            if m["id"] == user_id:
                role = 5
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
