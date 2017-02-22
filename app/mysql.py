# coding=utf-8
# _author_ = jiangzhuang

from app import db
from app.utils.MyException import SQLException
from app.models import User,TokenTemp,WeixinUser,Area,ActivityLevel,ActivityCategory,\
    ActivityMember,Activity,CycleActivity,Cluster,ClusterMember,Club,ClubMember,Venue,\
    QQUser,QQBindCode
from app.utils.common import sync,getSign
from sqlalchemy import or_
from app.utils.common import model2dict
import threading,time,datetime
lock = threading.Lock()
class VenueDB():
    def __init__(self):
        pass

    @staticmethod
    def add_venue(venue):
        '''
        新增地点
        :param venue:
        :return:
        '''
        try:
            db.session.add(venue)
        except Exception,e:
            raise SQLException("add venue")

    @staticmethod
    def venue_by_id(venue_id):
        try:
            return db.session.query(Venue).filter(Venue.id == venue_id).first()
        except Exception,e:
            raise SQLException("venue_by_id")

    @staticmethod
    def venue_by_coordinate(lng,lat):
        '''
        通过地图坐标判断是否存在该地点
        :param lng: 经度
        :param lat: 纬度
        :return:
        '''
        try:
            return db.session.query(Venue).filter(Venue.coordinate_lat == lat,Venue.coordinate_lng == lng).first()
        except Exception,e:
            raise SQLException("venue_by_coordinate")
            return
class UserDB():
    def __init__(self):
        pass

    @staticmethod
    def add_user(user):
        '''
        新增用户
        :param user:
        :return:
        '''
        try:
            db.session.add(user)
            return user
        except Exception,e:
            raise SQLException("add user")
            return
    @staticmethod
    def user_by_id(user_id):
        '''
        通过id查找用户
        :param user_id:用户id
        :return:
        '''
        try:
            return db.session.query(User).filter(User.id == user_id).first()
        except Exception,e:
            raise SQLException("user_by_id")
            return
    @staticmethod
    def update_user_data(user_id,user_arr):
        '''
        更新用户资料
        :return:
        '''
        try:
            user_db = db.session.query(User).filter(User.id == user_id).first()
            for key in user_arr:
                if key == "qq":
                   new_qq = user_arr[key]
                   if not new_qq:
                      userQq = db.session.query(User).fiter(User.qq == user_db.qq,User.status == -1).first()
                      userQq.status = 0
                      # qq置空
                      user_db.qq = ''
                      db.session.add(userQq)           # session
                      db.session.add(user_db)           # session
                      db.session.commit()
                   elif new_qq != user_db.qq:
                      qqUser = db.session.query(QQUser).fiter(QQUser.qq == new_qq).first()
                      if not qqUser:
                         raise Exception('no this qq')
                      userQq = db.session.query(User).fiter(User.qq == new_qq,User.openid !='').first()
                      if userQq:
                         raise Exception('this qq has be bind')

                      qqBindCode = QQBindCode()
                      qqBindCode.qq = new_qq
                      qqBindCode.uid = user_db.id
                      qqBindCode.create_time = str(int(time.time()))
                      qqBindCode.code = 'BD'
                      db.session.add(qqBindCode)           # session

                      db.session.commit()
                else:
                   user_db.key = user_arr[key]
                   db.session.add(user_db)
                   db.session.commit()
                   return user_db
        except Exception,e:
            raise SQLException("update_user_data")
            return


    @staticmethod
    def update_user_status(user_id,status):
        '''
        更新用户状态
        :param user_id:用户id,status：
        :return:  True False
        '''
        try:
           user_db = db.session.query(User).filter(User.id == user_id).first()
           if user_db:
              user_db.stauts = status
              db.session.add(user_db)
              return True
           return False
        except Exception,e:
            raise SQLException("update_user_status")
            return False

    @staticmethod
    def activity_user_list(activity_id):
        try:
           user_list = db.session.query(User).join(ActivityMember,ActivityMember.user_id == User.id).\
               filter(ActivityMember.activity_id == activity_id,ActivityMember.status == 0).all()

           return user_list
        except Exception,e:
            raise SQLException("activity_user_list")
            return

class TokenTempDB():
    def __init__(self):
        pass

    @staticmethod
    def update_token(tokenTemp):
        '''
        更新token
        :param tokenTemp:
        :return:
        '''
        try:
            tokenTemp_db = db.session.query(TokenTemp).filter(TokenTemp.name).first()
            if tokenTemp_db:
                tokenTemp_db.token = tokenTemp.token
                tokenTemp_db.update_time = tokenTemp.update_time
                db.session.add(tokenTemp_db)
            else:
                db.session.add(tokenTemp)
        except Exception,e:
            raise SQLException("update_token")


class WeixinUserDB():
    def __init__(self):
        pass

    @staticmethod
    def add_weixin_user(weixinUser):
        '''
        新增微信用户
        :param weixinUser:
        :return:
        '''
        try:
            db.session.add(weixinUser)
            user = User()
            user.sex = weixinUser.sex
            user.head_url = weixinUser.pic
            user.nick = weixinUser.nickname
            user.openid = weixinUser.openid
            db.session.add(user)
        except Exception,e:
            db.session.rollback()
            raise SQLException("add_weixin_user")


    @staticmethod
    def update_weixin_user(weixinUser):
        try:
            weixinUser_db = db.session.query(WeixinUser).filter(WeixinUser.openid == weixinUser.openid).first()
            weixinUser_db.nickname = weixinUser.nickname
            weixinUser_db.sex = weixinUser.sex
            weixinUser_db.pic = weixinUser.pic
            weixinUser_db.coordinate_lng = weixinUser.coordinate_lng
            weixinUser_db.coordinate_lat = weixinUser.coordinate_lat
            weixinUser_db.update_time = weixinUser.update_time
            db.session.add(weixinUser_db)
        except Exception,e:
            raise SQLException("update_weixin_user")

class AreaDB():
    def __init__(self):
        pass

    @staticmethod
    def list_area():
        '''
        获取城市列表
        :return:
        '''
        try:
            area_arr = db.session.query(Area).all()
            return area_arr
        except Exception,e:
            raise SQLException("list_area")


class ActivityLevelDB():
    def __init__(self):
        pass

    @staticmethod
    def list_activity_level(category):
        '''
        获取活动等级列表
        :param category: 活动类别
        :return:
        '''
        try:
            activity_level_arr = db.session.query(ActivityLevel).filter(ActivityLevel.category == category).all()
            return activity_level_arr
        except Exception,e:
            raise SQLException("list_activity_level")


class ActivityCategoryDB():
    def __init__(self):
        pass

    @staticmethod
    def list_activity_category():
        '''
        获取活动类别列表
        :return:
        '''
        try:
            activity_category_arr = db.session.query(ActivityCategory).all()
            return activity_category_arr
        except Exception,e:
            raise SQLException("list_activity_category")

class ActivityMemberDB():
    def __init__(self):
        pass


    @staticmethod
    @sync(lock)
    def activity_member_join(activityMember):
        '''
        参加活动
        :return:
        '''
        try:
            db.session.add(activityMember)
            activity = db.session.query(Activity).filter(Activity.id == activityMember.activity_id).first()
            # 判断报名人数
            if activity.member_count_limit - activity.member_count < activityMember.num:
                raise Exception('the num is too big')
            activity.member_count = activity.member_count + activityMember.num
            db.session.add(activity)
            db.session.commit()
        except Exception, e:
            db.session.rollback()
            raise SQLException(e)
        return activityMember

    @staticmethod
    @sync(lock)
    def activity_member_quit(activityMember):
        '''
        取消报名
        :return:
        '''
        try:
            activity = db.session.query(Activity).filter(Activity.id == activityMember.activity_id,
                                                         Activity.status == 0).first()

            activityMemberOld = db.session.query(ActivityMember).filter(
                ActivityMember.user_id == activityMember.user_id,
                ActivityMember.activity_id == activityMember.activity_id, ActivityMember.status == 0).first()

            activity.member_count = int(activity.member_count - activityMemberOld.num)
            db.session.add(activity)

            activityMemberOld.status = -1
            db.session.add(activityMemberOld)
            db.session.commit()
        except Exception, e:
            db.session.rollback()
            raise SQLException(e)
        return activityMember

    @staticmethod
    def activity_members_by_act(activity_id):
        try:
            return db.session.query(ActivityMember).filter(ActivityMember.activity_id == activity_id,ActivityMember.status == 0).all()
        except Exception,e:
            raise SQLException(e)
            return

class ActivityDB():
    def __init__(self):
        pass

    @staticmethod
    def init_activity(user_id):
        '''
        初始化活动
        :param activity:
        :return:
        '''
        try:
            activity = Activity(None)
            # 设定初始化参数 ------begin
            activity.status = 0
            activity.member_count = 0
            activity.creator_id = user_id
            db.session.add(activity)
            db.session.commit()
        except Exception, e:
            db.session.rollback()
            raise SQLException(e)
        return activity


    @staticmethod
    def update_activity(activity):
        '''
        更新活动
        :param activity:
        :return:
        '''
        try:
            activity_db = db.session.query(Activity).filter(Activity.id == activity.id,Activity.status == 0).first()
            if activity_db:
               activity_db.category = activity.category
               activity_db.name = activity.name
               activity_db.start_time = activity.start_time
               activity_db.end_time = activity.end_time
               activity_db.venue_id = activity.venue_id
               activity_db.fee = activity.fee
               activity_db.is_aa = activity.is_aa
               activity_db.member_count_limit = activity.member_count_limit
               activity_db.place_num = activity.place_num
               activity_db.mobile = activity.mobile
               activity_db.week = activity.week
               db.session.add(activity_db)
               db.session.commit()
               return activity_db
        except Exception, e:
            db.session.rollback()
            raise SQLException(e)
        return

    @staticmethod
    def update_activity_status(activity_id,status ):
        '''
        # 更新活动状态
        :param activity_id:
        :param status:
        :return:
        '''
        try:
            activity_db = db.session.query(Activity).filter(Activity.id == activity_id).first()
            if activity_db:
               activity_db.status = status
               db.session.add(activity_db)
        except Exception, e:
            db.session.rollback()
            raise SQLException(e)
        return activity_db


    @staticmethod
    def activity_by_id(activity_id):
        try:
            activity = db.session.query(Activity).filter(Activity.id == activity_id).first()
            return activity
        except Exception,e:
           raise SQLException(e)
           return


    @staticmethod
    def get_activity_sign(cluster_ids):
        '''
        通过qq群号获取报名标示
        :param cluster_ids:
        :return:
        '''
        try:
            # 一星期后
            min_time = int(time.mktime((datetime.datetime.now()
                                        + datetime.timedelta(days=-7)).timetuple())*1000)  # 一星期前
            # 一星期前
            max_time = int(time.mktime((datetime.datetime.now()
                                            + datetime.timedelta(days=7)).timetuple())*1000)

            query_sql = "select a.sign from activities a " \
                            "left join activity_clusters c on c.activity_id = a.id " \
                            "where a.`status` = '0' and c.cluster_id in (" + cluster_ids + ") " \
                            "and a.start_time > " +min_time + " and a.start_time < " + max_time
            signList = db.session.excute(query_sql)

            sign = getSign(signList)
            return sign
        except Exception,e:
            raise SQLException(e)
            return

    @staticmethod
    def get_mine_activity_list(user_id,page):
        try:
            if page == "published":
               act_list = db.session.query(Activity).filter(Activity.creator_id == user_id).all()
               for act in act_list:
                   venue = db.session.query(Venue).filter(Venue.id == act.venue_id).first()
                   if venue:
                        act.venue = venue
               return act_list
            elif page == "joined":
               # 只获取已经报名的
               act_list = db.session.query(Activity).join(ActivityMember,ActivityMember.activity_id == Activity.id).\
                  filter(ActivityMember.user_id == user_id,ActivityMember.status == 0).all()
               for act in act_list:
                   venue = db.session.query(Venue).filter(Venue.id == act.venue_id).first()
                   if venue:
                        act.venue = venue
               return act_list
            else:
               act_list1 = db.session.query(Activity).filter(Activity.creator_id == user_id).all()

               act_list2 = db.session.query(Activity).join(ActivityMember,ActivityMember.activity_id == Activity.id).\
                   filter(ActivityMember.user_id == user_id,ActivityMember.status == 0).all()

            return act_list2.extends(act_list1)

        except Exception,e:
            raise SQLException(e)
            return ''

    @staticmethod
    def get_activity_list(act_filter,page_size,page_index):
        try:
            if "by_distance" in act_filter and act_filter["act_filter"]:
                querysql = 'select a.id as id,a.start_time as start_time,a.end_time as end_time ,a.venue_id as venue_id,a.member_count_limit as member_count_limit,a.member_count as member_count,' \
                           'a.`status` as `status`,c.`name` as club_name,c.head_url as club_head_url ,SUM(POWER(ABS(v.coordinate_lng - w.coordinate_lng),2),POWER(ABS(v.coordinate_lat - w.coordinate_lat),2)) as distance ' \
                           'from activities a LEFT JOIN clubs c on a.club_id = c.id ' \
                           'left join venues v on a.venue_id = v.id left join weixin_user w on a.id = w.uid where a.`status` = 1 order by distance asc'
            elif "by_default" in act_filter and act_filter["by_default"]:
                return
            else:
                 querysql = 'select a.id as id,a.start_time as start_time,a.end_time as end_time ,a.venue_id as venue_id,a.member_count_limit as member_count_limit,a.member_count as member_count,' \
                   'a.`status` as `status`,c.`name` as club_name,c.head_url as club_head_url,a.category as category ' \
                   'from activities a LEFT JOIN clubs c on a.club_id = c.id where a.`status` in(0,1) '
                 '''
                 if "category" in act_filter and act_filter["category"]:
                    querysql = querysql + "and a.category = '" + act_filter["category"] + "'"
                 if "week" in act_filter and act_filter["week"]:
                    querysql = querysql + "and a.week = '" + act_filter["week"] + "'"
                 '''

                 print "querysql:",querysql
                 act_arr_list = db.session.execute(querysql)

                 act_list = []

                 if act_arr_list:
                     for act_arr in act_arr_list:
                         act = Activity(None)
                         act.id = act_arr[0]
                         act.start_time = act_arr[1]
                         act.end_time = act_arr[2]
                         act.venue_id = act_arr[3]
                         if act.venue_id:
                             venue = db.session.query(Venue).filter(Venue.id == act.venue_id).first()
                         act.member_count_limit = act_arr[4]
                         act.member_count = act_arr[5]
                         act.status = act_arr[6]
                         club = Club(None)
                         club.name = act_arr[7]
                         club.head_url = act_arr[8]
                         act.category = act_arr[9]

                         act.venue = venue
                         act.club = club

                         act_list.append(act)
                 return act_list
        except Exception,e:
            raise SQLException(e)
            return

    @staticmethod
    def get_club_activity_list(club_id,page_size,page_index):
        try:
            querysql = 'select a.id as id,a.start_time as start_time,a.end_time as end_time ,a.venue_id as venue_id,a.member_count_limit as member_count_limit,a.member_count as member_count,' \
                   'a.`status` as `status`,c.`name` as club_name,c.head_url as club_head_url,a.category as category ' \
                   'from activities a LEFT JOIN clubs c on a.club_id = c.id where a.`status` in(0,1) '
            querysql = querysql + "and a.club_id = '" +str(club_id)  + "'"
            act_arr_list = db.session.execute(querysql)

            act_list = []

            if act_arr_list:
               for act_arr in act_arr_list:
                 act = Activity(None)
                 act.id = act_arr[0]
                 act.start_time = act_arr[1]
                 act.end_time = act_arr[2]
                 act.venue_id = act_arr[3]
                 if act.venue_id:
                     venue = db.session.query(Venue).filter(Venue.id == act.venue_id).first()
                 act.member_count_limit = act_arr[4]
                 act.member_count = act_arr[5]
                 act.status = act_arr[6]
                 club = Club(None)
                 club.name = act_arr[7]
                 club.head_url = act_arr[8]
                 act.category = act_arr[9]

                 act.venue = venue
                 act.club = club

                 act_list.append(act)
            return act_list
        except Exception,e:
            raise SQLException(e)
            return


class CycleActivityDB():
     def __init__(self):
        pass

     @staticmethod
     def add(cycleActivity):
        '''
        新建活动
        :param cycleActivity:
        :return:
        '''
        try:
            db.session.add(cycleActivity)
            return cycleActivity
        except Exception, e:
            db.session.rollback()
            raise SQLException(e)
            return

     @staticmethod
     def update(cycleActivity):
        '''
        更新活动
        :param cycleActivity:
        :return:
        '''
        try:
            cycleActivity_db = db.session.query(CycleActivity).filter(CycleActivity.id == cycleActivity.id).first()
            if cycleActivity_db:
                cycleActivity_db.category = cycleActivity.category
                cycleActivity_db.name = cycleActivity.name
                cycleActivity_db.start_time = cycleActivity.start_time
                cycleActivity_db.end_time = cycleActivity.end_time
                cycleActivity_db.venue_id = cycleActivity.venue_id
                cycleActivity_db.fee = cycleActivity.fee
                cycleActivity_db.is_aa = cycleActivity.is_aa
                cycleActivity_db.member_count_limit = cycleActivity.member_count_limit
                cycleActivity_db.place_num = cycleActivity.place_num
                cycleActivity_db.mobile = cycleActivity.mobile
                cycleActivity_db.week = cycleActivity.week
                db.session.add(cycleActivity_db)
                return cycleActivity_db
        except Exception, e:
            db.session.rollback()
            raise SQLException(e)
            return


class ClusterDB():
     def __init__(self):
        pass

     @staticmethod
     def list_cluster_by_user(qq):
        cluster_arr = db.session.query(Cluster).join(ClusterMember,ClusterMember.external_id == Cluster.external_id)\
                     .filter(Cluster.creator_qq == qq)\
                     .filter(or_(ClusterMember.is_admin == 0)).all()
        return cluster_arr


class ClubDB():
     def __init__(self):
        pass

     @staticmethod
     def club_by_user(user_id):
         '''
         查询创建的俱乐部
         :param user_id:
         :return:
         '''
         club = db.session.query(Club).filter(Club.creator_id == user_id).first()
         return club

     @staticmethod
     def clubs_by_user(user_id):
         club = db.session.query(Club).join(ClubMember,ClubMember.club_id == Club.id)\
             .filter(ClubMember.user_id == user_id).all()

     @staticmethod
     def add_club(club):
         try:
             db.session.add(club)
             db.session.commit()
         except Exception,e:
             raise SQLException(e)
             return

     @staticmethod
     def club_by_id(club_id):
         try:
             club = db.session.query(Club).filter(Club.id == club_id).first()
             return club
         except Exception,e:
             raise SQLException(e)
             return


class ClubMembersDB():
     def __init__(self):
        pass


     @staticmethod
     def members_of_club(club_id):
         try:
             members = db.session.query(User).join(ClubMember,ClubMember.user_id == User.id).\
                 filter(ClubMember.club_id == club_id).all()
             return members
         except Exception,e:
             raise SQLException(e)
             return