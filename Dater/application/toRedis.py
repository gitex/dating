#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from Dater import r, mongo, config, app
from Dater.application.models import Users

# mongo.db.timezones.remove()

def next_sid():
    """
    Sid (Second ID) for next registration of user
    """
    last_sid = Users.objects.order_by('-sid').first().sid

    if bool(last_sid):
        r.set('sid', int(last_sid) + 1)
    else:
        r.set('sid', 1)


def sids_and_logins():
    """
    Sids and logins of users for messages Tornado
    """
    if mongo.db.users.find().count() > 0:
        data = {item['sid']: item['login'] for item in list(mongo.db.users.find())}
        name_field = config.REDIS_SIDS_LOGINS  # this name used in the Tornado

        if r.exists(name_field):
            r.delete(name_field)

        r.hmset(name_field, data)

def timezones():
    """
    Timezones of users for messages' time in the Tornado
    """
    if mongo.db.timezones.find().count() > 0:
        data = {item['login']: item['timezone'] for item in list(mongo.db.timezones.find())}
        name_field = config.REDIS_TIMEZONES  # this name used in the Tornado

        if r.exists(name_field):
            r.delete(name_field)

        r.hmset(name_field, data)


def all_to_redis():
    """
    Start all function for export to Redis
    """
    next_sid()
    sids_and_logins()
    timezones()
