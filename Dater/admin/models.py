#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from wtforms.fields import *
from wtforms.widgets import TextArea
from datetime import datetime


class CreatedPages(Document):
    title = StringField(max_lenght=160)
    file_name = StringField(max_lenght=160, unique=True)
    content = StringField()
    date = DateTimeField(default=datetime.now)
    status = BooleanField(default=False)



