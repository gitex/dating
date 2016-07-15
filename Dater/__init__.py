#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

import redis
from flask import Flask
from flask.ext.admin import Admin
from flask.ext.babel import Babel
from flask.ext.bcrypt import Bcrypt
from flask.ext.images import Images
from flask.ext.login import LoginManager
from flask.ext.mongoengine import MongoEngine
from flask.ext.pymongo import PyMongo
from flask.ext.security import Security, MongoEngineUserDatastore
from flask.ext.socketio import SocketIO
from flask_debugtoolbar import DebugToolbarExtension
from flask_googlemaps import GoogleMaps
from flask_mail import Mail
from flask_session import RedisSessionInterface
from flask_wtf.csrf import CsrfProtect
from gevent import monkey

from Dater import config, utils
from Dater.admin.views import register_models
from Dater.application.models import Users, Role
from Dater.utils import snippets

# Flask Application
app = Flask(__name__)
app.config.from_object(config)
app.json_encoder = snippets.JSONEncoderSecond
app.jinja_env.trim_blocks = True

# application logging
handler = RotatingFileHandler(app.config.get('FLASK_LOG_FILE', 'Dater.log'), maxBytes=10000, backupCount=1)
formatter = logging.Formatter(u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
handler.setLevel(logging.INFO)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

app_context = app.app_context()
app_context.push()

# CsrfProtect
csrf = CsrfProtect()
csrf.init_app(app)

# MongoDB
db = MongoEngine(app)

#PyMongo
mongo = PyMongo(app, config_prefix='MONGO_MAIN')

# Flask Mail
mail = Mail(app)

# Flask-GoogleMaps
GoogleMaps(app)

# Flask-bcrypt
flask_bcrypt = Bcrypt(app)

# Flask-Babel
babel = Babel(app=app, default_locale='en', default_timezone='UTC')

# Flask Security
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.session_protection = 'strong'

# Security Initialization
user_datastore = MongoEngineUserDatastore(db, Users, Role)
security = Security(app, user_datastore)

# Flask Admin
admin_init = Admin()
register_models(admin_init)
admin_init.init_app(app)

# Flask SocketIO
monkey.patch_all()
socketio = SocketIO(app)

# Flask Images
images = Images(app)

# Debug Toolbar
toolbar = DebugToolbarExtension(app)

# Redis
r = redis.StrictRedis(*config.REDIS_CONFIG)
app.session_interface = RedisSessionInterface(r, 'session:')

from Dater.application.toRedis import *
next_sid()
sids_and_logins()
timezones()
# all_to_redis()  # import default data to Redis


# Add views blueprints

from Dater.admin import mod as admin_mod
from Dater.view import mod as views_mod
app.register_blueprint(admin_mod)
app.register_blueprint(views_mod)


# Roles to the MongoDB
roles_mongodb = [item['name'] for item in mongo.db.role.find()]

for role in config.USERS_ROLES.keys():
    if role not in roles_mongodb:
        mongo.db.role.save({'name': role, 'description': config.USERS_ROLES[role]})

if __name__ == '__main__':
    app.run(debug=True)
