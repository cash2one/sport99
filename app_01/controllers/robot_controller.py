# coding:utf-8
__author__ = 'zhaojm'

from flask import Blueprint, current_app, request, jsonify
import json
from ..mongo import EventDB, ClusterDB, UserDB, QQBindCodeDB
from threading import Thread
import time, datetime
from ..utils import model2dict
from ..mredis import RedisClient


api = Blueprint('robot_controller', __name__, url_prefix='/qq')


@api.route('/', methods=['GET'])
def index():
    return 'robot index'


# =========================utils begin=============================
def select_func(cmd, func_dict, params):
    func = func_dict.get(cmd)
    if not func:
        errmsg = 'bad cmd: ' + cmd
        return jsonify({'retcode': -1, 'errmsg': errmsg})

    return func(params)

# =========================utils end=============================


# =========================receive begin=============================
@api.route('/receive', methods=['POST'])
def receive():
    print('---------key values begin--------------------------')
    for key in request.form:
        print key, ': ', request.form[key]
    print('-----------key values end------------------------')

    data = request.form.get('data')
    cmd = request.form.get('cmd')
    if not data or not cmd:
        return jsonify({'code': -1, 'errmsg': 'data or cmd not found'})

    data_json = json.loads(data)
    func_dict = {
        'getActivityList': get_activity_list,
        'getActivityDetail': get_activity_detail,
        'joinActivity': join_activity,
        'cancelJoinActivity': cancel_join_activity,
        'helpJoinActivity': help_join_activity,
        'helpCancelJoinActivity': help_cancel_join_activity,
        'speJoinActivity': spe_join_activity,
        'speCancelJoinActivity': spe_cancel_join_activity,
        'sendNormalIM': send_normal_im,
        'sendTmpIM': send_tmp_im,
        'get_cluster_events_count': get_cluster_events_count,
    }

    return select_func(cmd, func_dict, data_json)


def get_activity_list(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = params.get('qq')
    try:
        if RedisClient.get_robot_qq_key(qq):
            errmsg = "qq lock, cluster_id:=" + external_id + ", robot:=" + robot + ", qq:=" + qq
            return jsonify({'retcode': 1010, 'exist': True, 'errmsg': errmsg})
        RedisClient.set_robot_qq_key(qq)

        act_list_from_db = EventDB.events_of_cluster_from_db(external_id, None, None)
        acts_copy = []
        for act in act_list_from_db:
            start_time = time.strftime("%H:%M", time.localtime(act.get("start_time")))
            end_time = time.strftime("%H:%M", time.localtime(act.get("end_time")))
            start_day = time.strftime("%Y.%m.%d", time.localtime(act.get("start_time")))
            act_copy = {"sign": act.get("signs", {}).get(external_id, ""), "name": act.get("name"),
                        "start_day": start_day,
                        "venue_name": act.get("venue", {}).get("title", ""),
                        "start_time": start_time, "end_time": end_time,
                        "weekday": act.get("weekday")}
            acts_copy.append(act_copy)
        RedisClient.del_robot_qq_key(qq)
        return jsonify({'retcode': 0, 'exist': True, 'result': acts_copy})

    except Exception, e:
        current_app.logger.error(e.message)
        RedisClient.del_robot_qq_key(qq)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def get_activity_detail(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    if sign:
        sign = sign.upper()
    try:
        if RedisClient.get_robot_qq_key(qq):
            errmsg = "qq lock, cluster_id:=" + external_id + ", robot:=" + robot + ", qq:=" + qq
            return jsonify({'retcode': 1010, 'exist': True, 'errmsg': errmsg})
        RedisClient.set_robot_qq_key(qq)

        # print "1111111111"
        act = EventDB.event_of_cluster_by_sign_from_db(external_id, sign, None, None)
        if not act:
            RedisClient.del_robot_qq_key(qq)
            return jsonify({'retcode': 1004, 'errmsg': 'not found this activity'})
        # print "222222222222"
        user = UserDB.user_info_from_db_by_user_id(act.get("creator_id"))
        if not user:
            errmsg = "data error, creator not found, creator_id:=" + str(act.get("creator_id")), "event_id: " + str(
                act.get("id"))
            current_app.logger.error(errmsg)
            RedisClient.del_robot_qq_key(qq)
            return jsonify({"retcode": 2011, "errmsg": errmsg})
        # print "3333333333333"
        members = act.get("members")
        members_copy = []
        for member in members:
            id = member.get("id")
            # qq = member.get("qq")
            user_temp = member.get("user_temp")

            member_copy = {
                "gua": member.get("join_count") - 1,
                "help_qq": member.get("help_qq", "0"),
                "channel": member.get("channel", "微信"),
            }

            if id:
                user_from_db = UserDB.user_by_id_from_db(id)
                if not user_from_db:
                    # raise Exception("not found this user: id=" + id)
                    errmsg = "data error, not found event member from users db, event_id:=" + str(
                        act.get("id")) + ", user_id:=" + str(id)
                    current_app.logger.error(errmsg)
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({"retcode": 2011, "errmsg": errmsg})
                cluster_member = ClusterDB.find_cluster_member_from_db(user_from_db.get("qq", "-1"), external_id)
                member_card = None
                if cluster_member:
                    member_card = cluster_member.get("card")
                    if member_card == "": member_card = None
                member_copy.update({
                    "nick": member_card or user_from_db.get("nickname")
                            or user_from_db.get("wechat", {}).get("nickname", ""),
                    "qq": user_from_db.get("qq", "0"),
                })
            elif user_temp:
                member_copy.update({
                    "nick": user_temp,
                    "qq": -1,
                })
            else:
                errmsg = "data error, members error, not found id or user_temp, event_id:=" + str(act.get("id"))
                current_app.logger.error(errmsg)
                RedisClient.del_robot_qq_key(qq)
                return jsonify({"retcode": 2011, "errmsg": errmsg})
            members_copy.append(member_copy)
        # print "4444444444444444"
        start_time = time.strftime("%H:%M", time.localtime(act.get("start_time")))
        end_time = time.strftime("%H:%M", time.localtime(act.get("end_time")))
        start_day = time.strftime("%Y.%m.%d", time.localtime(act.get("start_time")))

        cluster_member = ClusterDB.find_cluster_member_from_db(user.get("qq", "-1"), external_id)
        member_card = None
        if cluster_member:
            member_card = cluster_member.get("card")
            if member_card == "": member_card = None
        creator_name = member_card or user.get("nickname") or user.get("wechat", {}).get("nickname")
        act_copy = {"sign": act.get("signs", {}).get(external_id, ""), "name": act.get("name"),
                    "venue_name": act.get("venue", {}).get("title", ""),
                    "start_time": start_time, "end_time": end_time,
                    "weekday": act.get("weekday"), "start_day": start_day, "creator_name": creator_name,
                    "mobile": act.get("mobile"), "member_count_limit": act.get("members_count_limit"),
                    "members": members_copy, "id": act.get("id")}
        # print "55555555555555"
        RedisClient.del_robot_qq_key(qq)
        return jsonify({'retcode': 0, 'exist': True, 'result': act_copy})

    except Exception, e:
        current_app.logger.error(e.message)
        RedisClient.del_robot_qq_key(qq)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    gua = params.get('gua')

    return common_join_activity(sign, robot, external_id, qq, gua, None, None)


def cancel_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))

    return common_cancel_join_activity(sign, robot, external_id, qq, None, None)


def help_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    gua = params.get('gua')
    friend_qq = str(params.get('friendQQ'))

    return common_join_activity(sign, robot, external_id, qq, gua, friend_qq, None)


def help_cancel_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    friend_qq = str(params.get('friendQQ'))

    return common_cancel_join_activity(sign, robot, external_id, qq, friend_qq, None)


def spe_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    gua = params.get('gua')
    friend = str(params.get('friend'))

    return common_join_activity(sign, robot, external_id, qq, gua, None, friend)


def spe_cancel_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    friend = str(params.get('friend'))

    return common_cancel_join_activity(sign, robot, external_id, qq, None, friend)


def common_join_activity(sign, robot, external_id, qq, gua, friend_qq, friend_nick):

    try:
        if RedisClient.get_robot_qq_key(qq):
            errmsg = "qq lock, cluster_id:=" + external_id + ", robot:=" + robot + ", qq:=" + qq
            return jsonify({'retcode': 1010, 'exist': True, 'errmsg': errmsg})
        RedisClient.set_robot_qq_key(qq)
        if sign:
            sign = sign.upper()

        # 获取activity
        # 报名 sign 活动
        act = EventDB.event_of_cluster_by_sign_from_db(external_id, sign, None, None)
        if not act:
            RedisClient.del_robot_qq_key(qq)
            return jsonify({'retcode': 1004, 'exist': True, 'errmsg': 'not found this activity '})

        # if(int(act.get("members_count_limit", 0)) <
        #        (int(act.get("members_count", 0)) + int(gua) + 1)):
        #     RedisClient.del_robot_qq_key(qq)
        #     return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members > count limit '})

        if friend_nick:
            # 帮一个nick报名
            member = EventDB.get_member_by_nick_from_event_db(act.get("id"), friend_nick)
            if member:
                already_join_count = member.get("join_count", 0)
                if already_join_count >= gua + 1:
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 1005, 'exist': True, 'errmsg': 'already join this activity '})

                more_count = int(gua) + 1 - already_join_count
                print "more_count:=", more_count

                if(act.get("members_count_limit", 0) <
                           act.get("members_count", 0) + more_count):
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members count > count limit '})

                # EventDB.update_nick_event_member_join_count(act.get("id"), friend_nick, gua + 1, more_count, None)
                EventDB.remove_member_by_nick_from_event_db(act.get("id"), friend_nick, already_join_count)
                EventDB.add_member_by_nick_to_event_db(act.get("id"), friend_nick, qq, gua + 1, None)

            else:
                if(act.get("members_count_limit", 0) <
                               act.get("members_count", 0) + gua + 1):
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members > count limit '})
                EventDB.add_member_by_nick_to_event_db(act.get("id"), friend_nick, qq, gua + 1, None)

        elif friend_qq:
            # 帮一个qq报名
            # print "帮一个QQ报名"
            user = UserDB.user_by_qq_from_user_db(friend_qq)
            # print "11111111111"
            if not user:
                # print "not user"
                cluster_member = ClusterDB.find_cluster_member_from_db(friend_qq, external_id)
                if not cluster_member:
                    RedisClient.del_robot_qq_key(qq)
                    errmsg = "data error, friend qq not found, cluster_id:=" + str(external_id) + ", friend_qq:=" + str(friend_qq)
                    current_app.logger.error(errmsg)
                    return jsonify({"retcode": 2011, 'exist': True, "errmsg": errmsg})
                    # return jsonify({'retcode': -1, 'exist': True, 'errmsg': 'not found this cluster member '})
                user_id = RedisClient.new_user_id()
                UserDB.insert_user_by_qq_to_db(user_id, friend_qq, cluster_member.get("nick"))
                user = UserDB.user_by_id_from_db(user_id)

                if(act.get("members_count_limit", 0) <
                       act.get("members_count", 0) + gua + 1):
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members > count limit '})
                UserDB.add_event_by_qq_to_user_db(friend_qq, act.get("id"))
                EventDB.add_member_by_friend_qq_to_event_db(act.get("id"), user.get("id"), qq, gua + 1, None)

            else:
                # print "has user"
                event_ids = UserDB.events_by_qq_from_user_db(friend_qq)
                if event_ids and act.get("id") in event_ids:
                    member = EventDB.get_member_by_id_from_event_db(act.get("id"), user.get("id"))
                    if not member:
                        RedisClient.del_robot_qq_key(qq)
                        errmsg = "data error,  event_id:=" + str(act.get("id")) + ", user_id:=" + str(user.get("id"))
                        current_app.logger.error(errmsg)
                        return jsonify({"retcode": 2011, 'exist': True, "errmsg": errmsg})

                    already_join_count = member.get("join_count")
                    if already_join_count >= gua + 1:
                        RedisClient.del_robot_qq_key(qq)
                        return jsonify({'retcode': 1005, 'exist': True, 'errmsg': 'already join this activity '})

                    more_count = int(gua) + 1 - already_join_count
                    print "more_count:=", more_count

                    if(act.get("members_count_limit", 0) <
                               act.get("members_count", 0) + more_count):
                        RedisClient.del_robot_qq_key(qq)
                        return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members count > count limit '})

                    # EventDB.update_event_member_join_count(act.get("id"), user.get("id"), gua + 1, more_count, None)
                    EventDB.remove_member_from_event_db(act.get("id"), user.get("id"), already_join_count)
                    EventDB.add_member_by_friend_qq_to_event_db(act.get("id"), user.get("id"), qq, gua + 1, None)

                else:
                    if(act.get("members_count_limit", 0) <
                           act.get("members_count", 0) + gua + 1):
                        RedisClient.del_robot_qq_key(qq)
                        return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members > count limit '})
                    UserDB.add_event_by_qq_to_user_db(friend_qq, act.get("id"))
                    EventDB.add_member_by_friend_qq_to_event_db(act.get("id"), user.get("id"), qq, gua + 1, None)


        else:
            # 自己报名

            user = UserDB.user_by_qq_from_user_db(qq)
            if not user:
                cluster_member = ClusterDB.find_cluster_member_from_db(qq, external_id)
                if not cluster_member:
                    RedisClient.del_robot_qq_key(qq)
                    errmsg = "data error, not found this cluster members, cluster_id:=" + str(external_id) + ", qq:=" + str(qq)
                    current_app.logger.error(errmsg)
                    return jsonify({'retcode': 2011, 'exist': True, 'errmsg': errmsg})
                user_id = RedisClient.new_user_id()
                UserDB.insert_user_by_qq_to_db(user_id, qq, cluster_member.get("nick"))
                user = UserDB.user_by_id_from_db(user_id)

                if(act.get("members_count_limit", 0) <
                       act.get("members_count", 0) + gua + 1):
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members > count limit '})
                UserDB.add_event_by_qq_to_user_db(qq, act.get("id"))
                EventDB.add_member_by_qq_self_to_event_db(act.get("id"), user.get("id"), gua + 1, None)

            else:
                event_ids = UserDB.events_by_qq_from_user_db(qq)

                if event_ids and act.get("id") in event_ids:
                    member = EventDB.get_member_by_id_from_event_db(act.get("id"), user.get("id"))
                    if not member:
                        RedisClient.del_robot_qq_key(qq)
                        errmsg = "data error, event_id:=" + str(act.get("id")) + ", user_id:=" + str(user.get("id"))
                        current_app.logger.error(errmsg)
                        return jsonify({"retcode": 2011, 'exist': True, "errmsg": errmsg})

                    already_join_count = member.get("join_count", 0)
                    if already_join_count >= gua + 1:
                        RedisClient.del_robot_qq_key(qq)
                        return jsonify({'retcode': 1005, 'exist': True, 'errmsg': 'already join this activity '})

                    more_count = int(gua) + 1 - already_join_count
                    print "more_count:=", more_count

                    if(act.get("members_count_limit", 0) <
                               act.get("members_count", 0) + more_count):
                        RedisClient.del_robot_qq_key(qq)
                        return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members count > count limit '})

                    # EventDB.update_event_member_join_count(act.get("id"), user.get("id"), gua + 1, more_count, None)
                    EventDB.remove_member_from_event_db(act.get("id"), user.get("id"), already_join_count)
                    EventDB.add_member_by_qq_self_to_event_db(act.get("id"), user.get("id"), gua + 1, None)
                else:

                    if(act.get("members_count_limit", 0) <
                           act.get("members_count", 0) + gua + 1):
                            RedisClient.del_robot_qq_key(qq)
                            return jsonify({'retcode': 1006, 'exist': True, 'errmsg': 'members > count limit '})
                    UserDB.add_event_by_qq_to_user_db(qq, act.get("id"))
                    EventDB.add_member_by_qq_self_to_event_db(act.get("id"), user.get("id"), gua + 1, None)

        print "get act detail"
        RedisClient.del_robot_qq_key(qq)
        return get_activity_detail({
            "robot": robot,
            "sign": act.get("signs", {}).get(external_id),
            "externalId": external_id,
            "qq": qq
        })

    except Exception, e:
        current_app.logger.error(e.message)
        RedisClient.del_robot_qq_key(qq)
        return jsonify({'retcode': -1, 'exist': True, 'errmsg': e.message})


def common_cancel_join_activity(sign, robot, external_id, qq, friend_qq, friend_nick):
    try:
        if RedisClient.get_robot_qq_key(qq):
            errmsg = "qq lock, cluster_id:=" + external_id + ", robot:=" + robot + ", qq:=" + qq
            return jsonify({'retcode': 1010, 'exist': True, 'errmsg': errmsg})
        RedisClient.set_robot_qq_key(qq)
        if sign:
            sign = sign.upper()

        if sign:
            # 取消单个活动sign
            # 获取活动
            act = EventDB.event_of_cluster_by_sign_from_db(external_id, sign, None, None)
            if not act:
                RedisClient.del_robot_qq_key(qq)
                return jsonify({'retcode': 1004, 'exist': True, 'errmsg': 'not found this activity '})

            a_list = []
            if friend_nick:
                # 删除nick报名
                activity_member = EventDB.get_member_by_nick_from_event_db(int(act.get("id")), friend_nick)
                if not activity_member:
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 0, 'exist': True, 'result': []})

                EventDB.remove_member_by_nick_from_event_db(int(act.get("id")), friend_nick,
                                                            activity_member.get("join_count"))
                a_list = [model2dict(act)]
            elif friend_qq:
                # print "帮取消"
                user = UserDB.user_by_qq_from_user_db(friend_qq)
                if not user:
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 0, 'exist': True, 'result': []})
                # print "111111111111"
                event_ids = user.get("events")
                if not event_ids or (act.get("id") not in event_ids):
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 0, 'exist': True, 'result': []})

                activity_member = EventDB.get_member_by_id_from_event_db(act.get("id"), user.get("id"))
                if not activity_member:
                    RedisClient.del_robot_qq_key(qq)
                    errmsg = "data error, event_id:=" + str(act.get("id")) + ", user_id:=", str(user.get("id"))
                    current_app.logger.error(errmsg)
                    return jsonify({'retcode': 2011, 'exist': True, 'errmsg': errmsg})
                # print "555555555555555"
                EventDB.remove_member_from_event_db(
                    act.get("id"), user.get("id"), activity_member.get("join_count"))
                UserDB.remove_event_from_user_db(act.get("id"), user.get("id"))
                a_list = [model2dict(act)]
            else:
                # print "删除自己报名"
                user = UserDB.user_by_qq_from_user_db(qq)
                if not user:
                     RedisClient.del_robot_qq_key(qq)
                     return jsonify({'retcode': 0, 'exist': True, 'result': []})
                    # ret = UserDB.upsert_user_qq_to_db(qq, cluster_member.get("nick"))
                # print "11111111"
                event_ids = user.get("events")
                # print "event_ids", event_ids
                if not event_ids or (act.get("id") not in event_ids):
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({'retcode': 0, 'exist': True, 'result': []})
                # print "2222222222222222"
                activity_member = EventDB.get_member_by_id_from_event_db(act.get("id"), user.get("id"))
                if not activity_member:
                    RedisClient.del_robot_qq_key(qq)
                    errmsg = "data error, event_id:=" + str(act.get("id")) + ", user_id:=" + str(user.get("id"))
                    current_app.logger.error(errmsg)
                    return jsonify({'retcode': 2011, 'exist': True, 'errmsg': errmsg})
                # print "555555555555555"
                EventDB.remove_member_from_event_db(
                    act.get("id"), user.get("id"), activity_member.get("join_count"))
                UserDB.remove_event_from_user_db(act.get("id"), user.get("id"))
                a_list = [model2dict(act)]
            # print "777777777777777777777777"
            a_list_copy = []
            if a_list:
                for a in a_list:
                    a_copy = {}
                    a_copy["id"] = a.get("id")
                    a_copy["sign"] = a.get("signs", {}).get(external_id, "")
                    a_copy["venue_name"] = a.get("venue", {}).get("title", "")
                    # current_app.logger.info(a_copy)
                    a_list_copy.append(a_copy)
            RedisClient.del_robot_qq_key(qq)
            return jsonify({'retcode': 0, 'exist': True, 'result': a_list_copy})

        else:
            # 取消所有活动
            if friend_nick:
                # 取消nick报名
                a_list = EventDB.remove_members_by_nick_from_event_db(external_id, friend_nick)

            elif friend_qq:
                # 帮取消
                user = UserDB.user_by_qq_from_user_db(friend_qq)
                if not user:
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({"retcode": 0, 'exist': True, "result": []})
                event_ids = user.get("events")
                if not event_ids:
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({"retcode": 0, 'exist': True, "result": []})

                events = EventDB.events_of_cluster_from_db(external_id, None, None)

                cluster_event_ids = []
                if events:
                    for event in events:
                        cluster_event_ids.append(event.get("id"))
                print "event_ids:=", event_ids
                print "cluster_event_ids:=", cluster_event_ids
                cluster_join_event_ids = list(set(event_ids).intersection(set(cluster_event_ids)))
                print "clusyter_join_event_ids:=", cluster_join_event_ids
                for event_id in cluster_join_event_ids:
                    activity_member = EventDB.get_member_by_id_from_event_db(event_id, user.get("id"))
                    if not activity_member:
                        RedisClient.del_robot_qq_key(qq)
                        errmsg = "data error, event_id:=" + str(event_id) + ", user_id:=" + str(user.get("id"))
                        current_app.logger.error(errmsg)
                        return jsonify({'retcode': 2011, 'exist': True, 'errmsg': errmsg})
                    EventDB.remove_member_from_event_db(
                        event_id, user.get("id"), activity_member.get("join_count"))
                    UserDB.remove_event_from_user_db(event_id, user.get("id"))

                a_list = EventDB.events_from_db_by_event_ids(cluster_join_event_ids)
            else:
                # 取消自己报名
                # print "1111111"
                user = UserDB.user_by_qq_from_user_db(qq)
                if not user:
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({"retcode": 0, 'exist': True, "result": []})
                event_ids = user.get("events")
                if not event_ids:
                    RedisClient.del_robot_qq_key(qq)
                    return jsonify({"retcode": 0, 'exist': True, "result": []})
                # print "2222222"
                events = EventDB.events_of_cluster_from_db(external_id, None, None)
                cluster_event_ids = []
                if events:
                    for event in events:
                        cluster_event_ids.append(event.get("id"))
                # print "3333333"
                cluster_join_event_ids = list(set(event_ids).intersection(set(cluster_event_ids)))
                print "cluster_join_event_ids:=", cluster_join_event_ids
                for event_id in cluster_join_event_ids:
                    activity_member = EventDB.get_member_by_id_from_event_db(event_id, user.get("id"))
                    if not activity_member:
                        RedisClient.del_robot_qq_key(qq)
                        errmsg = "data error, event_id:=" + str(event_id) + ", user_id:=" + str(user.get("id"))
                        current_app.logger.error(errmsg)
                        return jsonify({'retcode': 2011, 'exist': True, 'errmsg': errmsg})
                    EventDB.remove_member_from_event_db(
                        event_id, user.get("id"), activity_member.get("join_count"))
                    UserDB.remove_event_from_user_db(event_id, user.get("id"))
                # print "4444444"
                a_list = EventDB.events_from_db_by_event_ids(cluster_join_event_ids)
                print "a_list:=", a_list
            # print "5555555"
            a_list_copy = []
            if a_list:
                for a in a_list:
                    a_copy = {}
                    a_copy["id"] = a.get("id")
                    a_copy["sign"] = a.get("signs", {}).get(external_id, "")
                    a_copy["venue_name"] = a.get("venue", {}).get("title", "")
                    # current_app.logger.info(a_copy)
                    a_list_copy.append(a_copy)
            RedisClient.del_robot_qq_key(qq)
            return jsonify({'retcode': 0, 'exist': True, 'result': a_list_copy})

    except Exception, e:
        current_app.logger.error(e.message)
        RedisClient.del_robot_qq_key(qq)
        return jsonify({'retcode': -1, 'exist': True, 'errmsg': e.message})


def get_cluster_events_count(params):
    external_id = str(params.get("externalId"))
    qq = str(params.get("qq"))
    robot = str(params.get("robot"))
    try:
        if RedisClient.get_robot_qq_key(qq):
            errmsg = "qq lock, cluster_id:=" + external_id + ", robot:=" + robot + ", qq:=" + qq
            return jsonify({'retcode': 1010, 'exist': True, 'errmsg': errmsg})
        RedisClient.set_robot_qq_key(qq)

        count = EventDB.get_cluster_events_count(external_id)

        RedisClient.del_robot_qq_key(qq)
        return jsonify({"retcode": 0, "result": count})
    except Exception, e:
        current_app.logger.error(e.message)
        RedisClient.del_robot_qq_key(qq)
        return jsonify({"retcode": -1, "errmsg": e.message})


def send_tmp_im(params):
    return send_normal_im(params)


def send_normal_im(params):
    robot = str(params.get('robot'))
    qq = str(params.get('qq'))
    message = params.get('message')
    send_time = params.get('sendTime')

    func_dict = {
        '99': user_bd,
        'other': do_other_im,
    }
    try:
        # 绑定成功
        user = UserDB.user_by_qq_from_user_db(qq)
        if user and user.get("wechat"):
            return jsonify({"retcode": 0, "result": "邀请“小九”到你的QQ群即可绑定QQ群"})

        return select_func(message, func_dict, params)

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'exist': True, 'errmsg': e.message})


def user_bd(params):

    qq = str(params.get('qq'))
    message = params.get('message')
    send_time = params.get('sendTime')
    try:
        qq_bind_code = QQBindCodeDB.get_qq_bind_code(qq, message.upper())
        if not qq_bind_code:
            return jsonify({"retcode": 0, "exist": True,
                            "result": "请关注运动九九公众号我就能帮你服务啦~~\r\n公众号：yundongjiujiu"})
        qq_user = UserDB.user_by_qq_from_user_db(qq)
        if qq_user and qq_user.get("wechat"):
            raise Exception("qq has bind")
        user_id = qq_bind_code.get("user_id")
        user = UserDB.user_by_id_from_db(user_id)
        if not user:
            raise Exception(' no found this user user_id:=' + user_id)
        if qq_user:
            qq_user_event_ids = qq_user.get("events", [])
            user_event_ids = user.get("events", [])
            for event_id in qq_user_event_ids:
                activity_member = EventDB.get_member_by_id_from_event_db(event_id, qq_user.get("id"))
                if not activity_member:
                    errmsg = 'data error, event_id:=' + str(event_id) + ", user_id:=" + str(qq_user.get("id"))
                    current_app.logger.error(errmsg)
                    return jsonify({'retcode': 2011, 'exist': True, 'errmsg': errmsg})
                if event_id in user_event_ids:
                    # remove
                    EventDB.remove_member_from_event_db(event_id, qq_user.get("id"), activity_member.get("join_count"))
                else:
                    # 转到user
                    EventDB.add_member_to_event_db(event_id, user.get("id"), activity_member.get("join_count"), None)
                    EventDB.remove_member_from_event_db(event_id, qq_user.get("id"), activity_member.get("join_count"))
                    UserDB.add_event_to_user_db(event_id, user.get("id"))
            UserDB.remove_user_by_user_id(qq_user.get("id"))
        QQBindCodeDB.remove_qq_bind_code(qq)
        old_qq = user.get("qq")
        #  old_qq， QQ号有旧的账户，可以恢复，没有旧的账户，怎么办？还需要给他创建用户吗？不用了
        UserDB.revert_old_qq_user_from_user_db(old_qq)
        UserDB.upsert_user_qq_by_id_to_db(user_id, qq)
        return jsonify({"retcode": 0, "result": "验证成功，邀请“小九”到你的QQ群即可绑定你的QQ群"})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'exist': True, 'errmsg': e.message})


def do_other_im(params):
    qq = str(params.get('qq'))
    '''
    检查qq是否绑定到用户，返回不同话
    '''
    try:
        return jsonify({"retcode": 0, "result": "请关注运动九九公众号我就能帮你服务啦~~\r\n公众号：yundongjiujiu"})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})

# ========================= receive end =============================


# =========================sync begin=============================
@api.route('/sync', methods=['POST'])
def sync():
    print('---------key values begin--------------------------')
    for key in request.form:
        print key, ': ', request.form[key]
    print('-----------key values end------------------------')

    data = request.form.get('data')
    cmd = request.form.get('cmd')
    if not data or not cmd:
        return jsonify({'retcode': -1, 'errmsg': 'data or cmd not found'})

    data_json = json.loads(data)
    func_dict = {
        'saveUser': save_user,
        'removeUser': remove_user,
        'saveCluster': save_cluster,
        'removeCluster': remove_cluster,
        'addToCluster': add_to_cluster
    }

    return select_func(cmd, func_dict, data_json)


def save_user(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    nick = params.get('nick')
    is_admin = params.get('isAdmin')
    q_age = params.get('aAge')
    card = params.get('card')
    black = params.get('black')
    try:
        ClusterDB.remove_member_from_cluster_db(external_id, qq)
        ClusterDB.add_cluster_member_to_db(external_id, qq, nick, is_admin, card)
        # UserDB.upsert_user_qq_to_db(qq, nick)
        return jsonify({'retcode': 0})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def remove_user(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    try:
        ClusterDB.remove_member_from_cluster_db(external_id, qq)
        return jsonify({'retcode': 0})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def save_cluster(params):
    try:
        thread = Thread(target=save_cluster_async, args=[current_app, params])
        thread.start()
        return jsonify({"retcode": 0})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def save_cluster_async(app, params):
    # with app.app_context():
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    name = params.get('name')
    creator = str(params.get('creator'))
    members = params.get('members')

    try:
        members_copy = []
        for member in members:
            member_copy = {
                "qq": str(member.get("qq")),
                "nick": member.get("nick"),
                "is_admin": member.get("isAdmin"),
                "card": member.get("card")
            }
            members_copy.append(member_copy)
        ClusterDB.upsert_cluster_to_db(external_id, name, creator, members_copy, robot)
    except Exception, e:
        # TODO 这里需要一个单独的日志，打印到文件，同步日志
        pass


def remove_cluster(params):
    robot = params.get('robot')
    external_id = str(params.get('externalId'))
    try:

        ClusterDB.remove_robot_from_cluster(external_id, robot)
        robots = ClusterDB.robots_in_cluster(external_id)
        if len(robots) == 0:
            ClusterDB.remove_cluster_from_db(external_id)
        return jsonify({'retcode': 0})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def add_to_cluster(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    try:
        ClusterDB.upsert_cluster_add_info_to_db(external_id, robot)
        return jsonify({'retcode': 0})
    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


# =========================sync end=============================


# =========================push begin=============================
@api.route('/push', methods=['POST'])
def push():
    print('---------key values begin--------------------------')
    for key in request.form:
        print key, ': ', request.form[key]
    print('-----------key values end------------------------')

    data = request.form.get('data')
    cmd = request.form.get('cmd')
    if not data or not cmd:
        return jsonify({'code': -1, 'errmsg': 'data or cmd not found'})

    data_json = json.loads(data)
    func_dict = {
        'doPush': do_push,
    }

    return select_func(cmd, func_dict, data_json)


_PushTaskType = {
    'SendTmpMsg': 0,
    'SaveCluster': 0,
    'SaveAllClusters': 0,
    'SendClusterMsg': 0,
    'SendMsg': 0,
    'SendAttetion': 0,
    'JoinCluster': 0,
    'default': -1,
}

push_task_list = []


# task:{
#     type: 1,
#     args: 1,
# }


def do_push(params):
    # TODO do_push
    pass

# =========================push end=============================
