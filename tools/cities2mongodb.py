# coding=utf-8
__author__ = 'Van'
import re
import os
import pymongo

MONGODB_HOST = os.getenv("MONGODB_HOST", '127.0.0.1')
MONGODB_PORT = os.getenv("MONGODB_PORT", 27017)
mongodb_client_db = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT).sport99


def write_city_to_db(city_id, city_letter, city_name):
    mongodb_client_db.cities.insert(
        {
            "id": city_id,
            "letter": city_letter,
            "name": city_name
        }
    )


def read_cities():
    cities_file = open('docs/cities.txt', 'r')
    lines = cities_file.readlines()

    for line in lines:
        print line
        match = re.match(r'(\d+)\s+(\S+)\s+(\d+)\s+(\S+)\s+', line)
        # print "+++", match.group(0), match.group(1), match.group(2)
        if match:
            write_city_to_db(match.group(1), match.group(4), match.group(2))


if __name__ == "__main__":
    read_cities()