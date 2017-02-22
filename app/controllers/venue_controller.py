# coding=utf-8
# _author_ = jiangzhuang

from flask import Blueprint, request, current_app, jsonify

from app.models import Venue
from .. import db

venue_controller = Blueprint('venue_controller', __name__, url_prefix='/venue')

#保存地址
@venue_controller.route('/post', methods=['POST'])
def post():
    # 获取经纬坐标
    coordinate_lng = request.form.get('coordinate_lng', '')
    coordinate_lat = request.form.get('coordinate_lat', '')
    if coordinate_lng and coordinate_lat :
        # 先从数据库中 通过坐标获取地点,如果有直接返回，没有则保存
        venue = db.session.query(Venue).filter(Venue.coordinate_lng == coordinate_lng,
                                               Venue.coordinate_lat == coordinate_lat).first()

        if venue:
            data = {'id': venue.id}
            return jsonify({'code': 1, 'result': data})
        else :
            try:
                venue = Venue()
                venue.name = request.form.get('name', '')
                venue.address = request.form.get('address', '')
                venue.coordinate_lng = coordinate_lng
                venue.coordinate_lat = coordinate_lat
                venue.category = request.form.get('category', '')
                venue.link_man_mobile = request.form.get('link_man_mobile', '')

                venue = Venue().add(venue)
                data = {'id': venue.id}
                return jsonify({'code': 1, 'result': data})
            except Exception, e:
                current_app.logger.error(str(e))
                e_msg = ' venue save error '
                return jsonify({'code': 0, 'error': e_msg})
    else:
        e_msg = ' coordinate_lng or coordinate_lat is null '
        return jsonify({'code': 0, 'error': e_msg})
