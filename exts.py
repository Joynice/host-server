# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_socketio import SocketIO
db = SQLAlchemy()
email = Mail()
socketio = SocketIO()