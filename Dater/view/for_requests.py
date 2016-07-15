#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
from datetime import datetime

from bson import ObjectId
from flask import request, jsonify, session
from flask.ext.login import current_user, _get_user, login_required

from Dater import r, mongo, csrf
from Dater.application import models
from Dater.config import FOLDER_UPLOAD_MEDIAS_USERS, PROJECT_ROOT
from Dater.utils.snippets import age
from . import mod


@login_required
@csrf.exempt
@mod.route('/follow/<user_login>', methods=['POST'])
def change_follow(user_login):
    if current_user.is_authenticated():
        user = models.Users.objects.filter(login=current_user.login).first()
        if user_login in list(user.following):
            user.following.remove(user_login)
            user.save()
            return jsonify(follow=False, result="OK")
        else:
            user.following.append(user_login)
            user.save()
            return jsonify(follow=True, result="OK")
    return jsonify(follow=None, result="Error")


@login_required
@csrf.exempt
@mod.route('/like/<user_login>', methods=['POST'])
def like_user(user_login):
    if current_user.is_anonymous():
        return jsonify(result="None", status="User not authorized")

    user = models.Users.objects(login=user_login).first()
    if user_login not in user.users_like:
        user.users_like.append(user_login)
    user.save()

    return jsonify(result="OK")


@login_required
@csrf.exempt
@mod.route('/get', methods=['POST'])
def get_data():
    event = request.json['event']
    # print request.headers

    if event == 'random_user':
        # Exclude me, my like users, users that don't show and my subscriptions
        if current_user.is_authenticated() and current_user.is_active():
            exclude_list = [current_user.login]
            exclude_list.extend(current_user.users_like)
            exclude_list.extend(current_user.following)

            fields = ['sid', 'login', 'birthday', 'description']

            fields_from_base = {field: '$' + field for field in fields}
            all_users = mongo.db.users.aggregate([
                {"$group": {"_id": fields_from_base}}
            ])

            clear_users = [user[u'_id'] for user in all_users['result'] if user[u'_id'][u'login'] not in exclude_list]
            random_user = random.choice(clear_users)
            random_user['age'] = age(random_user['birthday'])
            return jsonify(result='OK', user=random_user)
        else:
            return jsonify(result='None', data="User is not authenticated", event=event, user=str(_get_user()))
    return jsonify(status="No response", event=event)


@login_required
@csrf.exempt
@mod.route('/set', methods=['POST'])
def set_data():
    event = request.json['event']


    # Likes
    if event == 'like':
        current_status = bool(mongo.db.filelike.find_one({
            'file_id': ObjectId(request.json['file_id']),
            'user': current_user.login
            }))

        if current_status is not True:
            mongo.db.filelike.save({
                'file_id': ObjectId(request.json['file_id']),
                'datetime': datetime.utcnow(),
                'user': current_user.login
                })
            return jsonify(data=True, info='Like added')
        else:
            mongo.db.filelike.remove({
                'file_id': ObjectId(request.json['file_id']),
                'user': current_user.login
                })
            return jsonify(data=False, info='Like deleted')

    # Timezone to session
    elif event == 'timezone':
        timezone = request.json['timezone']

        # To Flask Session
        session['timezone'] = timezone

        if current_user.is_authenticated():
            # To Redis for Tornado
            if r.hget('timezones', current_user.sid):
                r.hdel('timezones', current_user.sid)
            r.hset('timezones', current_user.sid, timezone)

            # To MongoDB for saving
            if mongo.db.timezones.find_one({'login': current_user.login}):
                mongo.db.timezones.update({'login': current_user.login}, {'timezone': timezone, 'login': current_user.login}, True)
            else:
                mongo.db.timezones.save({'login': current_user.login, 'timezone': timezone})
        return jsonify(message='Timezone added', result="OK", timezone=timezone)
    
    # Photo to avatar
    elif event == 'avatar':
        current_photo = mongo.db.media.find_one({
            'user': current_user.login, 
            'sid': request.json['sid']})
        mongo.db.users.update(
            {'login': current_user.login}, 
            {'$set': {'avatar': {
                'first_dir': current_photo['first_dir'],
                'second_dir': current_photo['second_dir'],
                'file_name': current_photo['file_name']}
            }})
        return jsonify(data=True)

    # New comment
    elif event == 'comment':
        if request.json.get('file_id', None) and request.json.get('text', None):

            mongo.db.filecomment.insert({
                'file_id': ObjectId(request.json['file_id']),
                'user': current_user.login,
                'text': request.json['text'],
                'datetime': datetime.utcnow()
                })
            return jsonify(data=True)
        return jsonify(data=False)

    return jsonify(data="No response", event=event)


@login_required
@csrf.exempt
@mod.route('/delete', methods=['POST'])
def del_data():
    event = request.json['event']

    if event == 'photo':
        file_id = ObjectId(request.json['file_id'])
        media = mongo.db.media.find_one({'_id': file_id})

        if media['user'] == current_user.login:
            media_path = [PROJECT_ROOT]
            media_path.extend(FOLDER_UPLOAD_MEDIAS_USERS)
            media_path.extend([media['first_dir'], media['second_dir']])

            folder_media = os.path.join(*media_path)

            media_path.append(media['file_name'])
            media_path = os.path.join(*media_path)

            # remove file
            if os.path.isfile(media_path):
                os.remove(media_path)

            # if folder is empty
            if os.path.isdir(folder_media):
                os.rmdir(folder_media)

            # delete all comments of this media
            mongo.db.filecomment.remove({'file_id': file_id})

            # delete all likes of this media
            mongo.db.filelike.remove({'file_id': file_id})

            # delete media
            mongo.db.media.remove({'_id': file_id})

            return jsonify(data="File was deleted", result=True)
    return jsonify(data="No response", result=False)


@csrf.exempt
@mod.route('/report', methods=['POST'])
def report():
    page_source = request.json['page']
    user_source = current_user.login
    data_source = request.json.get('data_source', '')
    user_suspect = request.json['suspect']
    type_report = request.json['type']
    message_about_suspect = request.json['text']

    # All types report:
    # 1) Comment
    # 2) Media
    # 3) profile
    # 4) Avatar

    if any([type_report == x for x in ['user', 'media', 'comment']]):
        last_reports = mongo.db.reportsforusers.find({
            'user_source': user_source, 'status': False}).count()
        if last_reports < 10:
            mongo.db.reportsforusers.save({
                'user_source': user_source,
                'suspect': user_suspect,
                'page_source': page_source,
                'report_type': type_report,
                'description': message_about_suspect,
                'date': datetime.utcnow(),
                'data_source': data_source,
                'status': False
            })
            return jsonify(result=True, type=type_report)
        return jsonify(result=False, type=type_report)

    return jsonify(data=False)

