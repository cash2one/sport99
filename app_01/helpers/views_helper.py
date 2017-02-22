# coding: utf-8
__author__ = 'jiangzhuang'
from app_01.mongo import EventDB, UserDB, mongodb_client_db
import datetime
import time
from copy import deepcopy
from ..mredis import RedisClient
from ..utils import get_event_sign
import random
import logging


def create_event():
    logging.basicConfig()
    print "scheduler  create_event start ----------------"
    today = datetime.datetime.now()
    today_add_6 = today + datetime.timedelta(days=6)
    week = today_add_6.weekday()
    template_arr = EventDB.event_template_from_db(week)
    if template_arr:
        for template in template_arr:
            try:
                template_id = template.pop("id", "")
                if template_id:
                    template_copy = deepcopy(template)
                    # 模板id
                    template_copy.update({"template_id": template_id})
                    template_copy.update({"type": "event"})
                    template_copy.update({"create_time": int(time.time())})
                    template_copy.pop("_id", "")
                    st_stamp = int(template.get("start_time"))
                    et_stamp = int(template.get("end_time"))
                    st = datetime.datetime.fromtimestamp(st_stamp)
                    et = datetime.datetime.fromtimestamp(et_stamp)
                    st_hm_str = str(st.hour) + ":" + str(st.minute)
                    et_hm_str = str(et.hour) + ":" + str(et.minute)

                    day_str = str(today_add_6.year) + "-" + str(today_add_6.month) + "-" + str(today_add_6.day)
                    start_time_str = day_str + " " + st_hm_str
                    end_time_str = day_str + " " + et_hm_str
                    # 开始时间 结束时间
                    start_time = int(time.mktime(time.strptime(start_time_str, '%Y-%m-%d %H:%M')))
                    end_time = int(time.mktime(time.strptime(end_time_str, '%Y-%m-%d %H:%M')))
                    weekday = datetime.datetime.fromtimestamp(start_time).weekday()
                    template_copy.update({"weekday": weekday})
                    template_copy.update({"start_time": start_time})
                    template_copy.update({"end_time": end_time})

                    # 活动标示
                    clusters = template.get("clusters", [])
                    signs = {}
                    if clusters.__len__() > 0:
                        for cluster in clusters:
                            sign_arr = EventDB.sign_from_event_db(cluster, start_time)
                            sign = get_event_sign(sign_arr)
                            signs.update({cluster: sign})

                    template_copy.update({"members": []})
                    template_copy.update({"members_count": 0})

                    template_copy.update({"clusters": clusters})
                    template_copy.update({"signs": signs})
                    # 活动id
                    id = RedisClient.new_event_id()
                    template_copy.update({"id": id})
                    print "create event by templet, templet_id = " + str(template_id) + " ,event id = " + str(id)
                    EventDB.add_event_to_db(template_copy)
                    # UserDB.add_event_to_user_db(id,template_copy.get("creator_id"))

            except Exception, e:
                print "create event auto ", e.message


def auto_sign():
    logging.basicConfig()
    print "scheduler  auto_sign start ----------------"
    # 提前6天报名
    template_id_arr = [4000, 4001, 4002, 4003, 4004, 4005, 4006, 4007, 4008, 4009]

    external_id = "121141483"
    cluster = mongodb_client_db.clusters.find_one({"external_id": external_id})
    members = cluster.get("members")
    total_count = len(members)

    # 1、查询模板id在列表中的活动
    for template_id in template_id_arr:
        d = datetime.datetime.now()
        weekday = d.weekday()
        event = mongodb_client_db.events.find_one({
            "weekday": weekday,
            "status": 0,
            "type": "event",
            "template_id": template_id,
            "start_time": {
                "gt": int(time.time()) + 3600 * 24 * 5
            }
        })
        c_event_id = event.get("id")
        print "c_event_id :" + str(c_event_id)
        # 2、判断报名人数
        members_count = event.get("members_count", 0)
        members_count_limit = event.get("members_count_limit", 0)
        print "members_count :" + str(members_count)
        print "members_count_limit :" + str(members_count_limit)
        if members_count >= members_count_limit:
            break
        elif members_count < members_count_limit / 2:
            # 3、从群组中随机获取昵称报名
            for i in range(members_count_limit / 2):
                index = random.randint(0, total_count - 1)
                m = members[index]
                mongodb_client_db.events.update(
                    {"id": c_event_id},
                    {
                        "$addToSet": {
                            "members": {
                                "user_temp": m.get("nick"),
                                "channel": "增",
                                "help_qq": "",
                                "join_count": 1,
                                "join_time": int(time.time())
                            }
                        },
                        "$inc": {"members_count": 1}
                    }
                )
        else:
            break


def test_scheduler():
    logging.basicConfig()
    print "test_scheduler:" + str(int(time.time()))
