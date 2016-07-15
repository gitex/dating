#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson import ObjectId
from flask import jsonify, session
from flask.json import JSONEncoder
from werkzeug.exceptions import HTTPException

from Dater import config
from pytz import timezone, utc
from datetime import datetime
from time import time, mktime, gmtime
from flask.ext.babel import gettext


class JSONEncoderSecond(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return JSONEncoder.default(self, obj)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS


def make_json_error(data):
    response = jsonify(data=data)
    response.status_code = (data.code if isinstance(data, HTTPException) else 500)
    return response


def list2choice(input_list, numeric=False, end=''):
    """
    :param input_list:
    :param numeric: value is int or not:
    :param end: end is string: cm, kg:
    :return list of tuple: [(value, value), (value, value)]:
    """
    result = []

    if isinstance(input_list, (list, tuple, set)):
        if not isinstance(numeric, bool):
            numeric = False

        if numeric is False:
            for item in input_list:
                value = str(item).replace(' ', '_').lower()
                result.append((value, str(item) + end))
        elif numeric is True:
            result.extend(list(enumerate(list(input_list), start=1)))
        return result
    else:
        return []


def values_choice(choices):
    """
    Values of choices for validation "AnyOf".

    :param choices: List/tuple of tuples/lists or dict
    :return: Unique values for validation

    Example:
    Call: values_choices([(1, "2"), (3, "4")])
    Return: [1, 3]
    """
    if isinstance(choices, (tuple, list, set)):
        return list(set(values[0] for values in choices))
    elif isinstance(choices, dict):
        return list(set(choices.keys()))
    else:
        return TypeError(gettext("Choices can be iterable only"))


def age(birthday, end=gettext(" years")):
    """
    User's age on his birthday

    :param birthday: birthday is datetime type
    :param end: end is text after text
    :return: 19 years, 25 years, 40 years
    """
    if birthday and isinstance(birthday, datetime) and isinstance(end, str):
        diff = datetime.now() - birthday
        years = int(diff.days/365.2425)
        return str(years) + end
    return TypeError(gettext('Age can be only datetime type'))


def ago(data=False):
    """
    (How long ago was committed action)
    Function need for get more human-readable format from datetime type or time (float/int type)

    :param data: Seconds or datetime
    :return: 14 days ago, 15 minutes ago, now, 2 year ago
    """
    now = datetime.now()

    if type(data) is int:
        diff = now - datetime.fromtimestamp(data)
    elif isinstance(data, datetime):
        diff = now - data
    elif not time:
        diff = now - now
    else:
        raise ValueError(gettext("Argument of function can be time or datetime"))

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return gettext("just now")
        if second_diff < 60:
            return str(second_diff) + gettext(" seconds ago")
        if second_diff < 120:
            return gettext("a minute ago")
        if second_diff < 3600:
            return str(second_diff / 60) + gettext(" minutes ago")
        if second_diff < 7200:
            return gettext("an hour ago")
        if second_diff < 86400:
            return str(second_diff / 3600) + gettext(" hours ago")

    if day_diff == 1:
        return gettext("Yesterday")
    if day_diff < 7:
        return str(day_diff) + gettext(" days ago")
    if day_diff < 31:
        return str(day_diff / 7) + gettext(" weeks ago")
    if day_diff < 365:
        return str(day_diff / 30) + gettext(" months ago")
    return str(day_diff / 365) + gettext(" years ago")


def utc_to_localtime(time_seconds, today_fmt="%H:%M:%S", last_days_fmt="%d.%m.%Y"):
    """
    The conversion to the local time of the user. This function use attribute "timezone" from flask session

    :param time_seconds: time is time type
    :param today_fmt: it's format of datetime for strftime, using for today
    :param last_days_fmt: it's format of datetime for strftime, using for last_day with date
    :return: 12:47:14 or 15.02.2016 if message was sent not today
    """
    now = datetime.now()

    if isinstance(time_seconds, (float, int)):
        diff = (now - datetime.fromtimestamp(time_seconds)).days

        if diff < 0:
            return ''
        elif diff == 0:
            fmt = today_fmt
        elif diff > 0:
            fmt = last_days_fmt
        else:
            return ''

        timezone_name = session.get('timezone', None)
        if not timezone_name: timezone_name = utc
        struct_time = gmtime(time_seconds)
        date = datetime.fromtimestamp(mktime(struct_time))
        user_timezone = timezone(timezone_name)
        loc_dt = user_timezone.localize(date)
        return loc_dt.strftime(fmt)

