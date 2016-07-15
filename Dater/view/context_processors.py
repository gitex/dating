#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import session, request, g
from flask.ext.login import current_user

from Dater import app, babel
from Dater import config
from Dater.utils.snippets import ago, utc_to_localtime, age

from pytz import timezone, utc
from datetime import datetime
from time import time, mktime, gmtime


@app.context_processor
def get_user():
    return dict(current_user=current_user)


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
    g.locale = get_locale()
    session['locale'] = get_locale()


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(config.LANGUAGES.keys())


@app.context_processor
def get_age_from_birthday():
    def get_age(birthday, endswith):
        return age(birthday, endswith)
    return dict(age=get_age)


@app.context_processor
def get_time_from_seconds():
    def to_localtime(time_seconds):
        return utc_to_localtime(time_seconds=time_seconds)
    return dict(utc_to_localtime=utc_to_localtime)


@app.context_processor
def time_ago():
    def datetime_to_time_ago(data):
        return ago(data)
    return dict(ago=datetime_to_time_ago)

