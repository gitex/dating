#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime

import tornado.gen
import tornado.web
import tornadoredis
from pytz import utc
from sockjs.tornado import SockJSRouter, SockJSConnection, proto
from tornado import web, ioloop

from Dater import config
from Dater.utils.snippets import utc_to_localtime


def tornadoredis_client():
    client = tornadoredis.Client(*config.REDIS_CONFIG)
    client.connect()
    return client


class PlansqTornadoChat(SockJSConnection):
    users = dict()
    timezones = dict()
    client = tornadoredis_client()

    def on_open(self, info):
        self.authenticated = False
        self.sids_logins = dict()

    @tornado.gen.engine
    def on_message(self, msg):
        data = proto.json_decode(msg)

        if data['type'] == 'auth':
            if bool(data.get('sid', None)):
                try:
                    int(data['sid'])  # check that sid is number, not word
                    self.user_sid = data['sid']
                    self.user_login = yield tornado.gen.Task(self.client.hget, 'sid:login:all', self.user_sid)
                    self.users[self.user_sid] = self
                    self.user_timezone = yield tornado.gen.Task(self.client.hget, 'timezones', self.user_sid)
                    self.timezones[self.user_sid] = self.user_timezone
                    self.authenticated = True
                    self.send(proto.json_encode({"body": "You was authorized", 'type': 'alert'}))
                except Exception, e:
                    logging.info("bad user's sid: " + str(data['sid']))
            else:
                self.send(proto.json_encode({"body": "You did not authorize", 'type': 'alert'}))
                self.close()

        elif data['type'] == 'message':
            if all([x in data for x in ['type', 'recipient', 'body', 'sender']]) \
                    and data['sender'] == self.user_sid:
                recipient = data['recipient']

                try:
                    int(recipient)  # check that sid is number, not word
                except Exception, e:
                    logging.info('sid of recipient is not number')
                    return

                self.thread = "_".join([str(x) for x in sorted([int(self.user_sid), int(recipient)])])

                if recipient not in self.sids_logins:
                    recipient_login = yield tornado.gen.Task(self.client.hget, 'sid:login:all', recipient)
                    self.sids_logins[recipient] = recipient_login

                # Save to Redis
                data_to_send = {
                    'thread_id': self.thread,
                    'sender': self.user_login,
                    'recipient': self.sids_logins[recipient],
                    'body': data['body'],
                    'datetime': (datetime.now() - datetime(1970, 1, 1)).total_seconds()
                }

                yield tornado.gen.Task(self.client.sadd, "thread:" + self.thread, proto.json_encode(data_to_send))
                yield tornado.gen.Task(self.client.sadd, 'new_threads:all', "thread:" + self.thread)

                # Send to Socket
                data_to_send['type'] = 'message'
                data_to_send['datetime_'] = utc_to_localtime(data_to_send['datetime'], self.user_timezone)
                self.send(proto.json_encode(data_to_send))

                # if recipient is online
                if recipient in self.users:
                    timezone = self.timezones[recipient] if recipient in self.timezones else utc
                    data_to_send['datetime_'] = utc_to_localtime(data_to_send['datetime'], timezone)
                    self.users[recipient].send(proto.json_encode(data_to_send))
            else:
                logging.info('Bad request: ' + str(data))
        else:
            logging.info('Bad request: ' + str(data))

    def on_close(self):
        del self.users[self.user_sid]
        del self.timezones[self.user_sid]


def start_tornado():
    # logging.getLogger().setLevel(logging.DEBUG)
    # logging.getLogger().setLevel(logging.INFO)

    EchoRouter = SockJSRouter(PlansqTornadoChat, '/socket')

    app = web.Application(EchoRouter.urls)
    app.listen(config.TORNADO_PORT)
    ioloop.IOLoop.instance().start()



if __name__ == '__main__':
    start_tornado()