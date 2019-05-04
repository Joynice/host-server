# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from .views import bp
from config import config
from flask import session, g, redirect, url_for
from .models import User, CMSPersmission


@bp.before_request
def before_request():
    if config['development'].CMS_USER_ID in session:
        user_id = session.get(config['development'].CMS_USER_ID)
        user = User.query.get(user_id)
        all_user =  User.query.all()
        if user:
            g.cms_user = user
            g.all_user = all_user


@bp.context_processor
def cms_context_processor():
    return {'CMSPermission': CMSPersmission}
