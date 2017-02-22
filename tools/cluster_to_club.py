# coding: utf-8
__author__ = 'jiangzhuang'

import pymongo
import time
import random


mongodb_client_db = pymongo.MongoClient('123.206.25.118', 27017).sport99
def all_club():
    return mongodb_client_db.clubs.find({"creator_id":{"$gt":0}},{"id":1,"creator_id":1})

def user_by_id(user_id):
    return mongodb_client_db.users.find_one({"id": user_id})

def cluster_by_qq(qq):
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
            {"external_id": 1, "name": 1,"members":1, "_id": 0}
        )
    return clusters

def add_follow_user_to_club_db(club_id, user_id, join_time,nickname,head_img_url):
        follow_member = mongodb_client_db.clubs.find_one({"id":club_id,"follow_members.id":user_id,"follow_members.role":3})
        if follow_member:
            print "the user has joined : user_id :",user_id," , club_id:",club_id
        else:
            mongodb_client_db.clubs.update(
                {"id": club_id},
                {
                    "$push": {"follow_members": {"id": user_id, "join_time": join_time, "role": 3,"nickname":nickname,"head_img_url":head_img_url}},
                    "$inc": {"follow_members_count": 1}
                }
            )
            user_follow = mongodb_client_db.users.find_one({"id":user_id,"follow_clubs.id":club_id})
            if user_follow:
                print "the user follow club is exist ,user_id ",user_id,"follow_clubs_id:",club_id
            else:
                mongodb_client_db.users.update(
                    {"id": user_id},
                    {
                        "$addToSet": {"follow_clubs": {"id": club_id}},
                        "$inc": {"follow_clubs_count": 1}
                    }
                )

def user_by_qq(qq):
        return mongodb_client_db.users.find_one({"qq": qq, "status": 0})

def init():
    try:
        mongodb_client_db.clubs.update(
            {"id":{"$gt":0}},
            {
                "$set":{
                  "follow_members_count":0,
                  "follow_members":[]
                }
            },
            False,True)
        mongodb_client_db.users.update(
            {"id":{"$gt":0}},
            {
                "$set":{
                    "follow_clubs_count":0,
                    "follow_clubs":[]
                }
            },
            False,True)
    except Exception,e:
        print e.message


def sync_member_cluster_to_club():
    qq_arr = ["2644712295","2138409857","2295458282"]
    images_arr = ['/static/app/img/headimgs/user1.png','/static/app/img/headimgs/user2.png','/static/app/img/headimgs/user3.png','/static/app/img/headimgs/user4.png','/static/app/img/headimgs/user5.png']

    join_time = int(time.time())
    print "join_time :",join_time
    try:
        # 1、查询所有俱乐部
        club_arr = all_club()
        for club in club_arr:
            # if club.get("id") == 49:
                print "----------------------"
                if club and club.get("creator_id"):
                    # 2、通过俱乐部creator_id 查询用户 ，得到qq
                    club_id = club.get("id")
                    creator_id = club.get("creator_id")
                    print " club : ",club_id ," , creator :",creator_id
                    creator = user_by_id(creator_id)
                    if creator and creator.get("qq"):
                    # 3、通过qq查询所有群，获得群列表
                       qq = creator.get("qq")
                       if qq in qq_arr:
                           print " I am a robot :",qq
                       else:
                           cluster_arr = cluster_by_qq(qq)
                           for cluster in cluster_arr:
                               members = cluster.get("members")
                               for member in members:

                                    join_user = user_by_qq(member.get("qq"))
                                    if join_user and join_user.get("id"):
                                        if join_user.get("id")== creator_id:
                                            print "creator_id = join_user_id :" ,creator_id
                                        else:
                                            # 4、将群成员加入俱乐部follow_members
                                            nickname = ""
                                            if "nickname" in join_user and not nickname:
                                                nickname = join_user["nickname"]

                                            if "wechat" in join_user and not nickname:
                                                nickname = join_user["wechat"]["nickname"]
                                            head_img_url = ""
                                            if "head_img_url" in join_user and not head_img_url:
                                                head_img_url = join_user["head_img_url"]
                                            if "wechat" in join_user and not head_img_url:
                                                head_img_url = join_user["wechat"].get("headimgurl")
                                            if not head_img_url:
                                                index = random.randint(0, 4)
                                                head_img_url = images_arr[index]
                                            add_follow_user_to_club_db(club_id,join_user.get("id"),join_time,nickname,head_img_url)
    except Exception,e:
        print e.message

# init()
sync_member_cluster_to_club()

