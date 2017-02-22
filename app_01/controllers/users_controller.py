# -*- coding:utf-8 -*-
__author__ = 'Van'
from flask import request, Blueprint, current_app, jsonify
from ..utils import model2dict
from ..mongo import UserDB, QQBindCodeDB, ClusterDB
import json

api = Blueprint('users_controller', __name__, url_prefix='')


@api.route('/users/show/<u_id>', methods=['GET'])
def user_show(u_id):
    try:
        user_dict = UserDB.mine_info_from_db_by_user_id(int(u_id))

        user = user_dict
        if not user:
            return json.dumps(model2dict({"code": 1, "user": {}}))
        if "nickname" in user_dict:
            user["nickname"] = user_dict["nickname"]
        else:
            if "wechat" in user_dict:
                user["nickname"] = user_dict["wechat"]["nickname"]

        if "head_img_url" in user_dict:
            user["head_img_url"] = user_dict["head_img_url"]
        else:
            if "wechat" in user_dict:
                user["head_img_url"] = user_dict["wechat"]["headimgurl"]
        if "sex" in user_dict:
            if user_dict["sex"] == "男":
               user["sex"] = 1
            else:
               user["sex"] = 0
        else:
            if "wechat" in user_dict:
                user["sex"] = user_dict["wechat"]["sex"]

        r_d = {
            "code": 1,
            "user": user
        }
        return json.dumps(model2dict(r_d))
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})


@api.route('/users/update/<u_id>', methods=['POST'])
def user_update(u_id):
    # print "request.args:=", request.args
    print('---------key values begin--------------------------')
    for key in request.args:
        print key, ': ', type(request.args[key]), request.args[key]
    print('-----------key values end------------------------')
    try:
        u_id = int(u_id)
        # filed_enable = ["name", "sex", "head_img_url", "height", "weight", "mobile", "nickname"]
        if "qq" in request.args:
            qq = request.args["qq"]
            user_in_db = UserDB.user_by_id_from_db(u_id)
            if not user_in_db:
                raise Exception("not found this user: u_id:=", u_id)
            if user_in_db.get("qq") and user_in_db.get("qq") == qq:
                # user.update({key: request.args[key]})
                QQBindCodeDB.remove_qq_bind_code_by_user_id(u_id)
            else:
                user_by_qq = UserDB.user_by_qq_from_user_db(qq)
                if user_by_qq and user_by_qq.get("wechat"):
                    raise Exception("qq has bind, please try another qq number, qq:=" + qq)
                QQBindCodeDB.upsert_qq_bind_code_by_id(u_id, qq, "99")

        # if "id" in request.args and int(request.args['id']) != u_id:  # just for check user id not found bug
        #     raise Exception("args has id, and != u_id, just for check user not found bug")
        # if isinstance(request.args.get("wechat"), str):
        #     raise Exception("wechat is string, in user_update, error, just for debug,")

        user = {}
        for key in request.args:
            if key == "qq":
                continue
            if key == "wechat":
                user.update({key: json.loads(request.args[key])})
                continue
            # if key in filed_enable:
            user.update({key: request.args[key]})
        print user
        UserDB.update_user_to_db(u_id, user)
        return jsonify({"code": 1})

    except Exception, e:
        current_app.logger.error(e.message)
        return jsonify({"code": 0})


@api.route('/users/clusters', methods=['GET'])
def user_clusters():
    try:
        print "="*50
        for k in request.args:
            print k, request.args.get(k)
        print "+"*50
        user_id = int(request.args.get("user_id"))
        user = UserDB.mine_info_from_db_by_user_id(user_id)
        if not user:
            raise Exception("user not found, user_id:=%r" % user_id)

        if "qq" in user:
            qq_bind = True
            clusters = ClusterDB.get_admin_clusters_by_qq_from_cluster_db(user["qq"])
            clusters_copy = []
            if clusters:
                for cluster in clusters:
                    clusters_copy.append(cluster)
            return json.dumps({"code": 1, "clusters": clusters_copy, "qq_bind": qq_bind, "qq": user["qq"]})
        else:
            # clusters = []
            clusters_copy = []
            # current_app.logger.info("clusters_copy:=", clusters_copy)
            return json.dumps({"code": 1, "clusters": clusters_copy})
    except Exception, e:
        current_app.logger.error(e.message)
        return json.dumps({"code": 0})