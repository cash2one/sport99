# coding: utf-8
__author__ = 'jiangzhuang'

import pymongo
import random
import time
import datetime

mongodb_client_db = pymongo.MongoClient('127.0.0.1', 27017).sport99

# 170000 开始
user_id = 170007
# 60  ---  150
club_id = 67
# 4000 --- 5000
event_id = 4009

nickname = "版纳"
mobile = "13651271143"

club_name = "版纳"
fee = 18

members_count_limit = 12

event_name = "丰台纪家庙夫子羽毛球馆"

weekday = [0,2,4]

venue_title = "丰台纪家庙夫子羽毛球馆"
venue_address = "10号线纪家庙地铁站D口"
introduce = "10号线纪家庙地铁站D口，提前电话联系13651271143"

start_time = "2016-4-19 11:00:01"
end_time = "2016-4-19 13:00:01"

# 1 创建用户
def create_user():

    images_arr = ['/static/app/img/headimgs/user1.png','/static/app/img/headimgs/user2.png','/static/app/img/headimgs/user3.png','/static/app/img/headimgs/user4.png','/static/app/img/headimgs/user5.png']



    openid = "xuniyonghu_"+str(user_id)
    index = random.randint(0, 4)
    head_img_url = images_arr[index]


    user = {
        "events": [],
        "events_count": 0,
        "follow_clubs": [],
        "follow_clubs_count": 0,
        "head_img_url": head_img_url,
        "height": "123",
        "id": user_id,
        "interest": "123",
        "clubs" : [{
              "role" : 0,
              "id" : club_id,
              "join_time" : int(time.time())
            }],
        "clubs_count" : 1,
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

    mongodb_client_db.users.insert(user)


# 2 创建俱乐部
def create_club():
     logo_arr = ["/static/app/img/headimgs/club1.png","/static/app/img/headimgs/club1.png","/static/app/img/headimgs/club3.png"]

     index = random.randint(0, 2)
     logo_url = logo_arr[index]

     club = {
          "bg_img_url" : "/static/app/img/bgimgs/club/P5.png",
          "bind_qq" : "",
          "create_time" : int(time.time()),
          "creator_id" : user_id,
          "events_count" : 0,
          "follow_members" : [],
          "follow_members_count" : 0,
          "id" : club_id,
          "logo_url" : logo_url,
          "members" : [{
              "role" : 0,
              "id" : user_id,
              "join_time" : int(time.time())
            }],
          "members_count" : 1,
          "name" : club_name,
          "status" : 0,
          "tags" : "羽毛球"
        }

     mongodb_client_db.clubs.insert(club)


# 3 创建周期活动
def create_template():



    event = {
              "category" : "羽毛球",
              "club_id" : club_id,
              "clusters" : [],
              "create_time" : int(time.time()),
              "creator_id" : user_id,
              "end_time" : int(time.mktime(time.strptime(end_time,"%Y-%m-%d %H:%M:%S"))),
              "fee" : fee,
              "id" : event_id,
              "is_aa" : "false",
              "is_cycle" : "true",
              "members" : [],
              "members_count" : 0,
              "introduce" : introduce,
              "members_count_limit" : members_count_limit,
              "mobile" : mobile,
              "name" : event_name,
              "place_num" : "具体场地号，到场看",
              "signs" : { },
              "start_time" : int(time.mktime(time.strptime(start_time,"%Y-%m-%d %H:%M:%S"))),
              "status" : 0,
              "type" : "template",
              "venue" : {
                "coordinate" : [0, 0],
                "phone" : "",
                "title" : venue_title ,
                "city" : "北京市",
                "address" : venue_address
              },
              "weekday" : 1,
              "days" : weekday
            }
    mongodb_client_db.events.insert(event)



# 4 自动报名







create_user()
create_club()
create_template()