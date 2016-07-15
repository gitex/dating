#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from wtforms.fields import *
from datetime import datetime
from flask.ext.wtf import Form
from wtforms.validators import Length, DataRequired

class CreatePageForm(Form):
    title = StringField('Title', [DataRequired(), Length(max=60)])
    file_name = StringField("Template Name", [DataRequired(), Length(max=230)])
    content = TextAreaField("Content", [DataRequired()])
    permalink = StringField('URL', [DataRequired(), Length(max=230)])
    status = BooleanField("Status Page", default=False)

    def validate(self):
        if not super(CreatePageForm, self).validate():
            return False
        return True