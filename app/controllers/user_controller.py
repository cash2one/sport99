# coding:utf-8
__author__ = 'zhaojm'

# 权限控制
from .. import login_manager
from app.models import User,QQUser,QQBindCode
from flask_login import login_required
from app.utils.common import model2dict
from flask import Blueprint, request, current_app, jsonify
from app import db
from app.mysql import UserDB
import time
'''
用户操作
'''
user_controller = Blueprint('user_controller', __name__, url_prefix='')


#修改
@user_controller.route('/update',methods=['POST'])
@login_required
def update():
    try :
        user_id = ''


        user_arr = request.args

        user_db = UserDB.update_user_data(user_id,user_arr)

        UserDB.update_user_data(user_id,user_arr)
        #user.password = request.form.get('password','')

        #密码加密
        #user.password = user.hash_password()

        return jsonify({'code': 1})
    except Exception,e:
        db.session.rollback()
        current_app.logger.error(str(e))
        e_msg = 'act_init service  except '
        return jsonify({'code': 0, 'error': e_msg})

#查询
@user_controller.route('/api/users/show/<user_id>',methods=['GET'])
@login_required
def detail(user_id):
    try:
      user = UserDB.user_by_id(user_id)
      if user:
          return jsonify({'code': 1, 'user':model2dict(user)})
      else :
          return jsonify({'code': 0, 'error': ' no user'})
    except Exception,e:
       current_app.logger.error(str(e))
       e_msg = ' get user detail exception '
       return jsonify({'code': 0, 'error': e_msg})


