#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from random import choice

from faker import Factory
from pymongo import MongoClient
from redis import StrictRedis

r = StrictRedis('localhost', 6379, 0)
need_users = 50

fake = Factory.create('fr_FR')

client = MongoClient('localhost', 27017)
database = client.mydb.users

test_cities = [
    {
        'city': 'Astana', 
        'country': 'Kazakhstan', 
        'coordinates': [51.16052269999999, 71.4703558]
    },
    ]

items_in_base = [item['login'] for item in database.find() if item['login'].startswith('fake_')]
last_fake_login = int(max(list(items_in_base)).split('#')[1]) if bool(items_in_base) else 1

logins_used = [None]
emails_used = [None]

for x in range(need_users):
    gender = choice(["F", "M"])
    random_city = choice(test_cities)

    email = None
    login = None

    while email in emails_used:
        email = fake.free_email()

    while login in logins_used:
        last_fake_login += 1
        login = 'fake_' + str(last_fake_login)

    data = {
        'birthday': datetime(choice(range(1960, 1995)), choice(range(1, 13)), choice(range(1, 28))),
        'first_name': fake.first_name_male() if gender is "M" else fake.first_name_female(),
        'last_name': fake.last_name_male() if gender is "M" else fake.last_name_female(),
        'gender': gender,
        'password': fake.password(length=10),
        'email': email,
        'description': fake.text(max_nb_chars=150),
        'sid': r.get('sid'),
        'fake': True,
        'coordinates': random_city['coordinates'],
        'login': login,
        'city': random_city['city'],
        'country': random_city['country']
        }
    database.save(data)
    r.incr('sid')