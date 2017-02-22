# coding:utf-8
__author__ = 'zhaojm'

import string
from flask import Blueprint, request, current_app, jsonify
from .. import db
from ..models import Club, ClubMember
from app.mysql import ClubDB,ClubMembersDB,UserDB
from app.utils.common import model2dict,get_value_from_dict

club_controller = Blueprint('club_controller', __name__, url_prefix='')


@club_controller.route('/init/<user_id>/<token>', methods=['GET'])
def club_init(user_id, token):
    try:
        club = db.session.query(Club).filter(Club.creator_id == user_id).first()
        if club:
            error = 'already create a club'
            raise Exception(error)

        club = Club()
        db.session.add(club)
        db.session.commit()
        result = {'club_id': club.id}
        return jsonify({'code': 1, 'result': result})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})


@club_controller.route('/clubs', methods=['POST'])
def clubs():
    try:
        club = Club(request.args)
        if not club.name or not club.tags:
            raise Exception('params not complete,(name, head_url, tags)')
        if not club.id:
            club.status = 0
        current_app.logger.debug(model2dict(club))
        ClubDB.add_club(club)
        return jsonify({'code': 1})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})


@club_controller.route('/update', methods=['PUT'])
def update():

    club_id = string.atoi(request.args.get('club_id'))
    creator_id = string.atoi(request.args.get('creator_id'))

    try:
        club = db.session.query(Club).filter_by(id=club_id).first()
        if not club:
            error = 'club is not found'
            raise Exception(error)

        club.name = request.args.get('name')
        club.head_url = request.args.get('head_url')
        club.tags = request.args.get('tags')

        if not club.name or not club.head_url or not club.tags:
            error = 'params not complete,(name, head_url, tags)'
            raise Exception(error)

        if club.creator_id != creator_id:
            error = 'not the creator, refuse to update'
            raise Exception(error)

        db.session.add(club)
        db.session.commit()
        return jsonify({'code': 1})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})


@club_controller.route('/clubs/show/<club_id>', methods=['GET'])
def detail(club_id):
    try:
        club = ClubDB.club_by_id(club_id)
        if not club:
            raise Exception('not found this club')

        return jsonify({'code': 1, 'club': model2dict(club)})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})


@club_controller.route('/mine_clubs', methods=['GET'])
def club_list():
    try:
        user_id = get_value_from_dict(request.args,"user_id",'')
        club = ClubDB.club_by_user(user_id)

        clubs = db.session.query(Club).\
            select_from(ClubMember).\
            filter_by(user_id=user_id, status=0).\
            join(Club, ClubMember.club_id == Club.id).all()

        return jsonify({'code': 1, 'club': model2dict(club),'follow_clubs':model2dict(clubs)})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})


@club_controller.route('/remove/<creator_id>/<club_id>', methods=['DELETE'])
def remove(creator_id, club_id):
    try:
        club = db.session.query(Club).filter(Club.id == club_id, Club.status == 0).first()
        if not club:
            raise Exception('not found this club')

        if club.creator_id != creator_id:
            raise Exception('refuse to delete, not the creator')

        club.status = -1
        db.session.add(club)
        db.session.commit()
        return jsonify({'code': 1})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})


@club_controller.route('/clubs/<c_id>/members', methods=['GET'])
def members_of_club(c_id):
    try:
        club_id = int(c_id)

        club = ClubDB.club_by_id(club_id)
        if club:
           members = ClubMembersDB.members_of_club(club_id)
           creator = UserDB.user_by_id(club.creator_id)
           managers = []
           managers.append(creator)
           return jsonify({"code": 1,"members": model2dict(members),"managers": model2dict(managers)})
        raise Exception(' error club id')
    except Exception,e:
        current_app.logger.error(e.message)
        return jsonify({'code': 0, 'error': e.message})
