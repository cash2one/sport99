# coding=utf-8
__author__ = 'Van.zx'

from flask import Blueprint, request, redirect, render_template, current_app
import json
import time
import hashlib
from ..helpers.util_helper import get_user
from ..mredis import RedisClient
from ..mongo import UserDB
from ..wechat.outh2 import ApiConfig, WechatApi  # 负责微信页面登陆
# from wechat_sdk import WechatBasic
# from wechat_sdk.exceptions import ParseError


api = Blueprint('wx', __name__, url_prefix="/api/wx")


def _get_wechat():
    url = "http://" + current_app.config.get('DOMAIN')+"/api/wx/auth"
    # url = "http://" + current_app.config.get('DOMAIN') + '/api/wx/auth'
    api_config = ApiConfig(
        appid=current_app.config.get("WECHAT_APP_ID"),
        app_secret=current_app.config.get("WECHAT_APP_SECRET"),
        redirect_uri=url,
        noncestr=current_app.config.get("WECHAT_NONCE")
    )
    wechat = WechatApi(api_config)
    return wechat


@api.route('/get_tx_signature', methods=['GET', 'POST'])
def get_tx_signature():
    """
    微信JDK需要的签名
    """
    prefix = request.args.get('prefix', '')
    try:
        jsapi_token = RedisClient.get_wx_jsapi_ticket_from_cache()
        wechat = _get_wechat()
        if not jsapi_token:
            access_token_dict = wechat.get_credential()
            access_token = access_token_dict["access_token"]
            jsapi_token_dict = wechat.get_jsapi_ticket(access_token)
            jsapi_token = jsapi_token_dict["ticket"]
            jsapi_ticket_expires_in = jsapi_token_dict["expires_in"]

            RedisClient.set_wx_jsapi_ticket_from_cache(jsapi_token, jsapi_ticket_expires_in)


        timestamp = int(time.time())
        nonce = current_app.config.get("WECHAT_NONCE")
        url = "http://" + current_app.config.get('DOMAIN') + "/" + prefix
        print "+++", url

        signature = wechat.generate_jsapi_signature(jsapi_token, timestamp, url)

        r_d = {
            "code": 1,
            "app_id": current_app.config.get("WECHAT_APP_ID"),
            "timestamp": timestamp,
            "noncestr": nonce,
            "signature": signature,
            "url":url,
            'qiniu_bucket_domain': current_app.config.get("QINIU_BUCKET_DOMAIN")
        }
        print r_d
        return json.dumps(r_d)
    except TypeError, e:
        import traceback
        print traceback.format_exc()
        current_app.logger.error(e)
        return json.dumps({"code": 0})


@api.route('/server_verify', methods=['GET'])
def server_verify():
    """
    用于微信公众平台配置使用
    """
    try:
        print "GET--------------------"
        signature = request.args.get("signature")
        token = current_app.config.get("WECHAT_TOKEN")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")

        echo_str = request.args.get("echostr")

        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "%s%s%s" % tuple(tmp_list)
        hash_sha1 = hashlib.sha1(tmp_str)
        value = hash_sha1.hexdigest()

        if value == signature:
            return echo_str
        else:
            return "error"

    except Exception, e:
        current_app.logger.error(e)
        return "error"


@api.route('/server_verify', methods=['POST'])
def server_verify_post():
    """
    用于微信公众平台配置使用
    """
    try:
         print "POST----------------------------"
         print "request.data :" + str(request.data)
         return ""

    except Exception, e:
        current_app.logger.error(e)
        return ""


@api.route("/app_id", methods=['GET'])
def app_id():
    return json.dumps({"app_id": current_app.config.get("WECHAT_APP_ID")})

# @api.route('/receive_msg', methods=['GET', 'POST'])
# def receive_msg():
#     try:
#         wechat = WechatBasic(
#             token=current_app.config.get("WECHAT_TOKEN"),
#             appid=current_app.config.get("WECHAT_APP_ID"),
#             appsecret=current_app.config.get("WECHAT_APP_SECRET")
#         )
#
#         print request.data
#         # 解析本次请求的 XML 数据
#         try:
#             wechat.parse_data(data=request.data)
#         except ParseError:
#             return 'Invalid XML Data'
#
#         # 获取解析好的微信请求信息
#         message = wechat.get_message()
#         user_open_id = message.source
#         # 检查redis中是否存储了此用户，没有的话存储，生成token,设置cookie
#         # 有的话，检查是否有改变，改变的话设置新COOKIE
#
#         rep = wechat.response_text(content=U'收到')
#         resp = make_response(rep, 200)
#         resp.set_cookie('current_wx_user', user_open_id)
#         # content_type = "application/xml"
#         return resp
#     except TypeError, e:
#         current_app.logger.error(e)
#         return json.dumps({"code": 0})

# 微信授权登录
# 1、引导用户进入授权页面同意授权，获取code login()
# 2、通过code换取网页授权access_token（与基础支持中的access_token不同）
# 3、如果需要，开发者可以刷新网页授权access_token，避免过期
# 4、通过网页授权access_token和openid获取用户基本信息（支持UnionID机制）


@api.route("/auth", methods=['GET'])
def auth():
    try:
        code = request.args.get('code')
        # print code
        wechat = _get_wechat()
        # print wechat.__dict__
        open_id, access_token, refresh_token = wechat.code_to_access_token(code)
        #
        wechat.refresh_access_token(refresh_token)

        user_wx = wechat.get_user_info(access_token, open_id)
        print user_wx
        # 判断是否对此登录 每个用户通过id绑定
        user_id = RedisClient.get_openid_from_cache(open_id)
        print "**"
        if not user_id:
            print "*0*"
            user = UserDB.user_by_open_id(open_id)
            if user:
                user_id = user["id"]
                UserDB.upsert_user_wx_to_db(user_id, user_wx)
                print "*2*"
            else:
                print "*1*"
                user_id = RedisClient.new_user_id()

                user_id = int(user_id)
                # 修改数据库
                UserDB.upsert_user_wx_to_db(user_id, user_wx)
        user_id = int(user_id)
        # 缓存用户基本信息
        RedisClient.cache_user(user_id, json.dumps(get_user(user_id)))
        # 缓存openid到user_id的映射
        RedisClient.cache_openid(open_id, user_id)
        RedisClient.cache_token(access_token, user_id)
        location = "/#/success?user_id=%s&token=%s" % (user_id, access_token)
        print 'user_id:', user_id, 'token:', access_token, 'open_id:', open_id

        return redirect(location)
    except TypeError, e:
        return json.dumps({"code": 0})


@api.route("/login")
def login():
    """
    从前端直接跳转到微信授权页，此步骤可忽略
    """
    try:
        wechat = _get_wechat()
        url = wechat.url_for_code(scope="snsapi_userinfo", state=1)
        # 跳转微信服务器授权页面
        print '跳转微信服务器授权页面', url
        return redirect(url)

    except TypeError, e:
        # 如果登陆发生问题，打印日志
        import traceback
        current_app.logger.error(e)
        return render_template("wechat_error.html")


@api.route("/create_menu", methods=['GET'])
def set_menu():
    #  https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN
    return "ok"


@api.route("/delete_menu", methods=['GET'])
def delete_menu():

    return "ok"


@api.route("/is_token_expired", methods=['GET', 'POST'])
def is_token_expired():
    # 验证我们的token是否过期
    # 以及微信是否过期?
    access_token = request.args.get("token")
    user_id = request.args.get("user_id")
    print "is_token_expired:", (RedisClient.check_token(access_token, user_id))
    if RedisClient.check_token(access_token, user_id):  # 用户登录，未过期
        return json.dumps({"code": 0})
    else:
        return json.dumps({"code": 1})