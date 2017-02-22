# -*- coding:utf-8 -*-
__author__ = 'Van'

from flask import request, Blueprint, current_app, jsonify
from ..utils import require_value_from_dict, model2dict
from ..mredis import RedisClient
from ..mongo import UserDB, EventDB, VenueDB, ClubDB, CityDB,EventTempletDB
from ..helpers.util_helper import get_user, user_role
from ..helpers.permission_helper import AdminPermission, UserPermission
from ..models import Event, Venue
import json
import datetime
import time
import copy
from ..utils import get_event_sign
import random

api = Blueprint('events_controller', __name__, url_prefix='')


@UserPermission()
@api.route('/event_id', methods=['GET', 'POST'])
def n_event_id():
    """
    新建俱乐部需要初始化
    """
    user_id = int(request.args.get("user_id", 0))

    user = UserDB.user_by_id_from_db(user_id)
    mobile = user.get("mobile", "")
    if not user:
        return jsonify({"code": 0, "error": "not found this user"})
    # TODO 从群信息，判断是否是创建者或者管理员，来获取群列表

    club = ClubDB.club_user_create_from_db(user_id)
    mid = "%d" % RedisClient.new_event_id()
    if club:
        club["_id"] = None
        return jsonify({"code": 1, "club": club, "id": mid, "mobile": mobile})
    else:
        return jsonify({"code": 1, "id": mid})


@UserPermission()
@api.route('/events', methods=['POST'])
def events_new():
    """
    新建
    """
    try:
        args = request.args

        user_id = int(args.get("user_id", 0))

        event = Event(args, user_id=user_id)
        st = datetime.datetime.fromtimestamp(int(args.get("start_time")))
        et = datetime.datetime.fromtimestamp(int(args.get("end_time")))
        # start_time = st + datetime.timedelta(days=-st.weekday(), hours=-st.hour, minutes=-st.minute)

        # 判断是否已经保存过了
        if RedisClient.get_event_key(getattr(event, "id", "")):
            return jsonify({"code": 1})
        RedisClient.set_event_key(getattr(event, "id", ""))

        if int(args.get("start_time")) > int(args.get("end_time")):
            current_app.logger.error("st > et ,event_id : " + getattr(event,"id",""))
            return jsonify({"code": 0,"error": "st > et "})
        if (int(args.get("end_time"))-int(args.get("start_time"))) > 3600*9*24:
            current_app.logger.error("the time is too long ,event_id : " + getattr(event,"id",""))
            return jsonify({"code": 0,"error": "the time is too long"})

        if args.get("clusters"):
            clusters = args.get("clusters").split(',')
        else:
            clusters = []
        if args.get("is_cycle") and args.get("is_cycle") == "true":

            count = EventDB.event_by_template_from_db(event.id)
            if count and count > 0:
                return jsonify({"code": 1})
            event.type = "template"
            EventDB.add_event_to_db(event.__dict__)
            event.type = "event"
            days = []
            mdays = args.get("days").split(',')
            for day in mdays:
                days.append(int(day))

            for i in range(0, 7):

                st1 = st + datetime.timedelta(days=i)
                print "days:", days
                if st1.weekday() in days:
                    print "st1", st1, st1.weekday()
                    event.start_time = time.mktime(st1.timetuple())
                    event.end_time = time.mktime((et + datetime.timedelta(days=i)).timetuple())
                    event.id = RedisClient.new_event_id()
                    event.weekday = st1.weekday()
                    event.is_cycle = "false"
                    event.template_id = int(args.get("id"))
                    signs = {}
                    if clusters.__len__() > 0:
                        for qq in clusters:
                            sign_arr = EventDB.sign_from_event_db(qq,time.mktime(st.timetuple()))
                            sign = get_event_sign(sign_arr)
                            if not sign:
                                EventDB.remove_event_from_db({"id": int(args.get("id"))})
                                EventDB.remove_event_from_db({"template_id": int(args.get("id"))})
                                return jsonify({"code": 4001, "error": qq})
                            # char, count = EventDB.events_week_max_sign_from_db(user_id, time.mktime(st.timetuple()), qq)
                            # print char, count
                            # if chr(ord(char) + count) <= "Z":
                            #     sign = chr(ord(char) + count)
                            # elif chr(ord(char) + count - 26) < char:
                            #     sign = chr(ord(char) + count - 26)
                            # else:
                            #     EventDB.remove_event_from_db({"id": int(args.get("id"))})
                            #     EventDB.remove_event_from_db({"template_id": int(args.get("id"))})
                            #     return jsonify({"code": 4001, "error": qq})
                            signs.update({qq: sign})
                    event.signs = signs
                    event.__dict__.pop("_id")
                    EventDB.add_event_to_db(event.__dict__)
                    # UserDB.add_event_to_user_db(getattr(event,"id"),user_id)
                    print "event id : ", event.id
        else:
            signs = {}
            if clusters.__len__() > 0:
                for qq in clusters:
                    sign_arr = EventDB.sign_from_event_db(qq,time.mktime(st.timetuple()))
                    sign = get_event_sign(sign_arr)
                    if not sign:
                        return jsonify({"code": 4001, "error": qq})
                    # char, count = EventDB.events_week_max_sign_from_db(user_id, time.mktime(st.timetuple()), qq)
                    # print char, count
                    # if chr(ord(char) + count) <= "Z":
                    #     sign = chr(ord(char) + count)
                    # elif chr(ord(char) + count - 26) < char:
                    #     sign = chr(ord(char) + count - 26)
                    # else:
                    #     return jsonify({"code": 4001, "error": qq})
                    signs.update({qq: sign})
            event.signs = signs
            EventDB.add_event_to_db(event.__dict__)
        # UserDB.add_event_to_user_db(getattr(event,"id"),user_id)
    except Exception, e:
        current_app.logger.error(e)
        return jsonify({"code": 0})
    return jsonify({"code": 1})


@UserPermission()
@api.route('/events/club', methods=['GET'])
def events_of_club():
    """
    获取俱乐部的所有活动
    """
    try:
        args = request.args
        page_size = int(args.get("page_size", 20))
        page_index = int(args.get("page_index", 1))
        club_id = int(require_value_from_dict(args, "club_id"))
        events = EventDB.events_of_club_from_db(club_id, page_size, page_index)

        now_time = int(time.time())
        events_copy = []
        for event in events:
            event["start_time"] = datetime.datetime.fromtimestamp(int(event["start_time"])).strftime("%Y-%m-%d %H:%M")
            if "members_count_limit" not in event or int(event["members_count_limit"]) == 0:
                event["percent"] = "0"
            else:
                event["percent"] = str(float(event["members_count"])/float(event["members_count_limit"])*100)

            if int(event["end_time"]) > now_time:
                if int(event["members_count"]) < int(event["members_count_limit"]):
                    event["status"] = "报名中"
                else:
                    event["status"] = "名额已满"
            else:
                event["status"] = "已经结束"
            events_copy.append(event)
        r_d = {
            "code": 1,
            "events": events_copy
        }
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})
    return json.dumps(model2dict(r_d))


@UserPermission()
@api.route('/events', methods=['GET'])
def events_all():
    weekdays = ["周一", "周二", "周三",  "周四", "周五", "周六", "周日"]
    try:
        args = request.args
        page_size = int(args.get("page_size", 100))
        page_index = int(args.get("page_index", 1))

        city = args.get("city", None)
        weekday = args.get("weekday", None)
        category = args.get("category", None)
        # way = args.get("way", None)
        t = int(time.time())
        m_filter = {"status": {"$gte": 0}, "end_time": {"$gt": t},"start_time":{"$gt":t-3600*24}}
        if city:
            m_filter.update({"venue.city": city})
        if weekday != "全部":
            m_filter.update(weekday=weekdays.index(weekday))
        if category != "全部":
            m_filter.update(category=category)
        # if way:
        #     lng = args.get("lng", 0)
        #     lat = args.get("lat", 0)
        #     near = {"coordinate": {"$near": [lng, lat]}}
        #     m_filter.update(venue=near)

        if weekday == "全部" and category == "全部":
            f = {"creator_id": int(args.get("user_id", 0)), "status": {"$gte": 0}, "end_time": {"$gt": t},"start_time":{"$gt":t-3600*24}}
            mine_events = EventDB.events_filter_from_db(f, 100, 1)
        else:
            mine_events = []
        events_copy = []
        events_ids = []
        now_time = int(time.time())

        for event in mine_events:
            # event["start_time"] = datetime.datetime.fromtimestamp(int(event["start_time"])).strftime("%Y-%m-%d %H:%M")
            club = ClubDB.club_info_from_db(event["club_id"])
            event["club"] = club
            if "members_count_limit" not in event or int(event["members_count_limit"]) == 0:
                event["percent"] = "0"
            else:
                event["percent"] = str(float(event["members_count"])/float(event["members_count_limit"])*100)

            if int(event["end_time"]) > now_time:
                if int(event["members_count"]) < int(event["members_count_limit"]):
                    event["status"] = "报名中"
                else:
                    event["status"] = "名额已满"
            else:
                event["status"] = "已经结束"

            events_ids.append(event.get("id"))
            events_copy.append(event)


        events = EventDB.events_filter_from_db(m_filter, page_size, page_index)
        for event in events:
            if event.get("id") in events_ids:
                continue
            club = ClubDB.club_info_from_db(event["club_id"])
            event["club"] = club
            if "members_count_limit" not in event or int(event["members_count_limit"]) == 0:
                event["percent"] = "0"
            else:
                event["percent"] = str(float(event["members_count"])/float(event["members_count_limit"])*100)

            if int(event["end_time"]) > now_time:
                if int(event["members_count"]) < int(event["members_count_limit"]):
                    event["status"] = "报名中"
                else:
                    event["status"] = "名额已满"
            else:
                event["status"] = "已经结束"

            events_copy.append(event)
        r_d = {
            "code": 1,
            "events": events_copy
        }
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})
    return json.dumps(model2dict(r_d))


@UserPermission()
@api.route('/events/mine', methods=['GET'])
def events_of_mine():
    """
    参加的 参数：published
    发布的 参数：joined
    """
    try:
        args = request.args
        # page_size = int(args.get("page_size", 20))
        # page_index = int(args.get("page_index", 1))
        user_id = int(require_value_from_dict(args, "user_id"))
        page = args.get("page", None)

        events = EventDB.events_of_user_from_db(user_id, page)

        now_time = int(time.time())
        events_copy = []
        for event in events:
            # event["start_time"] = datetime.datetime.fromtimestamp(int(event["start_time"])).strftime("%Y-%m-%d %H:%M")
            club = ClubDB.club_info_from_db(event["club_id"])
            event["club"] = club
            if "members_count_limit" not in event or "members_count" not in event or int(event["members_count_limit"]) == 0:
                event["percent"] = "0"
            else:
                event["percent"] = str(float(event["members_count"])/float(event["members_count_limit"])*100)

            if int(event["end_time"]) > now_time:
                if int(event["members_count"]) < int(event["members_count_limit"]):
                    event["status"] = "报名中"
                else:
                    event["status"] = "名额已满"
            else:
                event["status"] = "已经结束"

            events_copy.append(event)
        r_d = {
            "code": 1,
            "events": events_copy
        }
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})
    return json.dumps(model2dict(r_d))


@UserPermission()
@api.route('/events/<e_id>', methods=['GET'])
def events_show(e_id):
    """

    """
    try:
        event = EventDB.event_by_id_from_db(int(e_id))
        user_id = int(require_value_from_dict(request.args, "user_id"))
        has_joined = False
        is_creator = False
        join_count = 0
        ms = []
        if event:
            # print user_id, "=", event["creator_id"]
            if user_id == int(event["creator_id"]):
                is_creator = True
            # 完善成员列表
            for member in event["members"]:
                if member.get("id"):
                    user = get_user(member["id"])
                    if int(member["id"]) == user_id:
                        has_joined = True
                        join_count = member["join_count"]
                    ms.append(user)
                elif member.get("qq"):
                    user = UserDB.user_by_qq_from_user_db(member.get("qq"))
                    ms.append(user)
                elif member.get("user_temp"):
                    user = {"nickname": member.get("user_temp")}
                    ms.append(user)
                else:
                    pass

            event["members"] = ms
            club_id = event["club_id"]
            role = user_role(club_id, user_id)
            club = ClubDB.club_info_from_db(club_id)
            event["club"] = club

            # event["start_time"] = datetime.datetime.fromtimestamp(int(event["start_time"])).strftime("%Y-%m-%d %H:%M")
            # event["end_time"] = datetime.datetime.fromtimestamp(int(event["end_time"])).strftime("%Y-%m-%d %H:%M")
            if "members_count_limit" not in event or int(event["members_count_limit"]) == 0:
                event["percent"] = "0"
            else:
                event["percent"] = str(float(event["members_count"])/float(event["members_count_limit"])*100)

            r_d = {
                "code": 1,
                "event": event,
                "is_creator": is_creator,
                "has_joined": has_joined,
                "join_count": join_count,
                "role": role
            }
            print r_d
        else:
             return json.dumps({"code": 0})
    except Exception, e:
        current_app.logger.error(e)
        return json.dumps({"code": 0})
    return json.dumps(model2dict(r_d))


@UserPermission()
@api.route('/events/<e_id>/members', methods=['GET'])
def events_members(e_id):
    """

    """
    try:
        event = EventDB.event_by_id_from_db(int(e_id))
        images_arr = ['/static/app/img/headimgs/user1.png','/static/app/img/headimgs/user2.png','/static/app/img/headimgs/user3.png','/static/app/img/headimgs/user4.png','/static/app/img/headimgs/user5.png']

        os = [get_user(event["creator_id"])]
        ms = []
        # 完善成员列表
        for member in event["members"]:
            if member.get("id"):
                user = get_user(member["id"])
                user["id"] = member["id"]
                user["join_count"] = member.get("join_count")
                user["nickname"] = user.get("nickname")
                user["nickname_alia"] = user.get("nickname") + "(共%s人)" % member.get("join_count")
            elif member.get("user_temp"):
                nickname_alia = member.get("user_temp") + "(共%s人)" % member.get("join_count")
                user = {
                    "nickname": member.get("user_temp"),
                    "nickname_alia": nickname_alia
                }
                user["join_count"] = member.get("join_count")
            head_img_url = user.get("head_img_url")
            if not head_img_url:
                index = random.randint(0, 4)
                head_img_url = images_arr[index]
                user["head_img_url"] = head_img_url
            ms.append(user)

        r_d = {
            "code": 1,
            "managers": os,
            "members": ms
        }
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})
    return json.dumps(model2dict(r_d))



@UserPermission()
@api.route('/events/<e_id>/join', methods=['POST'])
def events_join(e_id):
    # try:
    event_id = int(e_id)
    user_id = int(require_value_from_dict(request.args, "user_id"))
    join_count = int(require_value_from_dict(request.args, "join_count"))
    join_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    exit_count = int(request.args.get("exit_count", 1))

    nickname = request.args.get("nickname")

    event = EventDB.event_by_id_from_db(event_id)
    if event:
        creator_id = event.get("creator_id")
        creator = UserDB.user_by_id_from_db(creator_id)
        if join_count > 0:
            if not event.get("members_count"):
                member_count = 0
            else:
                member_count = event.get("members_count")
            if (member_count+join_count) <= event.get("members_count_limit"):

                if nickname:
                    # 帮一个昵称报名
                    member = EventDB.get_member_by_nick_from_event_db(event_id, nickname)
                    if member:
                        already_join_count = member.get("join_count", 0)
                        if already_join_count >= join_count:
                            return jsonify({'code': 1005, 'exist': True, 'errmsg': 'already join this activity '})
                        more_count = join_count - already_join_count
                        print "more_count:=", more_count

                        EventDB.remove_member_by_nick_from_event_db(event_id, nickname, already_join_count)
                        EventDB.add_member_by_nick_to_event_db(
                            event_id,
                            nickname,
                            creator.get("qq"),
                            join_count,
                            join_time
                        )
                    else:
                        EventDB.add_member_by_nick_to_event_db(
                            event_id,
                            nickname,
                            creator.get("qq"),
                            join_count,
                            join_time
                        )
                elif user_id:
                        member = EventDB.get_member_by_id_from_event_db(event_id, user_id)
                        if member:
                            already_join_count = member.get("join_count", 0)
                            EventDB.remove_member_from_event_db(event_id, user_id, already_join_count)
                            UserDB.remove_event_from_user_db(event_id, user_id)
                        EventDB.add_member_to_event_db(event_id, user_id, join_count, join_time)
                        UserDB.add_event_to_user_db(event_id, user_id)
            else:
                return json.dumps({"code": 4002, "error": "人数超出限制，报名失败"})
        elif exit_count > 0:
            if user_id:
                user = UserDB.user_by_id_from_db(user_id)
                if user.get("events"):
                    events = user.get("events")
                    if event_id in events:
                        # 取消报名
                        EventDB.remove_member_from_event_db(event_id, user_id, exit_count)
                        UserDB.remove_event_from_user_db(event_id, user_id)
            elif nickname:
                activity_member = EventDB.get_member_by_nick_from_event_db(event_id, nickname)
                EventDB.remove_member_by_nick_from_event_db(event_id, nickname, activity_member.get("join_count"))

        else:
            return json.dumps({"code": 0, "error": "参数错误"})
    else:
        return json.dumps({"code": 0, "error": "活动不存在"})
    # except Exception, e:
    #     current_app.logger.error(e.message)
    #     return json.dumps({"code": 602, "error": "入库失败"})

    return json.dumps({"code": 1})


@UserPermission()
@api.route('/events/<e_id>/exit', methods=['POST'])
def events_exit(e_id):
    try:
        ids = request.args.get("ids")
        member_ids = ids.split(",")
        nicknames = request.args.get("nicknames")
        event_nicknames = nicknames.split(",")

        print member_ids, event_nicknames

        event = EventDB.event_by_id_from_db(int(e_id))

        if not event:
            return

        # count = 0
        # mems = []

        for id in member_ids:
            event_member = EventDB.get_member_by_id_from_event_db(int(e_id), int(id))
            if event_member:
                EventDB.remove_member_from_event_db(
                    int(e_id), int(id), event_member.get("join_count"))
                UserDB.remove_event_from_user_db(int(e_id), int(id))

        for nickname in event_nicknames:
            event_member = EventDB.get_member_by_nick_from_event_db(int(e_id), nickname)
            if event_member:
                EventDB.remove_member_by_nick_from_event_db(int(e_id), nickname, event_member.get("join_count"))

    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 602, "error": "入库失败"})

    return json.dumps({"code": 1})


@AdminPermission()
@api.route('/events/update/<e_id>', methods=['POST'])
def events_update(e_id):
    # try:
    event_id = int(e_id)
    user_id = int(require_value_from_dict(request.args, "user_id"))
    event = Event(request.args, user_id, True)
    if request.args.get("clusters"):
        clusters = request.args.get("clusters").split(',')
    else:
        clusters = []
    event.clusters = clusters
    # 停止周期活动
    old_event = EventDB.event_by_id_from_db(event_id)
    if old_event and old_event.get("template_id"):
        EventDB.remove_event_from_db({"id": int(old_event.get("template_id"))})
    old_clusters = old_event.get("clusters")
    event.signs = old_event["signs"]
    if clusters.__len__() > 0:
        for cluster in clusters:
            if cluster not in old_event["clusters"]:
                old_clusters.append(cluster)
                st = datetime.datetime.fromtimestamp(int(event.start_time))
                # char, count = EventDB.events_week_max_sign_from_db(user_id, time.mktime(st.timetuple()), cluster)
                # print char, count
                # if chr(ord(char) + count) <= "Z":
                #     sign = chr(ord(char) + count)
                # elif chr(ord(char) + count - 26) < char:
                #     sign = chr(ord(char) + count - 26)
                # else:
                #     sign = "*"
                sign_arr = EventDB.sign_from_event_db(cluster,time.mktime(st.timetuple()))
                sign = get_event_sign(sign_arr)
                if not sign:
                    return jsonify({"code": 4001, "error": cluster})
                event.signs.update({cluster: sign})
    event.clusters = old_clusters
    EventDB.update_event_to_db(event_id, model2dict(event.__dict__))
    return json.dumps({"code": 1})
    # except Exception, e:
    #     current_app.logger.error(e.message)
    #     return json.dumps({"code": 0})


@AdminPermission()
@api.route('/events/<e_id>/cancel', methods=['POST'])
def events_cancel(e_id):
    """
    取消
    """
    try:
        # user_id = int(args.get("user_id", 0))
        # club_id = int(args.get("club_id", 0))
        event_id = int(e_id)
        # 停止周期活动
        old_event = EventDB.event_by_id_from_db(event_id)
        if old_event and old_event.get("template_id"):
            EventDB.remove_event_from_db({"id": int(old_event.get("template_id"))})
        # if is_manager(club_id, user_id):
        EventDB.update_event_cancel_to_db(event_id)
        return json.dumps({"code": 1})
        # else:
        #     return json.dumps({"code": 0, "error": "lack_manager_authorization",
        #                        "error_desc": "对不起，你没有管理员权限!"})
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})


@api.route('/venue_id', methods=['GET', 'POST'])
def n_venue_id():
    """新建俱乐部需要初始化
    """
    return "%d" % RedisClient.new_venue_id()


@api.route('/venues', methods=['POST'])
def venues_new():
    """新建
    """
    try:
        args = request.args
        user_id = int(args.get("user_id", 0))

        venue = Venue(args, user_id=user_id)
        # 入库活动
        VenueDB.add_venue_to_db(model2dict(venue.__dict__))

    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})
    return json.dumps({"code": 1})


@api.route('/venues_search', methods=['GET'])
def venues_search():
    """新建
    """
    try:
        key = request.args.get("key", "")
        venues = VenueDB.venues_searching_from_db(key)
        venues_copy = []
        for venue in venues:
            venues_copy.append(venue)
        # 入库活动
        r_d = {
            "code": 1,
            "venues": venues_copy
        }
        return json.dumps(model2dict(r_d))
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})


@api.route('/cities', methods=['GET'])
def cities_all():
    """
    获取所以城市列表
    """
    try:
        cities = CityDB.cities_from_db()
        cities_copy = []
        for city in cities:
            cities_copy.append(city)

        r_d = {
            "code": 1,
            "cities": cities_copy
        }
        return json.dumps(r_d)
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})