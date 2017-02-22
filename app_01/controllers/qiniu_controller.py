# -*- coding: utf-8 -*-
__author__ = 'Van'
from qiniu import Auth
from flask import request, Blueprint, current_app, jsonify
import json

api = Blueprint('qiniu_controller', __name__)


@api.route('/qiniu/up_token', methods=['GET'])
def get_token():
    try:
        q = Auth(
            current_app.config.get("QINIU_ACCESS_KEY"),
            current_app.config.get("QINIU_SECRET_KEY"))
        token = q.upload_token(current_app.config.get("QINIU_BUCKET_NAME"))
        return json.dumps({"code": 1, "uptoken": token})
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})


@api.route('/qiniu/init/', methods=['GET'])
def init():
    return jsonify({"qiniu_bucket_domain": current_app.config.get("QINIU_BUCKET_DOMAIN")})

