# -*- coding: utf-8 -*-
__author__ = 'Van'
from qiniu import Auth
from flask import request, Blueprint, current_app, jsonify
import json

api = Blueprint('qiniu_controller', __name__, url_prefix='/qiniu')


@api.route('/up_token', methods=['GET'])
def get_token():
    try:
        q = Auth(
            current_app.config.get("QINIU_ACCESS_KEY"),
            current_app.config.get("QINIU_SECRET_KEY"))
        key = request.args.get('key', '')
        if key == '':
            return 'error, key lost'
        # 上传策略仅指定空间名和上传后的文件名，其他参数仅为默认值
        token = q.upload_token(current_app.config.get("QINIU_BUCKET_NAME"), key)
    except Exception, e:
        current_app.logger.error(e)
        return json.dumps({"code": 0})
    return json.dumps({"code": 1, "uptoken": token})


@api.route('/init/', methods=['GET'])
def init():
    return jsonify({"qiniu_bucket_domain": current_app.config.get("QINIU_BUCKET_DOMAIN")})

