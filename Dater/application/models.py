#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from flask.ext.security import UserMixin, RoleMixin
from mongoengine import *
from Dater.utils.snippets import age


class Role(Document, RoleMixin):
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)

    def __unicode__(self):
        return self.name


class Users(Document, UserMixin):
    # Registration and authorization
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    login = StringField(max_length=50, unique=True)
    email = StringField(max_length=120, unique=True)
    password = StringField(max_length=80)

    # User values
    sid = IntField(unique=True)
    datetime_registration = DateTimeField(default=datetime.utcnow)
    roles = ListField(ReferenceField(Role), default=[])
    active = BooleanField(default=False)
    confirmed_at = BooleanField(default=False)
    alert_new_message = StringField(default='0')
    alert_new_visites = StringField(default='0')
    alert_special_offer = StringField(default='0')
    has_photo = BooleanField(default=False)
    has_video = BooleanField(default=False)
    online = BooleanField(default=False)
    fake = BooleanField(default=False)
    count_photo = IntField(default=0)

    current_login_at = DateTimeField()
    last_login_at = DateTimeField()
    login_count = IntField()
    current_login_ip = StringField(max_length=60)
    last_login_ip = StringField(max_length=60)

    # User data
    gender = StringField(max_length=10)
    birthday = DateTimeField()
    description = StringField(max_length=160)
    marital_status = StringField(max_length=30)

    phone_code = StringField(max_length=5)
    phone_number = StringField(max_length=40)

    avatar = DictField()
  
    # User body
    growth = StringField(max_length=10)
    waist = StringField(max_length=10)
    weight = StringField(max_length=10)
    body = StringField(max_length=50)
    food = StringField(max_length=50) 
    eyes = StringField(max_length=50)
    origin = StringField(max_length=100)
    drink = StringField(max_length=120)
    smoking = StringField(max_length=120)
    hairs = StringField(max_length=100)

    gay = BooleanField(default=False)
    presentation = StringField(max_length=200, default=None)
    presentation_research = StringField(max_length=200, default=None)
    
    # GEO-data
    timezone = StringField(max_length=40)
    country = StringField(max_length=30)
    city = StringField(max_length=20)
    coordinates = GeoPointField()

    # My lists
    goals = ListField(StringField())
    languages = ListField(StringField(max_length=50))
    films = ListField(StringField(max_length=50))
    animals = ListField(StringField(max_length=50))
    feature = ListField(StringField(max_length=50))
    music = ListField(StringField(max_length=50))
    personality = ListField(StringField(max_length=50))

    # Follows
    followers = ListField(StringField(max_length=30))
    following = ListField(StringField())

    # Like or Not
    users_like = ListField(StringField())
    i_dont_like = ListField(StringField()) # delete

    # Quick search
    search_gender = StringField(max_length=1)
    search_age_min = StringField(max_length=2)
    search_age_max = StringField(max_length=2)
    search_country = StringField(max_length=50)
    search_department = StringField(max_length=50)
    search_online = BooleanField(default=False)
    search_photo = BooleanField(default=False)

    purpose_meeting = StringField(max_length=20, default=None)

    age = property(age(birthday))

    # @
    # def coordinates(self):
    #     if self.country and self.zipcode:
    #         data = r.hgetall('ZIP:' + self.country + ':' + self.zipcode)
    #         return {'longitude': data['longitude'], 'latitude': data['latitude']}
    #     return None

    # @property
    # def profile_complete(self):
    #     return True

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __unicode__(self):
        return self.login


class Messages(Document):
    """ Users' messages from Redis """
    thread_id = StringField()
    sender = StringField(max_length=50, required=True)
    recipient = StringField(max_length=50, required=True)
    body = StringField(required=True)
    datetime = DateTimeField(default=datetime.utcnow)


class Media(Document):
    file_name = StringField()
    first_dir = StringField()
    second_dir = StringField()
    type_file = StringField()

    # second ID need for link
    sid = IntField()

    # Information about file
    user = StringField()
    load_datetime = DateTimeField(default=datetime.utcnow)
    description = StringField(max_length=160)
    # tags = ListField(ObjectIdField())

    def get_likes_count(self):
        return FileLike.objects.filter(file=self.id).count()

    def get_comments_count(self):
        return FileComment.objects.filter(file=self.id).count()

    def __unicode__(self):
        return self.file_name



class Tags(Document):
    """ Tags of photo and video """
    title = StringField(max_length=100)
    description = StringField(max_length=250)
    date_created = DateTimeField(default=datetime.utcnow)

    def __unicode__(self):
        return self.title


class FileLike(Document):
    """ Model for likes of photo and video"""

    file_id = ObjectIdField()
    datetime = DateTimeField(default=datetime.utcnow)
    user = StringField()

    def __unicode__(self):
        return self.user


class FileComment(Document):
    """ Model for comments of photo and video"""

    file_id = ObjectIdField()
    datetime = DateTimeField(default=datetime.utcnow)
    user = StringField()
    text = StringField()

    @property
    def user_avatar(self):
        return Users.objects.filter(login=self.user).first().avatar


class LikeUser(Document):
    """ Model for function of site "Like or not" """

    like_user = ObjectIdField()
    who_like = ObjectIdField()
    datetime = DateTimeField(default=datetime.utcnow)
    viewed = BooleanField(default=False)


class DoNotShow(Document):
    """ Model to temporarily disable the user of another user ("Like or not") """

    main_user = StringField()
    blocked_user = StringField()
    block_date = DateTimeField()
    count_block = IntField(default=0)


class Timezones(Document):
    login = StringField()
    timezone = StringField()