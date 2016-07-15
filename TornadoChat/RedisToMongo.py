#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import redis
import pymongo
from Dater import config

r = redis.StrictRedis()

mongo = pymongo.MongoClient(config.MONGO_MAIN_HOST, config.MONGO_MAIN_PORT)


def clear_all_keys():
    all_keys_for_delete = ['new_threads:all']
    all_keys_for_delete.extend(r.keys('thread:*'))
    r.delete(*all_keys_for_delete)
    return True

if bool(r.smembers("new_threads:all")):
    for thread in r.smembers('new_threads:all'):
        messages = list(r.smembers(thread))
        json_messages = list(map(lambda x: json.loads(x), messages))
        for message in json_messages:
            mongo.mydb.messages.insert(message)

        # Remove values
        r.delete(thread)
        r.srem('new_threads:all', [thread])
    clear_all_keys()

# Check result
print "Redis: ", r.smembers('thread:*'), r.smembers('new_threads:all')
print "Mongo: ", list(mongo.mydb.messages.find())