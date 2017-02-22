# coding:utf-8
__author__ = 'zhaojm'

import time,datetime

from app import db
from app.models import Activity, Club, CycleActivity, User, ActivityMember,Venue
from app.mysql import ActivityCategoryDB,ActivityLevelDB,ActivityDB,ClusterDB,\
    ClubDB,UserDB,VenueDB,ActivityMemberDB
from app.utils.common import model2dict
from flask import Blueprint, request, current_app, jsonify
from flask_login import login_required
# from flask.ext.login import login_required

activity_controller = Blueprint('activity_controller', __name__, url_prefix='')


# 初始化活动
@activity_controller.route('/event_id', methods=['GET'])
def act_init():
    try:
        user_id = request.args.get("user_id", '')
        user = UserDB.user_by_id(user_id)
        if not user:
            return jsonify({'code': 0, 'error': ' user is not exist '})
        # 判断是否有俱乐部
        club = ClubDB.club_by_user(user_id)
        # 初始化活动()
        activity = ActivityDB.init_activity(user_id)
        activity_id = activity.id

        # QQ群组
        cluster_arr = ClusterDB.list_cluster_by_user(user.qq)

        return jsonify({'code': 1, 'id': activity_id, 'club': model2dict(club), 'cluster_list': model2dict(cluster_arr)})
    except Exception, eo:
        current_app.logger.error(str(eo))
        e_msg = 'act_init service  except '
        return jsonify({'code': 0, 'error': e_msg})


# 活动列表
@activity_controller.route('/events', methods=['GET'])
def act_list():
    try:
        # 前台传的排序规则
        act_arr = request.form

        page_index = 1
        page_size = 1

        act_filter = {} # 过滤条件
        by_distance = act_arr.get('distance', None)  # 最近距离
        by_default = act_arr.get('is_default', None)  # 默认
        if by_distance:
            act_filter = {"by_distance":by_distance}
        elif by_default:
            act_filter = {"by_default":by_default}
        else:
            category = act_arr.get('category', None)  # 活动类别
            if category:
               act_filter["category"] = category
            week = act_arr.get('week', None)  # 星期几
            if week:
               act_filter["week"] = week


        act_list = ActivityDB.get_activity_list(act_filter,page_size,page_index)
        current_app.logger.debug("act_list:"+str(model2dict(act_list)))
        return jsonify({'code': 1, 'events': model2dict(act_list)})
    except Exception, e:
        current_app.logger.error(str(e))
        e_msg = ' act_list service  except '
        return jsonify({'code': 0, 'error': e_msg})


# 活动展示
@activity_controller.route('/events/<e_id>', methods=['GET'])
def detail(e_id):
    '''
    查询活动详情
    :return:
    '''
    try:

        user_id = int(request.args.get("user_id",''))
        current_app.logger.debug("user_id :"+str(user_id))
        # 查询活动
        activity = ActivityDB.activity_by_id(e_id)
        act_dic = model2dict(activity)
        print 'act_dic : ' + str(act_dic)

        if not activity:
            raise Exception(' no this activity ')

        if "venue_id" in act_dic and act_dic["venue_id"]:
           venue = VenueDB.venue_by_id(activity.venue_id)
           activity.venue = venue
        if "club_id" in act_dic and act_dic["club_id"]:
           club = ClubDB.club_by_id(activity.club_id)
           activity.club = club
        members = ActivityMemberDB.activity_members_by_act(e_id)
        activity.members = members

        join_count = 0
        is_creator = False
        has_joined = False

        # 判断是否创建者
        if activity.creator_id == user_id:
           is_creator = True
        # 判断是否参加活动
        for member in members:
            if member.user_id == user_id:
                has_joined = True
                join_count = member.num


        '''
        sql = 'select a.id as id,a.start_time as start_time,a.end_time as end_time ,' \
              'a.venue_id as venue_id,a.member_count_limit as member_count_limit,a.member_count as member_count,' \
              'a.`status` as `status`,c.`name` as club_name,c.head_url as club_head_url ' \
              'from activities a LEFT JOIN clubs c on a.club_id = c.id where a.id = ' + e_id
        activity = db.session.execute(sql).first()
        if activity:
            act_dict = {
                'id': activity[0],
                'start_time': activity[1],
                'end_time': activity[2],
                'venue_id': activity[3],
                'member_count': activity[4],
                'current_num': activity[5],
                'status': activity[6],
                'club': {
                    'name': activity[7],
                    'head_url': activity[8]
                }
            }
            return jsonify({'code': 1, 'result': {"event": act_dict}})
        else:
            return jsonify({'code': 0, 'error': "no event from db"})
        '''
        return jsonify({"code": 1, "event": model2dict(activity),"is_creator": is_creator,
                        "has_joined": has_joined,"join_count": join_count,"role": 0})
    except Exception, eo:
        current_app.logger.error(str(eo))
        return jsonify({'code': 0, 'error': " activity detail error"})


# 更新活动信息
@activity_controller.route('/events', methods=['POST'])
# @login_required
def events():
    '''
    时间类型为时间戳格式
    :return:
    '''

    try:
        post_arr = request.form
        current_app.logger.debug(str(post_arr))
        if not post_arr:
            raise Exception('not post params ')
        activity = Activity(post_arr)
        venue = Venue(post_arr)
        venue_db = VenueDB.venue_by_coordinate(venue.coordinate_lng,venue.coordinate_lat)
        if venue_db:
            activity.venue_id = venue_db.id
        else:
            venue = VenueDB.add_venue(venue)
            activity.venue_id = venue.id

        # 处理时间
        start_time = activity.start_time
        end_time = activity.end_time
        if start_time > end_time:
            return jsonify({'code': 0, 'error': 'start_time > end_time'})
        week = int(time.strftime('%w',time.localtime(start_time)))
        activity.week = week

        activity.start_time = start_time
        activity.end_time = end_time
        is_cycle = post_arr.get('is_cycle', '')

        cluster_ids = request.args.get('cluster_id', None)
        # 判断是否需要报名标示
        if cluster_ids:
            # 获取报名标示
            sign  = ActivityDB.get_activity_sign(cluster_ids)
            current_app.logger.debug(' sign ---------------------------------')
            if sign:
                activity.sign = sign
            else :
                raise Exception(' no sign get')
        current_app.logger.debug(' no sign ---------------------------------')
        ActivityDB.update_activity(activity)

        if is_cycle == 1:
            # 创建周期活动
            cycleActivity = CycleActivity()
            cycleActivity.category = activity.category
            cycleActivity.name = activity.name
            cycleActivity.start_time = activity.start_time
            cycleActivity.end_time = activity.end_time
            cycleActivity.venue_id = activity.venue_id
            cycleActivity.fee = activity.fee
            cycleActivity.is_aa = activity.is_aa
            cycleActivity.member_count_list = activity.member_count_limit
            cycleActivity.place_num = activity.place_num
            cycleActivity.mobile = activity.mobile

            cycleActivity.club_id = activity.club_id
            # 获取周期活动时间
            cycleActivity.week = activity.week

            CycleActivity().add(cycleActivity)
        return jsonify({'code': 1})
    except Exception, eo:
        current_app.logger.error(str(eo))
        return jsonify({'code': 0, 'error': "update activity error"})


# 活动状态改变
@activity_controller.route('/event', methods='POST')
def event():
    '''
       取消 ， 发布
    '''
    try:
        event = request.args.get('event')
        # 根据不同操作，改变活动状态码

    except Exception, e:
        current_app.logger.error(str(e))
        return jsonify({'code': 0, 'error': "change activity status error"})


# 活动等级列表获取
@activity_controller.route('/levels/<category>', methods=['GET'])
def level_list(category):
    '''
    获取活动等级列表
    :return:
    '''
    try:
        # 活动等级列表
        act_level_list = ActivityLevelDB.list_activity_level(category)
        return jsonify({'code': 1, 'result': model2dict(act_level_list)})
    except Exception, e:
        current_app.logger.error(str(e))
        e_msg = 'act_level_list service except '
        return jsonify({'code': 0, 'error': e_msg})


# 活动种类列表获取
@activity_controller.route('/categories', methods=['GET'])
def category_list():
    try:
        # 活动类别列表
        act_categories = ActivityCategoryDB.list_activity_category()
        return jsonify({'code': 1, 'result': model2dict(act_categories)})
    except Exception, e:
        current_app.logger.error(str(e))
        e_msg = 'activity  category_list except '
        return jsonify({'code': 0, 'error': e_msg})


# 报名活动
@login_required
@activity_controller.route('/events/<e_id>/join', methods=['POST'])
def act_join(e_id):
    try:
        arr = request.args
        print str(arr),e_id
        userid = arr.get('user_id')
        activity_id = e_id
        join_count = int(arr.get('join_count','0'))
        exit_count = int(arr.get('exit_count','0'))

        channel = 'weixin'
        status = 0
        if join_count>0 and exit_count==0:
            #  参加活动
            current_app.logger.debug("join ")

            # 判断活动
            activity = db.session.query(Activity).filter(Activity.id == activity_id,Activity.status == 0).first()
            if not activity:
               return jsonify({'code': 0, 'error': ' activity id error '})

            # 判断是否报名
            act_member = db.session.query(ActivityMember).filter(ActivityMember.activity_id == activity_id,ActivityMember.user_id == userid,ActivityMember.status == 0).first()
            if act_member :
               return jsonify({'code': 0, 'error': ' has join '})



            # 新增报名
            activityMember = ActivityMember()
            activityMember.activity_id = activity_id
            activityMember.user_id = userid
            activityMember.channel = channel
            activityMember.num = join_count
            activityMember.status = status
            ActivityMemberDB.activity_member_join(activityMember)
            return jsonify({'code': 1})

        elif exit_count>0 and join_count<=0:
            current_app.logger.debug("exit ")
            # 退出活动
            # 判断活动
            activity = db.session.query(Activity).filter(Activity.id == activity_id,Activity.status == 0).first()
            if not activity:
               return jsonify({'code': 0, 'error': ' activity id error '})

            # 判断是否报名
            act_member = db.session.query(ActivityMember).filter(ActivityMember.activity_id == activity_id,ActivityMember.user_id == userid,ActivityMember.status == 0).first()
            if not act_member :
               return jsonify({'code': 0, 'error': ' has not join '})

            # 取消报名
            activityMember = ActivityMember()
            activityMember.activity_id = activity_id
            activityMember.user_id = userid
            ActivityMemberDB.activity_member_quit(activityMember)
            return jsonify({'code': 1})
        else:
           return jsonify({'code': 0, 'error': ' the num is error '})


    except Exception,e:
        current_app.logger.error(str(e))
        e_msg = 'act join except '
        return jsonify({'code': 0, 'error': e_msg})


# 取消报名
@activity_controller.route('/quit', methods=['POST'])
def act_quit():
    try:
        userid = request.args.get('userid')
        activity_id = request.args.get('activity_id')

        # 判断活动
        activity = db.session.query(Activity).filter(Activity.id == activity_id,Activity.status == 0).first()
        if not activity:
           return jsonify({'code': 0, 'error': ' activity id error '})

        # 判断是否报名
        act_member = db.session.query(ActivityMember).filter(ActivityMember.activity_id == activity_id,ActivityMember.user_id == userid,ActivityMember.status == 0).first()
        if not act_member :
           return jsonify({'code': 0, 'error': ' has not join '})

        # 取消报名
        activityMember = ActivityMember()
        activityMember.activity_id = activity_id
        activityMember.user_id = userid
        ActivityMember().quit(activityMember)
        return jsonify({'code': 1})
    except Exception,e:
        current_app.logger.error(str(e))
        e_msg = 'act quit except '
        return jsonify({'code': 0, 'error': e_msg})

@login_required
@activity_controller.route('/events/mine',methods=['GET'])
def events_of_mine():
    '''
    活动列表：参加的、创建的
    :return:
    '''
    try:
       page = request.args.get('page',None)
       user_id = request.args.get('user_id','')

       act_list = ActivityDB.get_mine_activity_list(user_id,page)

       return jsonify({'code': 1,"events":model2dict(act_list)})
    except Exception,e:
        current_app.logger.error(str(e))
        return jsonify({'code': 0, 'error': ' events_of_mine exception '})

@login_required
@activity_controller.route('/events/<e_id>/cancel',methods=['POST'])
def events_cancel(e_id):
    '''
    活动列表：参加的、创建的
    :return:
    '''
    try:
       activity_id = int(e_id)
       user_id = request.args.get('user_id','')

       activity = ActivityDB.update_activity_status(activity_id,-1)

       return jsonify({'code': 1})
    except Exception,e:
        current_app.logger.error(str(e))
        return jsonify({'code': 0, 'error': ' events_cancel exception '})



@activity_controller.route('/events/club',methods=['GET'])
def events_of_club():
    '''
    获取俱乐部的所有活动
    :return:
    '''
    try:
        args = request.args
        current_app.logger.debug(str(args))
        page_size = int(args.get("page_size", 20))
        page_index = int(args.get("page_index", 1))
        club_id = int(args.get("club_id",0))

        act_list = ActivityDB.get_club_activity_list(club_id,page_size,page_index)

        return jsonify({'code': 1,"events":model2dict(act_list)})
    except Exception,e:
        current_app.logger.error(str(e))
        return jsonify({'code': 0, 'error': ' events_of_club exception '})


@activity_controller.route('/events/<e_id>/members', methods=['GET'])
def events_members(e_id):
    """

    """
    try:
        arr = request.args
        current_app.logger.debug(str(arr))
        event = ActivityDB.activity_by_id(int(e_id))
        user_id = int(arr.get("user_id",0))
        managers = []
        creator = UserDB.user_by_id(event.creator_id)
        managers.append(creator)
        # 完善成员列表
        #members = ActivityMemberDB.activity_members_by_act(e_id)
        members = UserDB.activity_user_list(int(e_id))
        return jsonify({'code': 1,"managers":model2dict(managers),"members": members})
    except Exception, e:
        current_app.logger.error(e)
        jsonify({'code': 0, 'error': ' events_members exception '})


