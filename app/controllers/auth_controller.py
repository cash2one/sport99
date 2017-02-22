# coding=utf-8
# _author_ = jiangzhuang
'''
登录，权限控制
'''
from app.utils.common import model2dict
from flask import Blueprint, request, jsonify,current_app,redirect,session
from .. import db
from app.models import User,WeixinUser
from flask.ext.login import login_required,login_user,logout_user,current_user
from app.utils.WxUtil import WxUtil
auth_controller = Blueprint('auth_controller', __name__, url_prefix='/auth')


# 用户登录
@auth_controller.route('/login', methods=['POST'])
def login():

    try:
        userid = request.args.get('user_id')
        if userid:
            user = User().getUserById(userid)
            if user:
                login_user(user)
                return jsonify({'code': 1})
            else:
                return jsonify({'code': 0,'error':' error user_id '})
        else:
            return jsonify({'code': 0,'error':'  user_id is None'})
    except Exception,e:
        current_app.logger.error(str(e))
        return jsonify({'code': 0,'error': ' user login error  '})


# 用户退出
@auth_controller.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'code': 1})



# 每次访问前
@auth_controller.before_app_request
def before_request():
    if not current_user.is_authenticated():
       if 'login_user_id' in session:
          user_id = session['login_user_id']
          current_app.logger.debug(' userid in session is :' + str(user_id))


