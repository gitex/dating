# Add current path to sys.path of Python

from sockjs.tornado import SockJSRouter, SockJSConnection, proto
from tornado import web, ioloop

import logging
import os
import sys

from TornadoChat.chat_SockJS_tornado import start_tornado
from Dater import app, socketio
from Dater.config import FLASK_PORT, TORNADO_PORT


current_path = os.path.abspath(os.path.dirname(__file__))

if current_path not in sys.path:
    sys.path.insert(1, current_path)


# RUN FLASK
app.run(port=FLASK_PORT)
