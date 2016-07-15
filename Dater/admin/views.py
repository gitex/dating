#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, g
from flask.ext.admin.contrib.mongoengine import ModelView
from flask_admin import expose, BaseView, AdminIndexView
from flask.ext import login
from wtforms.fields import *
from wtforms.widgets import TextArea

from Dater.admin import forms
from Dater.application import models


class MyView(AdminIndexView):
    @expose('/comlaints/')
    def complaints_list(self):
        complaints = models.ComplaintsOfUsers.objects.all()
        new_complaints = models.ComplaintsOfUsers.objects.filter(status=False)
        return self.render('/admin/complaints_list.html', 
            all_complaints=complaints, new_complaints=new_complaints)

    @expose('/list/new_users/')
    def new_users(self):
        return self.render('/admin/new_users.html')

    @expose('/posts/')
    def posts_list(self):
        return self.render('/admin/posts.html')

    @expose('/most_popular_users/')
    def most_popular_users(self):
        users = models.Users.objects.all()
        return self.render('/admin/most_popular_users.html', users=users)

        
class UserView(ModelView):
    # column_filters = ['name']

    can_create = True
    can_edit = True
    can_delete = True

    create_modal = True
    edit_modal = True

    page_size = 100

    # column_exclude_list = ['password', ]
    column_searchable_list = ['login', 'email']
    # form_columns = ['first_name', 'last_name', 'login', 'email', 'active']

class TagsView(ModelView):
    column_editable_list = ['title', 'description']


 
# --- Register Models ---
def register_models(admin):

    admin.add_view(UserView(models.Users))
    admin.add_view(ModelView(models.Messages))
    admin.add_view(ModelView(models.FileComment))
    admin.add_view(ModelView(models.Media))
    admin.add_view(TagsView(models.Tags))