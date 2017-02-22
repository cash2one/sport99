# coding:utf-8
__author__ = 'zhaojm'

from flask import Blueprint, current_app, request, jsonify
from .. import db
from ..models import ActivityCluster, Activity, User, ActivityMember, Cluster, QQUser, ClusterMember, Venue, QQBindCode
import json
from sqlalchemy.sql import and_
import time, datetime

robot_controller = Blueprint('robot_controller', __name__, url_prefix='/qq')


@robot_controller.route('/', methods=['GET'])
def index():
    return 'robot index'


# =========================utils begin=============================
def select_func(cmd, func_dict, params):
    func = func_dict.get(cmd)

    if not func:
        return jsonify({'retcode': -1, 'errmsg': 'bad cmd'})
    return func(params)


# =========================utils end=============================


# =========================receive begin=============================
@robot_controller.route('/receive', methods=['POST'])
def receive():
    print('---------key values begin--------------------------')
    for key in request.form:
        print key, ': ', request.form[key]
    print('-----------key values end------------------------')

    data = request.form.get('data')
    cmd = request.form.get('cmd')
    if not data or not cmd:
        return jsonify({'code': -1, 'errmsg': 'data or cmd not found'})
    data_json = json.loads(data)
    func_dict = {
        'getActivityList': get_activity_list,
        'getActivityDetail': get_activity_detail,
        'joinActivity': join_activity,
        'cancelJoinActivity': cancel_join_activity,
        'helpJoinActivity': help_join_activity,
        'helpCancelJoinActivity': help_cancel_join_activity,
        'speJoinActivity': spe_join_activity,
        'speCancelJoinActivity': spe_cancel_join_activity,
        'sendNormalIM': send_normal_im,
        'sendTmpIM': send_tmp_im,
    }

    return select_func(cmd, func_dict, data_json)


def get_activity_list(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    # qq = params.get('qq')

    try:
        act_list_from_db = db.session.query(Activity). \
            select_from(ActivityCluster). \
            filter_by(
            cluster_id=external_id,
            status=0
        ).join(
            Activity,
            and_(ActivityCluster.activity_id == Activity.id, 0 == Activity.status)
        ).all()
        print('act_list_from_db=', act_list_from_db)
        a_list = []
        for act in act_list_from_db:
            venue = db.session.query(Venue).filter_by(id=act.venue_id).first()
            if not venue:
                raise Exception('not found the venue by id %r' % act.venue_id)
            a_dict = {
                # 'id': act.id,
                'sign': act.sign,
                'name': act.name,
                'start_time': time.strftime('%H:%M', time.localtime(int(act.start_time))),
                'end_time': time.strftime('%H:%M', time.localtime(int(act.start_time))),
                # 'venue_id': act.venue_id,
                'venue_name': venue.name
                # 'member_count_limit': act.member_count_limit,
                # 'member_count': act.member_count,
                # 'status': act.status,
            }
            a_list.append(a_dict)
        print('result=', a_list)
        return jsonify({'retcode': 0, 'result': a_list})

    except Exception, e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': 1, 'errmsg': e.message})


def get_activity_detail(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    # qq = params.get('qq')
    try:
        if not sign:
            # 查找最近的活动
            act = db.session.query(Activity). \
                select_from(ActivityCluster). \
                filter_by(
                cluster_id=external_id,
                status=0
            ).join(
                Activity,
                and_(ActivityCluster.activity_id == Activity.id, Activity.status == 0)
            ).order_by(Activity.start_time).first()
            if not act:
                return jsonify({'retcode': 1004, 'errmsg': '目前没有可以参加的活动'})

        else:
            # 查找sign活动
            act = db.session.query(Activity). \
                select_from(ActivityCluster). \
                filter_by(
                cluster_id=external_id,
                status=0
            ).join(
                Activity,
                and_(ActivityCluster.activity_id == Activity.id, Activity.status == 0, Activity.sign == sign)
            ).first()
            if not act:
                return jsonify({'retcode': 1004, 'errmsg': 'not found this activity'})
        print 'act:=', act

        venue = db.session.query(Venue).filter_by(id=act.venue_id).first()
        if not venue:
            raise Exception('not found the venue by id %r' % act.venue_id)
        user = db.session.query(User).filter_by(id=act.creator_id).first()
        if not user:
            raise Exception('creator not found id=%r' % act.creator_id)
        act_members = db.session.query(ActivityMember).filter_by(activity_id=act.id, status=0).all()
        members_json = []
        for member in act_members:
            nick = ""
            qq = -1
            if member.user_temp:
                nick = member.user_temp
                qq = -1
            else:
                user = db.session.query(User).filter_by(id=member.user_id).first()
                nick = user.nick
                qq = user.qq
            m_dict = {}
            m_dict.update({
                'nick': nick,
                'qq': qq,
                'gua': member.num - 1,
                'help_qq': member.help_qq,
                'channel': member.channel,
            })
            print 'm_dict:=', m_dict
            members_json.append(m_dict)
        print 'members_json:=', members_json
        a_dict = {
            'id': act.id,
            'sign': act.sign,
            'start_time': time.strftime('%H:%M', time.localtime(int(act.start_time))),
            'end_time': time.strftime('%H:%M', time.localtime(int(act.start_time))),
            # 'venue_id': act.venue_id,
            'venue_name': venue.name,
            'creator_name': user.nick,
            'mobile': act.mobile,
            'member_count_limit': act.member_count_limit,
            # 'member_count': act.member_count,
            # 'status': act.status,
            'members': members_json,
        }
        return jsonify({'retcode': 0, 'exist': True, 'result': a_dict})

    except Exception, e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    gua = params.get('gua')

    return common_join_activity(sign, robot, external_id, qq, gua, None, None)


def cancel_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))

    return common_cancel_join_activity(sign, robot, external_id, qq, None, None)


def help_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    gua = params.get('gua')
    friend_qq = str(params.get('friendQQ'))

    return common_join_activity(sign, robot, external_id, qq, gua, friend_qq, None)


def help_cancel_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    friend_qq = str(params.get('friendQQ'))

    return common_cancel_join_activity(sign, robot, external_id, qq, friend_qq, None)


def spe_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    gua = params.get('gua')
    friend = str(params.get('friend'))

    return common_join_activity(sign, robot, external_id, qq, gua, None, friend)


def spe_cancel_join_activity(params):
    sign = params.get('sign')
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    friend = str(params.get('friend'))

    return common_cancel_join_activity(sign, robot, external_id, qq, None, friend)


def common_join_activity(sign, robot, external_id, qq, gua, friend_qq, friend_nick):
    try:
        # 获取activity
        if sign:
            # 报名 sign 活动
            act = db.session.query(Activity). \
                select_from(ActivityCluster). \
                filter_by(cluster_id=external_id, status=0). \
                join(
                Activity,
                and_(ActivityCluster.activity_id == Activity.id, Activity.sign == sign, Activity.status == 0)). \
                first()
            print 'act:=', act
            if not act:
                return jsonify({'retcode': 1004, 'exist': True, 'errmsg': 'not found this activity '})
            pass
        else:
            # 报名最近的活动
            act = db.session.query(Activity). \
                select_from(ActivityCluster). \
                filter_by(cluster_id=external_id, status=0). \
                join(Activity,
                     and_(ActivityCluster.activity_id == Activity.id, Activity.status == 0)). \
                first()
            print 'act:=', act
            if not act:
                return jsonify({'retcode': 1004, 'exist': True, 'errmsg': 'not found this activity '})

        print 'act:=', act

        # 报名
        activity_member_result = ActivityMember()
        activity_member_result.activity_id = act.id
        activity_member_result.num = gua + 1
        activity_member_result.channel = 'qq'
        if friend_nick:
            # 帮一个nick报名
            # qq_cluster_member = db.session.query(ClusterMember).filter_by(qq=qq, external_id=external_id, status=0).first()
            # if not qq_cluster_member:
            #     raise Exception("not found this qq")
            # cluster = db.session.query(Cluster).filter_by(external_id=external_id, status=0).first()
            # if not cluster:
            #     raise Exception("not found this cluster")
            # if not qq_cluster_member.is_admin or qq != cluster.creator_qq:
            #     raise Exception("not the admin")
            activity_member = db.session.query(ActivityMember).\
                filter_by(user_temp=friend_nick, activity_id=act.id, status=0).first()
            if activity_member:
                return jsonify({'retcode': 1005, 'exist': True, 'errmsg': 'already join this activity'})

            activity_member_result.user_temp = friend_nick
            activity_member_result.help_qq = qq

        elif friend_qq:
            # 帮一个qq报名
            # qq_cluster_member = db.session.query(ClusterMember).filter_by(qq=qq, external_id=external_id, status=0).first()
            # if not qq_cluster_member:
            #     raise Exception("not found this qq")
            # cluster = db.session.query(Cluster).filter_by(external_id=external_id, status=0).first()
            # if not cluster:
            #     raise Exception("not found this cluster")
            # if not qq_cluster_member.is_admin or qq != cluster.creator_qq:
            #     raise Exception("not the admin")

            cluster_member = db.session.query(ClusterMember). \
                filter_by(external_id=external_id, qq=friend_qq, status=0).first()
            if not cluster_member:
                raise Exception('not found this cluster member')

            qq_user_from_db = db.session.query(QQUser).filter_by(qq=friend_qq, status=0).first()
            if not qq_user_from_db:
                print 'create qq user'
                qq_user = QQUser()
                qq_user.qq = friend_qq
                qq_user.nick_name = cluster_member.nick
                db.session.add(qq_user)
                db.session.commit()
                print 'create user'
                user = User()
                user.nick = cluster_member.nick
                user.qq = friend_qq
                db.session.add(user)
                db.session.commit()
                pass
            else:
                user = db.session.query(User).filter_by(qq=qq).first()
                if not user:
                    raise Exception('qq user found, user not found')

            activity_member = db.session.query(ActivityMember).\
                filter_by(user_id=user.id, activity_id=act.id, status=0).first()
            if activity_member:
                 return jsonify({'retcode': 1005, 'exist': True, 'errmsg': 'already join this activity'})

            activity_member_result.user_id = user.id
            activity_member_result.help_qq = qq

        else:
            # 自己报名
            cluster_member = db.session.query(ClusterMember).filter_by(external_id=external_id, qq=qq, status=0).first()
            if not cluster_member:
                raise Exception('not found this cluster member')

            qq_user_from_db = db.session.query(QQUser).filter_by(qq=qq).first()
            if not qq_user_from_db:
                print 'create qq user'
                qq_user = QQUser()
                qq_user.qq = cluster_member.qq
                qq_user.nick_name = cluster_member.nick
                db.session.add(qq_user)
                db.session.commit()
                print 'create user'
                user = User()
                user.nick = cluster_member.nick
                user.qq = qq
                db.session.add(user)
                db.session.commit()
            else:
                user = db.session.query(User).filter_by(qq=qq).first()
                if not user:
                    raise Exception('qq user found, user not found')

            activity_member = db.session.query(ActivityMember).\
                filter_by(user_id=user.id, activity_id=act.id, status=0).first()
            if activity_member:
                 return jsonify({'retcode': 1005, 'exist': True, 'errmsg': 'already join this activity'})

            activity_member_result.user_id = user.id
            pass

        print 'activity_member_result:=', activity_member_result
        # db.session.add(activity_member)
        # db.session.commit()
        ActivityMember.join(activity_member_result)

        # 获取活动详细信息
        venue = db.session.query(Venue).filter_by(id=act.venue_id).first()
        if not venue:
            raise Exception('not found the venue by id %r' % act.venue_id)
        user = db.session.query(User).filter_by(id=act.creator_id).first()
        if not user:
            raise Exception('creator not found id=%r' % act.creator_id)
        act_members = db.session.query(ActivityMember).filter_by(activity_id=act.id, status=0).all()
        members_json = []
        for member in act_members:
            nick = ""
            qq = -1
            if member.user_temp:
                nick = member.user_temp
                qq = -1
            else:
                user = db.session.query(User).filter_by(id=member.user_id).first()
                nick = user.nick
                qq = user.qq
            m_dict = {}
            m_dict.update({
                'nick': nick,
                'qq': qq,
                'gua': member.num - 1,
                'help_qq': member.help_qq,
                'channel': member.channel,
            })
            print 'm_dict:=', m_dict
            members_json.append(m_dict)
        print 'members_json:=', members_json

        a_dict = {
            'id': act.id,
            'sign': act.sign,
            'start_time': time.strftime('%H:%M', time.localtime(int(act.start_time))),
            'end_time': time.strftime('%H:%M', time.localtime(int(act.start_time))),
            # 'venue_id': act.venue_id,
            'venue_name': venue.name,
            'creator_name': user.nick,
            'mobile': act.mobile,
            'member_count_limit': act.member_count_limit,
            # 'member_count': act.member_count,
            # 'status': act.status,
            'members': members_json,
        }
        return jsonify({'retcode': 0, 'exist': True, 'result': a_dict})

    except Exception, e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'exist': True, 'errmsg': e.message})


def common_cancel_join_activity(sign, robot, external_id, qq, friend_qq, friend_nick):
    try:
        if sign:
            # 取消单个活动sign
            # 获取活动
            act = db.session.query(Activity). \
                select_from(ActivityCluster). \
                filter_by(cluster_id=external_id, status=0). \
                join(Activity, and_(ActivityCluster.activity_id == Activity.id, Activity.sign == sign,
                                    Activity.status == 0)). \
                first()
            print 'activity:=', act
            if not act:
                 return jsonify({'retcode': 1004, 'exist': True, 'errmsg': 'not found this activity'})

            if friend_nick:
                # qq_cluster_member = db.session.query(ClusterMember).filter_by(qq=qq, external_id=external_id, status=0).first()
                # if not qq_cluster_member:
                #     raise Exception("not found this qq")
                # cluster = db.session.query(Cluster).filter_by(external_id=external_id, status=0).first()
                # if not cluster:
                #     raise Exception("not found this cluster")
                # if not qq_cluster_member.is_admin or qq != cluster.creator_qq:
                #     raise Exception("not the admin")
                activity_member = db.session.query(ActivityMember).filter_by(user_temp=friend_nick)
            elif friend_qq:
                # qq_cluster_member = db.session.query(ClusterMember).filter_by(qq=qq, external_id=external_id, status=0).first()
                # if not qq_cluster_member:
                #     raise Exception("not found this qq")
                # cluster = db.session.query(Cluster).filter_by(external_id=external_id, status=0).first()
                # if not cluster:
                #     raise Exception("not found this cluster")
                # if not qq_cluster_member.is_admin or qq != cluster.creator_qq:
                #     raise Exception("not the admin")
                activity_member = db.session.query(ActivityMember). \
                    select_from(User). \
                    filter_by(qq=friend_qq, status=0). \
                    join(
                    ActivityMember,
                    and_(
                        User.id == ActivityMember.user_id,
                        ActivityMember.activity_id == act.id,
                        ActivityMember.status == 0
                    )).first()
            else:
                activity_member = db.session.query(ActivityMember). \
                    select_from(User). \
                    filter_by(qq=qq, status=0). \
                    join(
                    ActivityMember,
                    and_(
                        User.id == ActivityMember.user_id,
                        ActivityMember.activity_id == act.id,
                        ActivityMember.status == 0
                    )).first()

            if not activity_member:
                raise Exception('您没有报名此活动')

            print 'activity member:=', activity_member
            # activity_member.status = -1
            # db.session.add(activity_member)
            # db.session.commit()
            ActivityMember.quit(activity_member)

            venue = db.session.query(Venue).filter_by(id=act.venue_id).first()
            print 'venue:=', venue
            if not venue:
                raise Exception('not found this venue')
            a_list = []
            a_dict = {}
            a_dict.update({
                'sign': act.sign,
                'venue_name': venue.name
            })
            a_list.append(a_dict)
            print 'a_dict:=', a_dict
            return jsonify({'retcode': 0, 'exist': True, 'result': a_list})

        else:
            # 取消所有活动
            if friend_nick:
                activity_members = db.session.query(ActivityMember). \
                    filter_by(user_temp=friend_nick, status=0). \
                    all()
            elif friend_qq:
                activity_members = db.session.query(ActivityMember). \
                    select_from(User). \
                    filter_by(qq=friend_qq, status=0). \
                    join(ActivityMember, and_(User.id == ActivityMember.user_id, ActivityMember.status == 0)). \
                    all()
            else:
                activity_members = db.session.query(ActivityMember). \
                    select_from(User). \
                    filter_by(qq=qq, status=0). \
                    join(ActivityMember, and_(User.id == ActivityMember.user_id, ActivityMember.status == 0)). \
                    all()

            # if not activity_members:
            #         raise Exception('not join any activity')

            print 'activity_members:=', activity_members

            a_list = []
            for activity_member in activity_members:
                # activity_member.status = -1
                # db.session.add(activity_member)
                # db.session.commit()

                activity_from_db = db.session.query(Activity).filter_by(id=activity_member.activity_id).first()
                venue = db.session.query(Venue).filter_by(id=activity_from_db.venue_id).first()
                if not venue:
                    raise Exception('not found this venue')
                a_dict = {}
                a_dict.update({
                    'sign': activity_from_db.sign,
                    'venue_name': venue.name,
                })
                a_list.append(a_dict)
                ActivityMember.quit(activity_member)

            return jsonify({'retcode': 0, 'exist': True, 'result': a_list})

    except Exception, e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'exist': True, 'errmsg': e.message})


def send_normal_im(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    message = params.get('message')
    send_time = params.get('sendTime')

    func_dict = {
        'YD99': user_bd,
        'yd99': user_bd,
    }
    return select_func(message, func_dict, params)


def send_tmp_im(params):
    send_normal_im(params)
    pass


def user_bd(params):
    try:
        qq = str(params.get('qq'))
        message = params.get('message')
        send_time = params.get('sendTime')
        qqUser = db.session.query(QQUser).fiter(QQUser.qq == qq).first()
        if not qqUser:
            raise Exception(' no this qq user ')
        qqBindCode = db.session.query(QQBindCode).filter(QQBindCode.qq == qq,QQBindCode.code == message).first()
        if qqBindCode:

            user = User().getUserById(qqBindCode.uid)
            if not user:
                raise Exception(' no this user ')
            if user.qq and user.qq != qq:
                raise Exception(' the user has bind ')
            if user.qq and user.qq == qq:
                return jsonify({'retcode': 0, 'exist': True, 'result': 'bind success '})

            oldUser = db.session.query(User).filter(User.qq == qq,User.openid=='',User.status==0).first()
            oldUser.status = -1
            db.session.add(oldUser)
            user.qq = qq
            db.session.add(user)
            # 更新活动创建者 id
            db.session.query(Activity).fiter(Activity.creator_id == oldUser.id).update(Activity.creator_id == user.id)
            # 更新活动参与者 id
            db.session.query(ActivityMember).fiter(ActivityMember.user_id == oldUser.id).update(ActivityMember.user_id == user.id)

            # 将使用过的code移除
            db.session.remove(qqBindCode)
            db.session.commit()

    except Exception,e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': 1, 'exist': True, 'errmsg': e.message})

# =========================receive end=============================


# =========================sync begin=============================
@robot_controller.route('/sync', methods=['POST'])
def sync():
    print('---------key values begin--------------------------')
    for key in request.form:
        print key, ': ', request.form[key]
    print('-----------key values end------------------------')

    data = request.form.get('data')
    cmd = request.form.get('cmd')
    if not data or not cmd:
        return jsonify({'retcode': -1, 'errmsg': 'data or cmd not found'})
    data_json = json.loads(data)

    func_dict = {
        'saveUser': save_user,
        'removeUser': remove_user,
        'saveCluster': save_cluster,
        'removeCluster': remove_cluster,
        'addToCluster': add_to_cluster
    }

    return select_func(cmd, func_dict, data_json)


def save_user(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    nick = params.get('nick')
    is_admin = params.get('isAdmin')
    q_age = params.get('aAge')
    card = params.get('card')
    black = params.get('black')
    try:
        cluster_member = db.session.query(ClusterMember).filter_by(qq=qq, external_id=external_id, status=0).first()
        if not cluster_member:
            cluster_member = ClusterMember()
            cluster_member.external_id = external_id
            cluster_member.qq = qq
            cluster_member.nick = nick
            cluster_member.is_admin = is_admin
            cluster_member.card = card
            db.session.add(cluster_member)
            db.session.commit()
            pass

        qq_user = db.session.query(QQUser).filter_by(qq=qq).first()
        if not qq_user:
            qq_user = QQUser()
            qq_user.qq = qq
        qq_user.nick_name = nick
        qq_user.status = 0
        db.session.add(qq_user)
        db.session.commit()

        user = db.session.query(User).filter_by(qq=qq).first()
        if not user:
            user = User()
        user.qq = qq
        user.nick = nick
        user.status = 0
        db.session.add(user)
        db.session.commit()
        return jsonify({'retcode': 0})

    except Exception, e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def remove_user(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    qq = str(params.get('qq'))
    try:
        cluster_member = db.session.query(ClusterMember).filter_by(qq=qq, external_id=external_id, status=0).first()
        if cluster_member:
            db.session.delete(cluster_member)
            db.session.commit()
            pass
        qq_user = db.session.query(QQUser).filter_by(qq=qq, status=0).first()
        if qq_user:
            qq_user.status = -1
            db.session.add(qq_user)
            db.session.commit()
            pass
        return jsonify({'retcode': 0})

    except Exception, e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})
    pass


def save_cluster(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    name = params.get('name')
    creator = str(params.get('creator'))
    members = params.get('members')

    try:
        cluster = db.session.query(Cluster).filter_by(external_id=external_id).first()
        if not cluster:
            cluster = Cluster()
            cluster.external_id = external_id
        cluster.name = name
        cluster.creator_qq = creator
        cluster.status = 0
        db.session.add(cluster)
        db.session.commit()

        for member in members:
            qq = str(member.get('qq'))
            cluster_member = db.session.query(ClusterMember).filter_by(external_id=external_id, qq=qq).first()
            if not cluster_member:
                cluster_member = ClusterMember()
            cluster_member.external_id = str(member.get("externalId"))
            cluster_member.qq = qq
            cluster_member.nick = member.get("nick")
            cluster_member.is_admin = member.get("isAdmin")
            # cluster_member.qAge = member.get("qAge")
            cluster_member.card = member.get("card")
            # cluster_member.black = member.get("black")
            db.session.add(cluster_member)
            db.session.commit()
            pass
        return jsonify({'retcode': 0})

    except Exception, e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def remove_cluster(params):
    robot = params.get('robot')
    external_id = params.get('externalId')
    try:
        cluster = db.session.query(Cluster).filter_by(external_id=external_id, status=0).first()
        if cluster:
            cluster.status = -1
            db.session.add(cluster)
            db.session.commit()

            # members = db.session.query(ClusterMember).filter_by(external_id=external_id, status=0).all()
            # for member in members:
            #     member.status = -1
            #     db.session.add(member)
            #     db.session.commit()
            #     pass
        # print 'remove cluster retcode = 0'
        return jsonify({'retcode': 0})

    except Exception, e:
        db.session.rollback()
        current_app.logger.error(e.message)
        return jsonify({'retcode': -1, 'errmsg': e.message})


def add_to_cluster(params):
    robot = str(params.get('robot'))
    external_id = str(params.get('externalId'))
    # TODO add push cmd  暂时没用
    return jsonify({'retcode': 0})


# =========================sync end=============================


# =========================push begin=============================
@robot_controller.route('/push', methods=['POST'])
def push():
    print('---------key values begin--------------------------')
    for key in request.form:
        print key, ': ', request.form[key]
    print('-----------key values end------------------------')

    data = request.form.get('data')
    cmd = request.form.get('cmd')
    if not data or not cmd:
        return jsonify({'code': -1, 'errmsg': 'data or cmd not found'})
    data_json = json.loads(data)

    func_dict = {
        'doPush': do_push,
    }

    return select_func(cmd, func_dict, data_json)


_PushTaskType = {
    'SendTmpMsg': 0,
    'SaveCluster': 0,
    'SaveAllClusters': 0,
    'SendClusterMsg': 0,
    'SendMsg': 0,
    'SendAttetion': 0,
    'JoinCluster': 0,
    'default': -1,
}

push_task_list = []


# task:{
#     type: 1,
#     args: 1,
# }


def do_push(params):
    # TODO do_push
    pass

# =========================push end=============================
