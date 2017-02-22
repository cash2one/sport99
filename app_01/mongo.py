# -*- coding:utf-8 -*-
__author__ = 'Van'

import os
import pymongo
import datetime
import time
import threading

lock = threading.Lock()
# from bson import ObjectId

MONGODB_HOST = os.getenv("MONGODB_HOST", '127.0.0.1')
MONGODB_PORT = os.getenv("MONGODB_PORT", 27017)
mongodb_client_db = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT).sport99


class UserDB():
    def __init__(self):
        pass

    @staticmethod
    def user_by_open_id(open_id):
        """
        登录
        """
        return mongodb_client_db.users.find_one({"wechat.openid": open_id})

    @staticmethod
    def add_user_to_db(user):
        """
        新建用户
        """
        return mongodb_client_db.users.insert(user)

    @staticmethod
    def update_user_to_db(user_id, data):
        """
        修改用户
        """
        mongodb_client_db.users.update(
            {"id": user_id},
            {"$set": data}
        )

    @staticmethod
    def upsert_user_wx_to_db(user_id, wx):
        """
        跟新用户微信
        """
        return mongodb_client_db.users.update(
            {"id": user_id},
            {
                "$set": {
                    "status": 0,
                    "wechat": wx
                }
            },
            True
        )

    @staticmethod
    def insert_user_by_qq_to_db(user_id, qq, nick):
        """
        跟新用户QQ
        """
        return mongodb_client_db.users.insert({"id": user_id, "qq": qq, "nickname": nick, "status": 0})

    @staticmethod
    def upsert_user_qq_by_id_to_db(user_id, qq):
        """
        跟新用户QQ
        """
        return mongodb_client_db.users.update(
            {"id": user_id},
            {
                "$set": {"qq": qq, "status": 0}
            },
            True
        )

    @staticmethod
    def user_by_id_from_db(user_id):
        """
        登录
        """
        return mongodb_client_db.users.find_one({"id": user_id})

    @staticmethod
    def login_from_db(mobile, psw):
        """
        登录
        """
        return mongodb_client_db.users.find_one({"mobile": mobile, "password": psw})

    @staticmethod
    def all_users_from_db():
        """
        所有用户 ＃MARK 暂时没有用
        """
        return mongodb_client_db.users.find()

    @staticmethod
    def user_info_from_db_by_user_id(user_id):
        """
        用户信息：姓名, 头像, 性别, 微信
        """
        return mongodb_client_db.users.find_one(
            {"id": user_id}, {"id": 1, "nickname": 1, "head_img_url": 1, "sex": 1, "wechat": 1})

    @staticmethod
    def mine_info_from_db_by_user_id(user_id):
        """
        用户信息：姓名, 头像, 性别, 微信
        """
        return mongodb_client_db.users.find_one(
            {"id": user_id},
            {
                "nickname": 1,
                "head_img_url": 1,
                "sex": 1,
                "mobile": 1,
                "birthday": 1,
                "interest": 1,
                "city": 1,
                "wechat": 1,
                "weight": 1,
                "height": 1,
                "qq": 1,
                "email": 1
            }
        )

    @staticmethod
    def add_club_to_user_db(club_id, user_id, role, join_time):
        """
        用户加入俱乐部
        """
        mongodb_client_db.users.update(
            {"id": user_id},
            {
                "$addToSet": {"clubs": {"id": club_id, "role": role, "join_time": join_time}},
                "$inc": {"clubs_count": 1}
            }
        )

    @staticmethod
    def remove_club_from_user_db(club_id, user_id):
        """
        用户加入俱乐部
        """
        mongodb_client_db.users.update(
            {"id": user_id},
            {
                "$pull": {"clubs": {"id": club_id}},
                "$inc": {"clubs_count": -1}
            }
        )

    @staticmethod
    def clubs_of_user_from_db(user_id):
        """
        用户俱乐部列表
        """
        user = mongodb_client_db.users.find_one({"id": user_id}, {"clubs": 1})

        if user and "clubs" in user:
            return user["clubs"]
        else:
            return []

    @staticmethod
    def follow_clubs_of_user_from_db(user_id):
        """
        用户俱乐部列表
        """
        user = mongodb_client_db.users.find_one({"id": user_id}, {"follow_clubs": 1})

        if user and "follow_clubs" in user:
            return user["follow_clubs"]
        else:
            return []

    @staticmethod
    def add_event_to_user_db(event_id, user_id):
        """
        用户报名活动
        """
        mongodb_client_db.users.update(
            {"id": user_id},
            {
                "$addToSet": {"events": event_id},
                "$inc": {"events_count": 1}
            }
        )

    @staticmethod
    def remove_event_from_user_db(event_id, user_id):
        """
        用户取消报名活动
        """
        mongodb_client_db.users.update(
            {"id": user_id},
            {
                "$pull": {"events": event_id},
                "$inc": {"events_count": -1}
            }
        )

    @staticmethod
    def user_events_from_db(user_id):
        """
        用户的所有活动
        """
        user = mongodb_client_db.users.find_one({"id": user_id}, {"events": 1})
        if user and "events" in user:
            return user["events"]
        else:
            return []

    @staticmethod
    def add_follow_club_to_user_db(club_id, user_id):
        """
        用户加入俱乐部
        """
        mongodb_client_db.users.update(
            {"id": user_id},
            {
                "$addToSet": {"follow_clubs": {"id": club_id}},
                "$inc": {"follow_clubs_count": 1}
            }
        )

    @staticmethod
    def remove_follow_club_to_user_db(club_id, user_id):
        """
        用户加入俱乐部
        """
        mongodb_client_db.users.update(
            {"id": user_id},
            {
                "$pull": {"follow_clubs": {"id": club_id}},
                "$inc": {"follow_clubs_count": -1}
            }
        )

    # @staticmethod
    # def remove_event_by_qq_from_user_db(qq, event_id):
    #     return mongodb_client_db.users.update(
    #         {"qq": qq, "status": 0},
    #         {
    #             "$pull": {"events": event_id},
    #         }
    #     )

    @staticmethod
    def add_event_by_qq_to_user_db(qq, event_id):
        """
        用户报名活动
        """
        mongodb_client_db.users.update(
            {"qq": qq, "status": 0},
            {
                "$addToSet": {"events": event_id},
            }
        )

    @staticmethod
    def user_by_qq_from_user_db(qq):
        return mongodb_client_db.users.find_one({"qq": qq, "status": 0})

    @staticmethod
    def user_by_openid_from_user_db(openid):
        return mongodb_client_db.users.find_one({"wechat.openid": openid, "status": 0})

    @staticmethod
    def events_by_qq_from_user_db(qq):
        user = mongodb_client_db.users.find_one({"qq": qq, "status": 0})

        if user and user.get("events"):
            return user["events"]
        else:
            return None

    @staticmethod
    def remove_user_by_qq_from_user_db(qq):
        #
        mongodb_client_db.users.update({"qq": qq, "status": 0}, {"$set": {"status": -1}})

    @staticmethod
    def remove_user_by_user_id(user_id):
        mongodb_client_db.users.update({"id": user_id, "status": 0}, {"$set": {"status": -1}})

    @staticmethod
    def revert_old_qq_user_from_user_db(qq):
        #
        mongodb_client_db.users.update({"qq": qq, "status": -1}, {"$set": {"status": 0}})

    @staticmethod
    def user_id_max_from_db():
        res = mongodb_client_db.users.find({"id": {"$gt": 0}}, {"id": 1, "_id": 0}).sort("id", -1).limit(1)
        return int(res[0]["id"])


class ClubDB():
    def __init__(self):
        pass

    @staticmethod
    def club_info_from_db(club_id):
        """
        俱乐部基本信息
        """
        return mongodb_client_db.clubs.find_one(
            {"id": club_id},
            {
                "id": 1, "name": 1, "city": 1, "category": 1, "logo_url": 1, "tags": 1, "description": 1,
                "members_count": 1, "events_count": 1, "follow_members_count": 1, "setting.join_need_approve": 1,
                "apply_join_members_count": 1, "bg_img_url": 1
            }
        )

    @staticmethod
    def club_setting_from_db(club_id):
        """
        俱乐部基本信息
        """
        return mongodb_client_db.clubs.find_one(
            {"id": club_id},
            {
                "id": 1, "name": 1, "city": 1, "category": 1, "logo_url": 1, "type": 1, "description": 1,
                "setting.join_need_approve": 1, "apply_join_members_count": 1, "company": 1
            }
        )

    @staticmethod
    def clubs_of_user_from_db(user_id, page_size, page_index):
        """
        分页取所有俱乐部列表，#MARK 初期没有推荐搜索时使用
        """
        skip = page_size * (page_index - 1)
        clubs = UserDB.clubs_of_user_from_db(user_id)
        club_ids = []
        for club in clubs:
            club_ids.append(club["id"])
        print club_ids
        clubs = mongodb_client_db.clubs.find({"id": {"$in": club_ids}, "status": 0}).skip(skip).limit(page_size)
        return clubs

    @staticmethod
    def club_user_create_from_db(user_id):
        """
        分页取所有俱乐部列表，#MARK 初期没有推荐搜索时使用
        """
        club = mongodb_client_db.clubs.find_one({"creator_id": user_id})
        return club

    @staticmethod
    def follow_clubs_of_user_from_db(user_id):
        """
        分页取所有俱乐部列表，#MARK 初期没有推荐搜索时使用
        """
        clubs = UserDB.follow_clubs_of_user_from_db(user_id)
        club_ids = []
        for club in clubs:
            club_ids.append(club["id"])

        clubs = mongodb_client_db.clubs.find({"id": {"$in": club_ids}},
                                             {"id": 1, "tags": 1, "logo_url": 1, "name": 1, "creator_id": 1,
                                              "bg_img_url": 1})
        return clubs

    @staticmethod
    def add_club(club):
        """
        新建俱乐部
        """
        return mongodb_client_db.clubs.insert(club)

    @staticmethod
    def update_club_to_db(club_id, fields):
        """
        修改俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$set": fields
            }
        )

    @staticmethod
    def update_club_company_to_db(club_id, company):
        """
        修改俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$set": {"company": company}
            }
        )

    @staticmethod
    def update_join_need_approve_to_db(club_id, v):
        """
        修改俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$set": {"setting.join_need_approve": v}
            }
        )

    @staticmethod
    def members_of_club_from_db(club_id):
        """
        俱乐部成员列表
        """
        club = mongodb_client_db.clubs.find_one({"id": club_id}, {"members": 1})

        if club and "members" in club:
            members = club["members"]
        else:
            members = []
        return members

    @staticmethod
    def follow_members_of_club_from_db(club_id):
        """
        俱乐部关注成员列表
        """
        club = mongodb_client_db.clubs.find_one({"id": club_id}, {"follow_members": 1})

        if club and "follow_members" in club:
            members = club["follow_members"]
        else:
            members = []
        return members

    @staticmethod
    def apply_join_members_of_club_from_db(club_id):
        """
        俱乐部成员列表
        """
        club = mongodb_client_db.clubs.find_one({"id": club_id}, {"apply_join_members": 1})

        if club and "apply_join_members" in club:
            members = club["apply_join_members"]
        else:
            members = []
        return members

    @staticmethod
    def add_apply_user_to_club_db(club_id, user_id, join_time):
        """
        加入俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$push": {"apply_join_members": {"id": user_id, "join_time": join_time}},
                "$inc": {"apply_join_members_count": 1}
            }
        )

    @staticmethod
    def approve_join_user_to_club_db(club_id, user_id, join_time):

        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$pull": {"apply_join_members": {"id": user_id}},
                "$push": {"members": {"id": user_id, "join_time": join_time, "role": 3}},
                "$inc": {"members_count": 1, "apply_join_members_count": -1}
            }
        )

    @staticmethod
    def add_user_to_club_db(club_id, user_id, join_time):
        """
        加入俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$push": {"members": {"id": user_id, "join_time": join_time, "role": 3}},
                "$inc": {"members_count": 1}
            }
        )

    @staticmethod
    def remove_user_from_club_db(club_id, user_id):
        """
        退出俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$pull": {"members": {"id": user_id}},
                "$inc": {"members_count": -1}
            }
        )

    @staticmethod
    def remove_club_from_db(club_id):
        """
        退出俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$set": {"status": -1},
            }
        )

    @staticmethod
    def add_follow_user_to_club_db(club_id, user_id, join_time, nickname, head_img_url):
        """
        加入俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$push": {"follow_members": {"id": user_id, "join_time": join_time, "role": 3, "nickname": nickname,
                                             "head_img_url": head_img_url}},
                "$inc": {"follow_members_count": 1}
            }
        )

    @staticmethod
    def remove_follow_user_to_club_db(club_id, user_id):
        """
        加入俱乐部
        """
        mongodb_client_db.clubs.update(
            {"id": club_id},
            {
                "$pull": {"follow_members": {"id": user_id}},
                "$inc": {"follow_members_count": -1}
            }
        )

    @staticmethod
    def club_all_from_db():
        mongodb_client_db.clubs.find({
            "id": {"$gt": 0},
            "creator_id": {"$gt": 0}
        })

    @staticmethod
    def club_id_max_from_db():
        res = mongodb_client_db.clubs.find({"id": {"$gt": 0}}, {"id": 1, "_id": 0}).sort("id", -1).limit(1)
        return int(res[0]["id"])


class EventDB():
    """
    db.events.ensureIndex("venue":{"coordinate":"2d"})
    """

    def __init__(self):
        pass

    @staticmethod
    def events_of_club_from_db(club_id, page_size, page_index):
        """
        俱乐部活动
        """
        return mongodb_client_db.events.find(
            {"club_id": club_id, "status": 0, "type": "event"}).sort("start_time", -1).skip(
            page_size * (page_index - 1)).limit(page_size)

    @staticmethod
    def event_by_id_from_db(event_id):
        """
        活动内容
        """
        return mongodb_client_db.events.find_one({"id": event_id})

    @staticmethod
    def events_of_user_from_db(user_id, page):
        """
        用户 报名 的 所有活动
        """

        if page == "published":
            return mongodb_client_db.events.find({"creator_id": user_id, "status": {"$gte": 0}, "type": "event"}).sort(
                "start_time", -1)
        elif page == "joined":
            event_ids = UserDB.user_events_from_db(user_id)
            return mongodb_client_db.events.find(
                {"id": {"$in": event_ids}, "status": {"$gte": 0}, "type": "event"}).sort("start_time", -1)
        else:
            events_published = mongodb_client_db.events.find({"creator_id": user_id, "type": "event"}).sort(
                "start_time", -1)
            event_ids = UserDB.user_events_from_db(user_id)
            event_joined = mongodb_client_db.events.find({"id": {"$in": event_ids}, "type": "event"}).sort("start_time",
                                                                                                           -1)
            return event_joined.extends(events_published)

    @staticmethod
    def events_filter_from_db(m_filter, page_size, page_index):
        """
        筛选
        """
        skip = page_size * (page_index - 1)
        m_filter.update({"type": {"$in": ["event", "null"]}})

        return mongodb_client_db.events.find(m_filter).sort("start_time", 1).skip(skip).limit(page_size)

    @staticmethod
    def events_week_max_sign_from_db(user_id, start_time, qq):
        """
        计算本周的活动标示
        """
        events = mongodb_client_db.events.find(
            {
                # "creator_id": user_id,
                "start_time": {
                    "$gt": start_time - 3600 * 24 * 7,
                    "$lt": start_time + 3600 * 24 * 7
                },
                "clusters": qq,
                # "status": 0,
                "type": "event",
            }
        )
        if events.count() == 0:
            return chr(65), 0
        else:
            chars = []
            for e in events:
                if "signs" in e and qq in e["signs"]:
                    chars.append(e["signs"][qq])
            chars.sort()
            if chars.__len__() > 0:
                char = chars[0]
                return char, chars.__len__()
            else:
                return 'A', 0

    @staticmethod
    def remove_event_from_db(rule):
        mongodb_client_db.events.remove(rule)

    @staticmethod
    def add_event_to_db(event):
        mongodb_client_db.events.insert(event)

    @staticmethod
    def update_event_to_db(event_id, fields):
        """
        修改活动设置
        """
        mongodb_client_db.events.update(
            {"id": event_id},
            {
                "$set": fields
            }
        )

    @staticmethod
    def update_event_cancel_to_db(event_id):
        """
        设置活动为已取消
        """
        mongodb_client_db.events.update(
            {"id": event_id},
            {
                "$set": {
                    "status": -1
                }
            }
        )

    @staticmethod
    def add_member_to_event_db(event_id, user_id, join_count, join_time):

        channel = "微信"  # "web"
        EventDB.add_member_base_to_event_db(event_id, user_id, None, None, join_count, join_time, channel)
        # mongodb_client_db.events.update(
        #     {"id": event_id},
        #     {
        #         "$addToSet": {"members": {"id": user_id, "join_count": join_count, "join_time": join_time}},
        #         "$inc": {"members_count": join_count}
        #     }
        # )

    @staticmethod
    def remove_member_from_event_db(event_id, user_id, exit_count):
        mongodb_client_db.events.update(
            {"id": event_id},
            {
                "$pull": {"members": {"id": user_id}},
                "$inc": {"members_count": 0 - exit_count}
            }
        )

    @staticmethod
    def set_member_count(event_id, mems, count):
        mongodb_client_db.events.update(
            {"id": event_id},
            {
                "$set": {
                    "members": mems,
                    "members_count": count
                }
            }
        )

    @staticmethod
    def add_member_by_nick_to_event_db(event_id, user_temp, help_qq, join_count, join_time):
        channel = "增"
        EventDB.add_member_base_to_event_db(event_id, None, user_temp, help_qq, join_count, join_time, channel)

        # mongodb_client_db.events.update(
        #     {"id": event_id},
        #     {
        #         "$addToSet": {
        #             "members": {
        #                 "user_temp": user_temp,
        #                 "channel": "增",
        #                 "help_qq": help_qq,
        #                 "join_count": join_count,
        #                 "join_time": join_time
        #             }
        #         },
        #         "$inc": {"members_count": join_count}
        #     }
        # )

    @staticmethod
    def add_member_by_friend_qq_to_event_db(event_id, user_id, help_qq, join_count, join_time):
        channel = "qq"
        EventDB.add_member_base_to_event_db(event_id, user_id, None, help_qq, join_count, join_time, channel)

        # mongodb_client_db.events.update(
        #     {"id": event_id},
        #     {
        #         "$addToSet": {"members":
        #             {
        #                 "id": user_id,
        #                 "channel": "qq",
        #                 "help_qq": help_qq,
        #                 "join_count": join_count,
        #                 "join_time": join_time
        #             }
        #         },
        #         "$inc": {"members_count": join_count}
        #     }
        # )

    @staticmethod
    def add_member_by_qq_self_to_event_db(event_id, user_id, join_count, join_time):

        channel = "qq"
        EventDB.add_member_base_to_event_db(event_id, user_id, None, None, join_count, join_time, channel)

        # return mongodb_client_db.events.update(
        #     {"id": event_id},
        #     {
        #         "$addToSet": {
        #             "members": {"id": user_id, "channel": "qq", "join_count": join_count, "join_time": join_time}},
        #         "$inc": {"members_count": join_count}
        #     }
        # )

    @staticmethod
    def add_member_base_to_event_db(event_id, user_id, user_temp, help_qq, join_count, join_time, channel):

        lock.acquire()

        try:
            # 判断人数
            event = EventDB.event_by_id_from_db(event_id)
            if not event.get("members_count"):
                member_count = 0
            else:
                member_count = event.get("members_count")
            if (member_count + join_count) <= event.get("members_count_limit"):
                if user_temp:
                    mongodb_client_db.events.update(
                        {"id": event_id},
                        {
                            "$addToSet": {
                                "members": {
                                    "user_temp": user_temp,
                                    "channel": channel,
                                    "help_qq": help_qq,
                                    "join_count": join_count,
                                    "join_time": join_time
                                }
                            },
                            "$inc": {"members_count": join_count}
                        }
                    )
                elif user_id and help_qq:
                    mongodb_client_db.events.update(
                        {"id": event_id},
                        {
                            "$addToSet": {"members":
                                {
                                    "id": user_id,
                                    "channel": channel,
                                    "help_qq": help_qq,
                                    "join_count": join_count,
                                    "join_time": join_time
                                }
                            },
                            "$inc": {"members_count": join_count}
                        }
                    )
                elif user_id and (not help_qq):
                    mongodb_client_db.events.update(
                        {"id": event_id},
                        {
                            "$addToSet": {"members":
                                              {"id": user_id,
                                               "channel": channel,
                                               "join_count": join_count,
                                               "join_time": join_time
                                               }
                                          },
                            "$inc": {"members_count": join_count}
                        }
                    )
                else:
                    raise Exception("error params when join event");
        except Exception, e:
            print e.message
        finally:
            lock.release()

    @staticmethod
    def get_member_by_nick_from_event_db(event_id, user_temp):
        event = mongodb_client_db.events.find_one({"id": event_id})
        if event and event.get("members"):
            members = event["members"]
            for member in members:
                if member.get("user_temp") == user_temp:
                    return member
        return None

    @staticmethod
    def get_member_by_qq_from_event_db(event_id, qq):
        event = mongodb_client_db.events.find_one({"id": event_id})
        if event and event.get("members"):
            members = event["members"]
            for member in members:
                if member.get("qq") == qq:
                    return member
        return None

    @staticmethod
    def get_member_by_id_from_event_db(event_id, user_id):
        event = mongodb_client_db.events.find_one({"id": event_id})
        if event and event.get("members"):
            members = event["members"]
            for member in members:
                if member.get("id") == user_id:
                    return member
        return None

    @staticmethod
    def remove_member_by_nick_from_event_db(event_id, user_temp, exit_count):
        mongodb_client_db.events.update(
            {"id": event_id},
            {
                "$pull": {
                    "members": {"user_temp": user_temp}
                },
                "$inc": {"members_count": (0 - exit_count)}
            }
        )

    @staticmethod
    def remove_members_by_nick_from_event_db(cluster_id, user_temp):
        events = EventDB.events_of_cluster_from_db(cluster_id, None, None)
        events_remove = []
        for event in events:
            member = EventDB.get_member_by_nick_from_event_db(event.get("id"), user_temp)
            if member:
                events_remove.append(event)
                EventDB.remove_member_by_nick_from_event_db(event.get("id"), user_temp, member.get("join_count"))
        return events_remove

    @staticmethod
    def events_by_qq_from_event_db(cluster_id, qq):
        """
        qq报名的所有活动
        """
        now = time.time()
        event_ids = UserDB.events_by_qq_from_user_db(qq)
        events = mongodb_client_db.events.find({
            "id": {"$in": event_ids},
            "clusters": {"$all": [cluster_id]},
            "status": 0,
            "type": "event",
            "end_time": {"$gte": now, "$lte": now + 60 * 60 * 24 * 7},
        }).sort("start_time", 1)
        return events

    @staticmethod
    def events_of_cluster_from_db(cluster_id, page_size, page_index):
        """
        群活动列表
        """
        now = time.time()
        return mongodb_client_db.events.find(
            {
                "type": "event",
                "clusters": {"$all": [cluster_id]},
                "end_time": {"$gte": now, "$lte": now + 60 * 60 * 24 * 7},
                "status": 0,
                "start_time": {"$gt": now - 3600 * 24}
            },
            {"_id": 0}
        ).sort("start_time", 1)

    @staticmethod
    def events_from_db_by_event_ids(event_ids):

        return mongodb_client_db.events.find({
            "id": {"$in": event_ids},
        }).sort("start_time", 1)

    @staticmethod
    def event_of_cluster_by_sign_from_db(cluster_id, sign, page_size, page_index):
        """
        群活动详情
        """
        now = time.time()
        if sign:
            return mongodb_client_db.events.find_one({
                "clusters": {"$all": [cluster_id]},
                "end_time": {"$gte": now, "$lte": now + 60 * 60 * 24 * 7},
                "signs." + cluster_id: sign,
                "type": "event",
                "status": 0,
            })
        else:
            # 最近的活动
            events = mongodb_client_db.events.find({
                "clusters": {"$all": [cluster_id]},
                "end_time": {"$gte": now, "$lte": now + 60 * 60 * 24 * 7},
                "type": "event",
                "status": 0,
                "start_time": {"$gt": now - 3600 * 24}
            }).sort("start_time", 1).limit(1)
            # current_app.logger.info(events)
            if events.count() == 0:
                return None
            return events[0]

    @staticmethod
    def cities_from_db():
        cities = mongodb_client_db.cities.find({}, {"_id": 0}).sort("letter")
        return cities

    @staticmethod
    def sign_from_event_db(cluster, start_time):
        sign_arr = mongodb_client_db.events.find(
            {
                "status": 0,
                "type": "event",
                "end_time": {
                    "$gte": start_time - 3600 * 24 * 7,
                    "$lte": start_time + 3600 * 24 * 7
                },
                "signs." + cluster: {
                    "$exists": True
                }
            },
            {"_id": 0, "signs." + cluster: 1}
        )
        sign_list = []
        if sign_arr:
            for sign in sign_arr:
                sign_list.append(sign["signs"].get(cluster))
        return sign_list

    @staticmethod
    def event_template_from_db(weekday):
        return mongodb_client_db.events.find({"days": {"$in": [weekday]}, "status": 0, "type": "template"})

    @staticmethod
    def get_cluster_events_count(cluster_id):
        now = time.time()
        return mongodb_client_db.events.find({
            "clusters": {"$in": [cluster_id]},
            "end_time": {"$gte": now, "$lte": now + 60 * 60 * 24 * 7},
            "status": 0,
            "type": "event",
        }).count()

    @staticmethod
    def event_id_max_from_db():
        res = mongodb_client_db.events.find({"id": {"$gt": 0}}, {"id": 1, "_id": 0}).sort("id", -1).limit(1)
        return int(res[0]["id"])

    @staticmethod
    def event_by_template_from_db(id):
        return mongodb_client_db.events.find({"template_id": id}).count()

class VenueDB():
    def __init__(self):
        pass

    @staticmethod
    def add_venue_to_db(venue):
        return mongodb_client_db.venues.insert(venue)

    @staticmethod
    def venues_from_db(page_size, page_index):
        skip = page_size * (page_index - 1)
        return mongodb_client_db.venues.find().skip(skip).limit(page_size)


class ClusterDB():
    def __init__(self):
        pass

    @staticmethod
    def remove_cluster_from_db(cluster_id):
        return mongodb_client_db.clusters.update(
            {"external_id": cluster_id},
            {
                "$set": {"status": -1}
            }
        )

    @staticmethod
    def find_cluster_member_from_db(qq, cluster_id):
        cluster = mongodb_client_db.clusters.find_one({"external_id": cluster_id}, {"members": 1})
        if cluster and cluster.get("members"):
            members = cluster["members"]
            for member in members:
                if member and member.get("qq") and member["qq"] == qq:
                    return member
        return None

    @staticmethod
    def find_cluster_members_from_db(cluster_id):
        cluster = mongodb_client_db.clusters.find_one({"external_id": cluster_id}, {"members": 1})
        if cluster and cluster.get("members"):
            members = cluster["members"]
            return members
        return None

    @staticmethod
    def add_cluster_member_to_db(cluster_id, qq, nick, is_admin, card):
        return mongodb_client_db.clusters.update(
            {"external_id": cluster_id},
            {
                "$addToSet": {"members": {"qq": qq, "nick": nick, "is_admin": is_admin, "card": card}},
            }
        )

    @staticmethod
    def upsert_cluster_to_db(cluster_id, name, creator_qq, members, robot_qq):
        """
        跟新群
        """
        return mongodb_client_db.clusters.update(
            {"external_id": cluster_id},
            {
                "$set": {"name": name, "creator": creator_qq, "status": 0, "members": members},
                "$addToSet": {"robots": robot_qq},
            },
            True
        )

    @staticmethod
    def upsert_cluster_add_info_to_db(cluster_id, robot_qq):
        return mongodb_client_db.clusters.update(
            {"external_id": cluster_id},
            {
                "$set": {"status": 0},
                "$addToSet": {"robots": robot_qq},
            },
            True
        )

    @staticmethod
    def remove_robot_from_cluster(cluster_id, robot_qq):
        mongodb_client_db.clusters.update(
            {"external_id": cluster_id},
            {
                "$pull": {"robots": robot_qq},
            }
        )
        pass

    @staticmethod
    def robots_in_cluster(cluster_id):
        cluster = mongodb_client_db.clusters.find({"external_id": cluster_id}, {"_id": 0, "robots": 1})
        if cluster and "robots" in cluster:
            return cluster["robots"]
        return []

    @staticmethod
    def remove_member_from_cluster_db(cluster_id, qq):
        """
        退出群
        """
        return mongodb_client_db.clusters.update(
            {"external_id": cluster_id},
            {
                "$pull": {"members": {"qq": qq}},
            }
        )

    @staticmethod
    def get_admin_clusters_by_qq_from_cluster_db(qq):
        """
        通过QQ查询创建的和管理的群
        """
        clusters = mongodb_client_db.clusters.find(
            {
                "status": 0,
                "$or": [
                    {"creator": qq},
                    {"members":
                        {"$elemMatch":
                            {
                                "qq": qq,
                                "is_admin": True
                            }
                        }
                    }
                ]
            },
            {"external_id": 1, "name": 1, "_id": 0}
        )
        return clusters


class QQBindCodeDB():
    def __init__(self):
        pass

    @staticmethod
    def get_qq_bind_code(qq, code):
        now = time.time()
        qq_bind_code = mongodb_client_db.qq_bind_code.find_one({
            "qq": qq,
            "code": code,
            "create_time": {"$gt": now - 60 * 60 * 1}
        })
        return qq_bind_code

    @staticmethod
    def upsert_qq_bind_code_by_id(user_id, qq, code):
        now = time.time()
        mongodb_client_db.qq_bind_code.update(
            {"user_id": user_id, "code": code},
            {"$set": {"qq": qq, "create_time": now}},
            True
        )

    @staticmethod
    def remove_qq_bind_code(qq):
        mongodb_client_db.qq_bind_code.remove({"qq": qq})

    @staticmethod
    def remove_qq_bind_code_by_user_id(user_id):
        mongodb_client_db.qq_bind_code.remove({"user_id": user_id})


class CityDB():
    def __init__(self):
        pass

    @staticmethod
    def cities_from_db():
        return mongodb_client_db.cities.find({}, {"_id": 0}).sort("initial")


class AreaDB():
    def __init__(self):
        pass

    @staticmethod
    def area_list(self):
        return mongodb_client_db.areas.find().sort({'pin_yin': -1})


class EventTempletDB():
    def __init__(self):
        pass

    @staticmethod
    def add_event_templet_to_db(event_templet):
        mongodb_client_db.event_templet.insert(event_templet)

    @staticmethod
    def update_event_templet_status_to_db(tmeplet_id):
        mongodb_client_db.event_templet.update(
            {"id": tmeplet_id},
            {
                "$set": {"status": -1}
            }
        )


class AdminUserDB():
    def __init__(self):
        pass

    @staticmethod
    def check_user_access(username, password):
        admin_user = mongodb_client_db.admin_users.find_one({"username": username, "password": password})
        return admin_user

    @staticmethod
    def get_user_ids(admin_id):
        admin_users = mongodb_client_db.admin_users.find_one({"id": int(admin_id)}, {"_id": 0, "user_ids": 1})
        user_ids = admin_users.get("user_ids")
        return user_ids or []

    @staticmethod
    def add_user_id(admin_id, user_id):
        mongodb_client_db.admin_users.update({"id": int(admin_id)}, {"$addToSet": {"user_ids": user_id}})


class AdminDB():
    def __init__(self):
        pass

    @staticmethod
    def get_club_list(admin_id):
        user_ids = AdminUserDB.get_user_ids(admin_id)
        print "user_ids:=", user_ids
        return mongodb_client_db.clubs.find({"creator_id": {"$in": user_ids}}, {"_id": 0})

    @staticmethod
    def get_club_detail(id):
        # print "id:=", id
        club = mongodb_client_db.clubs.find_one({"id": id})
        # print "club:=", club
        return club

    @staticmethod
    def get_user_detail(id):
        user = mongodb_client_db.users.find_one({"id": id})
        return user

    @staticmethod
    def get_event_list(admin_id):
        user_ids = AdminUserDB.get_user_ids(admin_id)
        now = time.time()
        events = mongodb_client_db.events.find({
            "creator_id": {"$in": user_ids},
            "status": 0,
            # "type": "event",
            "end_time": {"$gte": now, "$lte": now + 60 * 60 * 24 * 7},
        }).sort("start_time", 1)

        return events

    @staticmethod
    def get_event_list_by_club_id(club_id):
        # print "club_id", club_id
        now = time.time()
        events = mongodb_client_db.events.find({
            "club_id": club_id,
            "status": 0,
            # "type": "event",
            "end_time": {"$gte": now, "$lte": now + 60 * 60 * 24 * 7},
        }).sort("start_time", 1)

        return events
