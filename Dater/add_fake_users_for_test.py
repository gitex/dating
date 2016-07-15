#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from pymongo import Connection
from faker import Factory
import redis
from __init__ import user_datastore
from application import models
import random

fake = Factory.create('fr_FR')
r = redis.StrictRedis('localhost', 6379, 0)

client = Connection('localhost', 27017)
base = client['mydb']
database = base['users']
# database.remove()
emails = [item['email'] for item in database.find()]
logins = [item['login'] for item in database.find()]

def create_test_users():
    c = 0
    for _ in range(1, 40):

        data = {
            'sid': r.get('sid'),
            'first_name': fake.first_name_female(),
            'last_name': fake.last_name_female(),
            'login': 'Fake_{0}'.format(r.get('sid')),
            'email': fake.free_email(),
            'password': fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True),
            'zipcode': fake.postcode(),
            'country': fake.country_code(),
            'active': True,
            'confirmed_at': True,
            'fake': True,
            'gender': 'F',
            'coordinates': [float(fake.latitude()), float(fake.longitude())],
            'birthday': fake.date_time(),
            'growth': str(random.choice(range(120, 190)))

        }

        if data['email'] not in emails and data['login'] not in logins:
            emails.append(data['email'])
            logins.append(data['login'])
            user_datastore.create_user(**data)
            c += 1

        r.incr('sid')
    return c

print create_test_users()