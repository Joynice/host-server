# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from flask import Blueprint, make_response
from utils.captcha import Captcha
from utils import zlcache
from io import BytesIO
bp = Blueprint('common', __name__, url_prefix='/c')

@bp.route('/captcha/')
def graph_captcha():
    text, image = Captcha.gene_graph_captcha()
    zlcache.set(text.lower(), text.lower())
    out = BytesIO()
    image.save(out, 'png')
    out.seek(0)
    resp = make_response(out.read())
    resp.content_type = 'image/png'
    return resp