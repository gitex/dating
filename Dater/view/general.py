#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import os.path
import random
import uuid
from datetime import datetime

import requests
from bson import ObjectId
from bson.son import SON
from flask import url_for, render_template, redirect, request, jsonify, send_from_directory, abort, flash
from flask.ext.googlemaps import Map
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_security.forms import LoginForm
from flask_security.utils import encrypt_password

from Dater import r, user_datastore, security, app, mongo, config, csrf
from Dater.application import forms, models
from Dater.utils.token import generate_confirmation_token, confirm_token
from Dater.view import mod, send_email


# ++++++++++ test +++++++++++++


@mod.route('/test', methods=['GET', 'POST'])
def test1():
    return jsonify(result=2)


# +++++++++++++++++++++++++++++++++


@mod.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token, expiration=86000)
        user = models.Users.objects.filter(email=email).first()
        if user.confirmed_at:
            flash('Account already confirmed. Please login.', 'success')
        else:
            user.confirmed_at = True
            user.save()
            flash('You have confirmed your account. Thanks!', 'success')
        return jsonify(result=True)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('.profile'))


@csrf.exempt
@mod.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    if request.method == "POST":
        token = generate_confirmation_token(current_user.email)
        confirm_url = url_for('.confirm_email', token=token, _external=True)
        send_email(subject="Dater: confirm registration!",
                   recipients=[current_user.email],
                   sender=config.MAIL_DEFAULT_SENDER,
                   name_template='email/email_confirmation',
                   first_name=current_user.first_name,
                   confirm_url=confirm_url)
        flash('Message send! Check your email for confirm', 'success')
    return render_template('confirm_email.html')


@csrf.exempt
@mod.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        user_datastore.create_user(
            sid=r.get('sid'),
            first_name=form.first_name.data.title().strip(),
            last_name=form.last_name.data.title().strip(),
            login=form.login.data.lower().strip(),
            email=form.email.data.lower().strip(),
            password=encrypt_password(form.password.data.strip()))
        r.incr('sid')

        user = models.Users.objects.filter(login=form.login.data.lower()).first()
        user_datastore.add_role_to_user(user=user, role=user_datastore.find_role('user'))
        login_user(user)

        r.hset(config.REDIS_SIDS_LOGINS, user.sid, user.login)  # for Tornado

        # send email for check
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('.confirm_email', token=token, _external=True)
        send_email(subject="Dater: you was registered!",
                   recipients=[user.email],
                   sender=config.MAIL_DEFAULT_SENDER,
                   name_template='email/email_confirmation',
                   first_name=user.first_name,
                   confirm_url=confirm_url)

        return redirect(url_for('.profile'))
    return render_template('register.html', form=form)


@security.login_context_processor
def login():
    return dict(form=LoginForm())


@mod.route('/logout')
def logout():
    if current_user.is_authenticated():
        logout_user()
    return redirect(url_for('security.login'))


@mod.route('/')
@mod.route('/index')
@mod.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """ Profile of current user """
    from Dater.application.lang_values import default_label

    if current_user.coordinates:
        map_lat, map_lng = current_user.coordinates[0], current_user.coordinates[1]
        google_map = Map(identifier="view-side", lat=map_lat, lng=map_lng, markers=[(map_lat, map_lng)])
    else:
        google_map = None

    return render_template('profile.html', default_label=default_label, google_map=google_map)


@login_required
@csrf.exempt
@mod.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    """ Edit profile of current user """
    if current_user.is_anonymous():
        return redirect(url_for('security.login'))

    form = forms.EditProfile(obj=current_user)

    if request.method == 'POST' and form.validate():
        # user = models.Users.objects.filter(login=current_user.login).first()
        user = mongo.db.users.find_one({'login': current_user.login})
        form.populate_obj(user)

        if bool(form.place.data):
            # API request for Google API
            place = form.place.data.replace(', ', '+')
            request_google = requests.get(
                'http://maps.googleapis.com/maps/api/geocode/json?address={0}' \
                '&sensor=false&language=en'.format(place.encode('utf-8'))).json()

            if request_google['status'] == "OK":
                location = request_google['results'][0]['geometry']['location']
                user.coordinates = [location['lat'], location['lng']]

                # user.timezone = tz.tzNameAt(float(location['lat']), float(location['lng']))
                for address in request_google['results'][0]['address_components']:
                    if 'locality' in address['types']:
                        user.city = address['long_name']
                    elif 'country' in address['types']:
                        user.country = address['long_name']
                user.save()
                return redirect(url_for('.profile'))
            else:
                user.save()
                flash('Address not found!')

        user.save()
        return redirect(url_for('.profile'))

    return render_template('edit-profile.html', form=form)


@login_required
@csrf.exempt
@mod.route('/attention')
def attention():
    """ Function of site 'Like or Not' """
    if current_user.is_anonymous():
        return redirect(url_for('security.login'))
    return render_template('dashboard.html')


@mod.route('/user/<login_of_user>')
def view_user(login_of_user):
    """ Profiles of other users """
    user = models.Users.objects.filter(login=login_of_user).first()
    if not user:
        abort(404)

    if user.coordinates:
        map_lat, map_lng = user.coordinates[0], user.coordinates[1]
        google_map = Map(identifier="view-side", lat=map_lat, lng=map_lng, markers=[(map_lat, map_lng)])
    else:
        google_map = None

    return render_template('restricted-profile.html', user=user, google_map=google_map)


@mod.route('/my_followings', methods=['GET', 'POST'])
def my_followings():
    """ List of my foolowings """
    return render_template('my_followings.html')


@mod.route('/countries')
def countries():
    return jsonify(data=list(mongo.db.users.aggregate(
        [
            {'$match': {'country': {'$gt': ''}}},
            {'$group': {
                '_id': '$country',
                'count': {'$sum': 1}}},
            {'$sort': SON([("count", -1)])}
        ])))
    

@mod.route('/last_users')
def last_users():
    last_users_list = models.Users.objects.order_by('-datetime_registration').limit(20)
    return render_template('last_users.html', last_users=last_users_list)


@mod.route('/search_via_city', methods=['GET', 'POST'])
def search_via_city():
    form = forms.SearchUsersViaCity()

    if request.method == "POST" and form.validate():
        found_users = models.Users.objects.filter(city=form.city.data)
        return render_template('found_users.html', found_users=found_users)
    return render_template('parts/search_via_city.html', form=form)


@mod.route('/search', methods=['GET', 'POST'])
def search():
    form = forms.SearchUsersViaParameters()

    if request.method == "POST" and form.validate():
        search_parameters = {}

        # Search by gender
        if any([form.man.data, form.woman.data]) and not all([form.man.data, form.woman.data]):
            search_parameters['$or'] = []
        else:
            search_parameters['$or'] = [{'gender': 'F'}, {'gender': 'M'}, {'gender': ''}]

        if form.man.data:
            search_parameters['$or'].append({'gender': 'M'})
        elif form.woman.data:
            search_parameters['$or'].append({'gender': 'F'})

        # Use min age & max age for getting datetine
        if any([form.min_age.data, form.max_age.data]):
            search_parameters['birthday'] = {}

        get_year = lambda x: datetime.now().year - int(x)
        if bool(form.min_age.data):
            min_date = datetime(get_year(form.min_age.data), 01, 01)
            search_parameters['birthday']['$lte'] = min_date
        if bool(form.max_age.data):
            max_date = datetime(get_year(form.max_age.data), 12, 31)
            search_parameters['birthday']['$gte'] = max_date

        # Use place for search coordinates by Google API
        if form.place.data:
            place = form.place.data.replace(', ', '+')
            request_google = requests.get(
                'http://maps.googleapis.com/maps/api/geocode/json?address={0}' \
                '&sensor=false&language=en'.format(place.encode('utf-8'))).json()

            if request_google['status'] == "OK":
                location = request_google['results'][0]['geometry']['location']
                searched_coordinates = [location['lat'], location['lng']]

                search_parameters['coordinates'] = \
                    {'$near' : {'$geometry': {'coordinates': searched_coordinates}}}

                # If user have changed area
                if form.area.data:
                    search_parameters['coordinates']['$near']['$maxDistance'] = int(form.area.data)*1000

        found_users = mongo.db.users.find(search_parameters)

        return render_template('found_users.html', found_users=found_users)
    return render_template('search.html', form=form)


@mod.route('/load_file', methods=['GET', 'POST'])
def load_file():
    form = forms.LoadMediaFile()

    if request.method == "POST" and form.validate():
        project_root = app.config['PROJECT_ROOT']
        images_dir = app.config['FOLDER_UPLOAD_MEDIAS_USERS']
        max_count_folder = app.config['MAX_COUNT_FOLDER_FOR_PHOTO']
        folder_medias_full_path = os.path.join(project_root, *images_dir)

        # Get names of dirs
        first_dir = str(random.randint(1, max_count_folder))
        second_dir = str(random.randint(1, max_count_folder))
        name_file = str(uuid.uuid4())

        # Sid and update count photos of user
        photo_last_sid = list(mongo.db.media.find({'user': current_user.login}, sort=[("sid", -1)]).limit(1))
        if photo_last_sid:
            photo_current_sid = int(photo_last_sid[0]['sid']) + 1
        else:
            photo_current_sid = 1

        # Save file to directory
        if form.file_data.data:
            file_extension = os.path.splitext(form.file_data.data.filename)[-1]
            directory = os.path.join(folder_medias_full_path, first_dir, second_dir)
            if not os.path.exists(directory):
                os.makedirs(directory)
            form.file_data.data.save(os.path.join(directory, name_file + file_extension))

            image_extension = ['png', 'jpg', 'jpeg', 'gif']
            video_extension = ['mp4', 'avi', 'webm']

            if any([file_extension[1:] == x for x in image_extension]):
                type_file = 'image'
            elif any([file_extension[1:] == x for x in video_extension]):
                type_file = 'video'
            else:
                type_file = file_extension

            mongo.db.media.save({
                'file_name': name_file + file_extension,
                'first_dir': first_dir,
                'second_dir': second_dir,
                'sid': photo_current_sid,
                'user': current_user.login,
                'type_file': type_file,
                'description': form.description.data,
                'load_datetime': datetime.utcnow()
            })

            return redirect(url_for('.media', user_login=current_user.login, media_sid=photo_current_sid))
    return render_template('add_photo.html', form=form)


@mod.route('/media/<user_login>/<int:media_sid>')
def media(user_login, media_sid):
    media = mongo.db.media.find_one({'user': user_login, 'sid': int(media_sid)})
    if not media:
        abort(404)

    comments = mongo.db.filecomment.find({
        'file_id': ObjectId(media.get('_id'))}, sort=[("datetime",  1)])
    likes = mongo.db.filelike.find({
        'file_id': ObjectId(media.get('_id'))}, sort=[("datetime",  1)])

    photo_user_count = mongo.db.media.find({'user': user_login}).count()

    return render_template('media.html', media=media, comments=comments, likes=likes,
                           all_photos_count=photo_user_count)


@mod.route('/media/<user_login>/')
def all_media_of_user(user_login):
    if not mongo.db.users.find_one({'login': user_login}):
        abort(404)
    medias = mongo.db.media.find({'user': user_login})
    return render_template('all_media_of_user.html', medias=medias)


@mod.route('/' + '/'.join(app.config['FOLDER_UPLOAD_MEDIAS_USERS']) + '/<first_dir>/<second_dir>/<path:filename>')
def media_path(first_dir, second_dir, filename):
    directory_list = [app.config['PROJECT_ROOT']]
    for folder in app.config['FOLDER_UPLOAD_MEDIAS_USERS']:
        directory_list.append(folder)
    directory_list.extend([first_dir, second_dir])
    directory = os.path.join(*directory_list)
    return send_from_directory(directory, filename)


@mod.route('/chat', methods=['GET', 'POST'])
def chat():
    user_sid = request.args.get("sid", None)
    tornado_port = config.TORNADO_PORT

    limit_messages_first_load = 40

    dialogues =  mongo.db.messages.aggregate([
        {'$match': {"$or":[ {"sender": current_user.login}, {"recipient": current_user.login}]}},
        {"$group": {"_id": {'thread_id': '$thread_id', 'sender': '$sender', 'recipient': '$recipient'}}},
        {"$sort": SON([("datetime", -1)])}
    ])

    filter_dialogues = []

    for dialogue in [item['_id'] for item in dialogues]:
        partner_login = dialogue['sender'] if dialogue['recipient'] == current_user.login else dialogue['recipient']
        partner_sid = dialogue['thread_id'].split('_')[0] if dialogue['thread_id'].split('_')[1] == str(current_user.sid) else dialogue['thread_id'].split('_')[1]
        filter_dialogues.append({'thread': dialogue['thread_id'], 'login': partner_login, 'sid': partner_sid})

    favorite_list = mongo.db.users.aggregate([
        {'$match': {"$or": [{"login": login for login in current_user.following}]}},
        {'$group': {"_id": {'login': '$login', 'sid': '$sid'}}}
    ])

    if user_sid:
        thread_id = "_".join([str(x) for x in sorted([int(user_sid), int(current_user.sid)])])
        recipient_login = r.hget('sid:login:all', user_sid)

        # check new messages in thr Redis
        if r.exists('new_threads:all') and "thread:" + thread_id in r.smembers('new_threads:all'):
            messages = list(r.smembers("thread:" + thread_id))
            json_messages = list(map(lambda x: json.loads(x), messages))
            for message in json_messages:
                mongo.db.messages.save(message)
            r.delete("thread:" + thread_id)
            r.srem('new_threads:all', ["thread:" + thread_id])

        messages = mongo.db.messages.find(
                {"thread_id": thread_id}, sort=[("datetime", 1)]).limit(limit_messages_first_load)

        values_to_render = dict(recipient=recipient_login, tornado_port=tornado_port, messages=messages, dialogues=filter_dialogues, favorite_list=favorite_list)
        return render_template('chat_tornado.html', **values_to_render)
    else:
        # messages = group by users
        return render_template('chat_tornado.html', tornado_port=tornado_port)