#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from flask.ext.mail import Message

from Dater import mail, app
from Dater.utils.decorators import async

mod = Blueprint('views', __name__)


@async
def send_async_email(message):
    with app.app_context():
        mail.send(message)


def send_email(subject, sender, recipients, name_template, **kwargs):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = render_template(name_template + '.txt', **kwargs)
    msg.html = render_template(name_template + '.html', **kwargs)
    send_async_email(msg)

import general, for_requests, context_processors, errors