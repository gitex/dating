#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
from flask import url_for
import datetime

DEBUG = True
FLASK_LOG_FILE = 'Dater.log'

# Main settings
SECRET_KEY = '4f6d0251-7927-45e5-a211-8b8411deca'
FLASK_PORT = 5500
TORNADO_PORT = 8899

# Patches of Flask
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, "static"),)
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),)

# PyMongo
MONGO_MAIN_HOST = 'localhost'
MONGO_MAIN_PORT = 27017
MONGO_MAIN_DBNAME = "mydb"

# MongoEngine
MONGODB_SETTINGS = {'HOST': MONGO_MAIN_HOST, "PORT": MONGO_MAIN_PORT, "DB": MONGO_MAIN_DBNAME}

# Wtforms
WTF_CSRF_ENABLED = True
WTF_CSRF_CHECK_DEFAULT = True
WTF_CSRF_SECRET_KEY = '4f6d0251-7927-45e5-a211-8b8411deca22'
WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH']
WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']
WTF_CSRF_SSL_STRICT = True

# Media files
MAX_COUNT_FOLDER_FOR_PHOTO = 120  # Type is INTEGER
FOLDER_UPLOAD_MEDIAS_USERS = ['static', 'uploads', 'media']  # static/uploads/media
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
MAX_CONTENT_LENGTH = 12 * 1024 * 1024 + 1  # 12 mb
UPLOAD_FOLDER = '/uploads'

# Flask-DebugToolbar
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Redis
REDIS_CONFIG = ('localhost', 6379, 0)
REDIS_QUEUE_KEY = 'fufidur3089uujc'
# REDIS names
REDIS_SIDS_LOGINS = 'sid:login:all'
REDIS_TIMEZONES = 'timezones'

# Flask Sessions
SESSION_REDIS = REDIS_CONFIG
PERMANENT_SESSION_LIFETIME = datetime.timedelta(31)  # life of session in days

# Flask-Mail
MAIL_SERVER = 'smtp.yandex.ru'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'mail.just.in.case@yandex.ru'
MAIL_PASSWORD = 'qwerty789'
MAIL_DEFAULT_SENDER = MAIL_USERNAME

# Flask-Security : Core
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = '4f6d0251-7927-45e5-a211-8b8411deca22'
SECURITY_FLASH_MESSAGES = True
SECURITY_EMAIL_SENDER = ('Dater', MAIL_DEFAULT_SENDER)

# Flask-Security : Feature Flags
SECURITY_CONFIRMABLE = False
SECURITY_RECOVERABLE = True
SECURITY_TRACKABLE = True
SECURITY_REGISTERABLE = False

# Flask-Security: URLs and Views
SECURITY_LOGIN_URL = '/login'
SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
SECURITY_POST_LOGOUT_VIEW = '/'
SECURITY_POST_LOGIN_VIEW = '/profile'
# SECURITY_CONFIRM_URL = url_for('.token')


USERS_ROLES = {
    'user': 'Default role for main users',
    'admin': 'Administrator of site'}

DEFAULT_AVATAR = {'first_folder': '0', 'second_folder': '0', 'file_name': 'images/avatar.png'}

# OTHER SETTINGS

# YANDEX_MAPS_API_KEY = u'AI1SGlYBAAAA25AjVQIAwtvmcCDe_QDZtnNLFpYliMiltHcAAAAAAAAAAACq2tUV3baid1GH9RFQbczKbUgNtQ=='
GOOGLE_MAPS_API_KEY = 'AIzaSyDSkpIHRCAedsAJDdqbRg15qOC2B2Uh6Hs'

SITE_DOMAIN = 'http://127.0.0.1:{0}/'.format(FLASK_PORT)


# Celery
BROKER_URL = 'redis://{0}:{1}/{2}'.format(*REDIS_CONFIG)
CELERY_RESULT_BACKEND = 'redis://{0}:{1}/{2}'.format(*REDIS_CONFIG)


# Languages for Babel
LANGUAGES = {
    'ru': 'Russian',
    'en': 'English',
    # 'en-gb': 'English (Great Britain)',
    'es': 'Español'.decode('utf-8'),
    'fr': 'Français'.decode('utf-8')
}

PASS = "stixoplet345"
