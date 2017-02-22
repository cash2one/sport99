# coding: utf-8
__author__ = 'zhaojm'

import os
import pymongo
import redis

MONGODB_HOST = os.getenv("MONGODB_HOST", '127.0.0.1')
MONGODB_PORT = os.getenv("MONGODB_PORT", 27017)
mongodb_client_db = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT).sport99

REDIS_HOST = os.getenv("REDIS_HOST", '127.0.0.1')
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=0)


class RedisClient(object):
    @staticmethod
    def set_user_id(user_id):
        redis_client.set("user_id", user_id)

    @staticmethod
    def set_event_id(event_id):
        redis_client.set("event_id", event_id)

    @staticmethod
    def set_club_id(club_id):
        redis_client.set("club_id", club_id)


class MongoClient(object):
    @staticmethod
    def user_id_max_from_db():
        res = mongodb_client_db.users.find({"id": {"$gt": 0}}, {"id": 1, "_id": 0}).sort("id", -1).limit(1)
        return int(res[0]["id"])

    @staticmethod
    def club_id_max_from_db():
        res = mongodb_client_db.clubs.find({"id": {"$gt": 0}}, {"id": 1, "_id": 0}).sort("id", -1).limit(1)
        return int(res[0]["id"])

    @staticmethod
    def event_id_max_from_db():
        res = mongodb_client_db.events.find({"id": {"$gt": 0}}, {"id": 1, "_id": 0}).sort("id", -1).limit(1)
        return int(res[0]["id"])


class InitRedis(object):
    @staticmethod
    def init_event_id():
        max_event_id = MongoClient.event_id_max_from_db()
        RedisClient.set_event_id(max_event_id + 1)
        pass

    @staticmethod
    def init_user_id():
        max_user_id = MongoClient.user_id_max_from_db()
        RedisClient.set_user_id(max_user_id + 1)
        pass

    @staticmethod
    def init_club_id():
        max_club_id = MongoClient.club_id_max_from_db()
        RedisClient.set_club_id(max_club_id + 1)
        pass


def main():
    InitRedis.init_user_id()
    InitRedis.init_event_id()
    InitRedis.init_club_id()

if __name__ == "__main__":
    main()
    pass
