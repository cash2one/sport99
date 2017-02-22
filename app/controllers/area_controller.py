# coding:utf-8
# _author_ = jiangzhuang

from flask import Blueprint, request, current_app, jsonify
from .. import db

area_controller = Blueprint('area_controller', __name__, url_prefix='/area')


@area_controller.route('/area_list', methods=['POST'])
def area_list():
    '''
    获取城市列表
    '''
    try:
        # 查询城市列表
        querysql = "select * from areas a " \
                   "where a.pid in (select id from areas where pid = '1') " \
                   "or ( short_name = '2' and id in ('10','2','3','23') )" \
                   "order by id "
        areas = db.session.execute(querysql)

        area_list = []
        # 封装从数据库中查询到的对象
        for area in areas:
            area_dict = {'id': area[0], 'name': area[3]}
            area_list.append(area_dict)
        return jsonify({'code': 1, 'result': area_list})
    except Exception, e:
        current_app.logger.error(str(e))
        e_msg = 'area ajax_list service except '
        return jsonify({'code': 0, 'error': e_msg})
