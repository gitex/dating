#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import json

one_degree = 111.11

client = MongoClient('localhost', 27017)
database = client.mydb.around_people

# for i in range(1, 11):
#     database.save({'sid': i, 'loc': [i*3.7577, i*-12.4376]})

items = [item for item in database.find({"loc": {"$within": {"$center": [[11, -38], 20/one_degree]}}})]

items_clear = []
for x in items:
    del x['_id']
    items_clear.append(x)

print json.dumps(items_clear, sort_keys=True, indent=4)