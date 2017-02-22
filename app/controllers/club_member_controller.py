# coding: utf-8
__author__ = 'zhaojm'

from flask import request, Blueprint, jsonify, current_app
from .. import db
from ..models import Club, ClubMember, User
import string


club_member_controller = Blueprint('club_member_controller', __name__, url_prefix='/club_member')


@club_member_controller.route('/add', methods=['POST'])
def add():
    user_id = string.atoi(request.args.get('user_id'))
    club_id = string.atoi(request.args.get('club_id'))
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            raise Exception('user is not found')

        club = db.session.query(Club).filter_by(id=club_id).first()
        if not club:
            raise Exception('club is not found')

        cm = db.session.query(ClubMember).filter_by(user_id=user_id, club_id=club_id).first()
        if cm:
            raise Exception('already have this club member')

        cm = ClubMember()
        cm.club_id = club_id
        cm.user_id = user_id
        db.session.add(cm)
        db.session.commit()
        return jsonify({'code': 1})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})


@club_member_controller.route('/remove/<user_id>/<club_id>', methods=['DELETE'])
def remove(user_id, club_id):
    try:
        club = db.session.query(Club).filter_by(id=club_id).first()
        if not club:
            raise Exception('club is not found')

        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            raise Exception('user is not found')

        if club.creator_id == user_id:
            raise Exception('the user is creator')

        cm = db.session.query(ClubMember).filter_by(user_id=user_id, club_id=club_id, status=0).first()
        if not cm:
            error = 'do not find this club member'
            raise Exception(error)

        cm.status = -1
        db.session.add(cm)
        db.session.commit()
        return jsonify({'code': 1})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})

