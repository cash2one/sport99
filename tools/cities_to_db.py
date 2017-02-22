# coding=utf-8
__author__ = 'Van'
import re
import os
import pymongo

MONGODB_HOST = os.getenv("MONGODB_HOST", '127.0.0.1')
MONGODB_PORT = os.getenv("MONGODB_PORT", 27017)
mongodb_client_db = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT).sport99

# 创建俱乐部需要全城市列表,格式如下
# [
#     {
#         "initial": "B", # 首字母
#         "cities": {
#             "id": 10900,
#             "word": "Beijing",
#             "name": "北京市"
#         }
#     },
#     {
#         "initial": "C",
#         "cities": {
#
#         }
#     },...
# ]


def write_city_to_db(initial, city_id, city_letter, city_name):
    """
    将一个城市插入
    :param initial:
    :param city_id:
    :param city_letter:
    :param city_name:
    :return: 插入结果
    """
    return mongodb_client_db.cities.update(
        {
            "initial": initial
        },
        {
            "$set": {
                "initial": initial
            },
            "$addToSet": {
                "cities": {
                    "id": city_id,
                    "word": city_letter,
                    "name": city_name
                }
            }
        },
        True
    )


def read_cities():
    cities_file = open('docs/cities.txt', 'r')
    lines = cities_file.readlines()

    for line in lines:
        print line
        match = re.match(r'(\d+)\s+(\S+)\s+(\d+)\s+(\S+)\s+', line)
        # print "+++", match.group(0), match.group(1), match.group(2)
        if match:
            # 获取首字母
            word = match.group(4)
            initial = word[0: 1]
            # 入库
            write_city_to_db(initial, match.group(1), word, match.group(2))


if __name__ == "__main__":
    read_cities()