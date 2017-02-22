# coding=utf-8
# _author_ = jiangzhuang

import time,threadpool
from flask import Blueprint, current_app, request,redirect, jsonify,session
from app.utils.WxUtil import WxUtil
from weixin.wxapi import WeixinHelper, ObjectDict
from app.models import WeixinUser, WeixinMenu,OauthUrl,User
from flask.ext.login import login_user,current_user
from app.utils.common import urlParams,randomStr
from .. import db
from .. import mypool


weixin_controller = Blueprint('weixin_controller', __name__, url_prefix='/api/wx')


# 微信<->服务器 核心消息处理器
@weixin_controller.route('/index', methods=['GET', 'POST'])
def index():
    try:
        for key in request.form:
            current_app.logger.debug(key + ":" + request.form.get(key))
        # 微信消息处理
        if request.method == "POST":
            current_app.logger.debug("POST")
            current_app.logger.debug(request.data)
            bodyXml = request.data
            xml = ObjectDict(WeixinHelper.xmlToArray(bodyXml))

            # TODO 加密消息解密处理

            # 明文处理
            msgtype = xml.MsgType
            if msgtype == "event":
                key = xml.Event
                if key == 'subscribe':  # 关注
                    requests = threadpool.makeRequests(WxUtil.subscribe, [xml])
                    [mypool.putRequest(req) for req in requests]
                    #WxUtil.subscribe(xml)
                elif key == 'unsubscribe': # 取消关注
                    requests = threadpool.makeRequests(WxUtil.unsubscribe, [xml])
                    [mypool.putRequest(req) for req in requests]
                    #WxUtil.unsubscribe(xml)
                else:
                    raise Exception(' unhandle event ' + key)
            elif msgtype == "text":
                key = "all"
                current_app.logger.debug(' recive the content : '+ xml.Content)
            else:
                raise Exception(' unhandle msgtype ' + msgtype)

            return ''

            # 用于微信绑定验证
        else:
            current_app.logger.debug("GET")
            signature = request.args.get('signature')
            timestamp = request.args.get('timestamp')
            nonce = request.args.get('nonce')
            echostr = request.args.get('echostr')
            # 微信消息验证
            if WeixinHelper.checkSignature(signature, timestamp, nonce):
                return echostr
            else:
                raise Exception('the weixin checkSignature error ')
    except Exception, e:
        current_app.logger.error(str(e))
        return ''
'''
@weixin_controller.route('/oauth')
def oauth():
    current_app.logger.debug('----------------------------oauth :'+request.method)
    try:
        state = request.args.get('state','')  # url标识
        code = request.args.get('code','')  # 授权code
        current_app.logger.debug('授权url 返回参数 ： state = '+state+';code = '+code )

        oauthUrl = db.session.query(OauthUrl).filter(OauthUrl.id == state).first()
        redirctUrl = oauthUrl.url
        # 授权获取信息
        openid =  WxUtil.getOpenId(code)
        if openid:
            # 判断用户是否存在
            user = db.session.query(User).filter(User.openid == openid).first()
            if user :
                current_app.logger.debug('微信用户'+openid+'已经存在')
                login_user(user)
                session['login_user_id'] = user.id
                return redirect(urlParams(redirctUrl,{'id':user.id}))
            else:
                current_app.logger.debug('微信用户'+openid+'尚不存在')
                # 新增用户
                userinfo = WxUtil.getUserInfo(openid)

                weixinUser = WeixinUser()
                weixinUser.openid = userinfo.get('openid')
                weixinUser.nickname = userinfo.get('nickname')
                weixinUser.sex = userinfo.get('sex')
                weixinUser.pic = userinfo.get('headimgurl')
                weixinUser.create_time = str(int(time.time()) * 1000)
                weixinUser.subscribe = userinfo.get('subscribe')
                weixinUser.update_time = str(int(time.time()) * 1000)
                WeixinUser().add(weixinUser)
                # 判断是否成功
                user = db.session.query(User).filter(User.openid == openid).first()
                if user :
                    login_user(user,remember=True)
                    return redirect(urlParams(redirctUrl,{'id':user.id}))
                else:
                    return ''

        else:
            return redirect(redirctUrl)

    except Exception,e:
        current_app.logger.error(str(e))
        return ''
'''

@weixin_controller.route('/auth',methods=['GET'])
def oauth():
    try:
        code = request.args.get('code','')  # 授权code

        # 授权获取信息
        openid =  WxUtil.getOpenId(code)
        if openid:
            # 判断用户是否存在
            user = db.session.query(User).filter(User.openid == openid).first()
            if user :
                current_app.logger.debug('微信用户'+openid+'已经存在')
                login_user(user)
                # session['login_user_id'] = user.id
                return jsonify({'code': 1 ,'user_id': user.id, 'open_id': user.openid})
            else:
                current_app.logger.debug('微信用户'+openid+'尚不存在')
                # 新增用户
                userinfo = WxUtil.getUserInfo(openid)

                weixinUser = WeixinUser()
                weixinUser.openid = userinfo.get('openid')
                weixinUser.nickname = userinfo.get('nickname')
                weixinUser.sex = userinfo.get('sex')
                weixinUser.pic = userinfo.get('headimgurl')
                weixinUser.create_time = str(int(time.time()) * 1000)
                weixinUser.subscribe = userinfo.get('subscribe')
                weixinUser.update_time = str(int(time.time()) * 1000)
                WeixinUser().add(weixinUser)
                # 判断是否成功
                user = db.session.query(User).filter(User.openid == openid).first()
                if user :
                    login_user(user,remember=True)
                    return jsonify({'code': 1 ,'user_id': user.id, 'open_id': user.openid})
                else:
                    return jsonify({'code': 0})

        else:
            return jsonify({'code': 0})

    except Exception,e:
        current_app.logger.error(str(e))
        return jsonify({'code': 0})

@weixin_controller.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated():
        return jsonify({'code': 1})

    user_agent = request.headers['User-Agent']
    current_app.logger.debug('user_agent :' + user_agent)
    user_id = request.args.get('id')
    if user_id:
       user = User().getUserById(user_id)
       if user:
          login_user(user)
          # session['login_user_id'] = user.id
          return jsonify({'code': 1})
       else:
          return jsonify({'code': 0,'error':' error user_id '})

    #判断是否微信客户端
    if 'micromessenger' in user_agent:
        oauthurl = WxUtil.isOauth()
        current_app.logger.debug('oauth url :' + oauthurl)
        return redirect(oauthurl)
    #return jsonify({'code': 1,'result':{oauthurl}})
    #else :
    return jsonify({'code': 0})

@weixin_controller.route('/createMenu', methods=['GET'])
def createMenu():
    json = '{"button": [' \
       '{"name": "去运动","type": "view","url": "http://test.yundong99.net/#/events"},' \
       '{"name": "俱乐部","sub_button": [' \
           '{"type": "view","name": "发布活动","url": "http://test.yundong99.net/#/events/create_step1"},' \
           '{"type": "view","name": "创建俱乐部","url": "http://test.yundong99.net/#/clubs/create_step1"}]' \
       '},' \
       '{"name": "个人信息","sub_button": [' \
           '{"type": "view","name": "我的俱乐部","url": "http://test.yundong99.net/#/clubs"},' \
           '{"type": "view","name": "我的活动","url": "http://test.yundong99.net/#/mine_events"},' \
           '{"type": "view","name": "设置","url": "http://test.yundong99.net/#/info_set"}]' \
       '}]}'
    return WxUtil.createMenu(json)

@weixin_controller.route('/get_tx_signature', methods=['GET'])
def get_tx_signature():
    """
    微信js调用参数
    """
    prefix = request.args.get('prefix', '')
    try:
        url = request.url
        jsSign = WxUtil.getJsSign(url)
        appid = WxUtil.getAppid()
        j_j = {
            "code": 1,
            "app_id": appid,
            "timestamp": jsSign['timestamp'],
            "noncestr": jsSign['nonceStr'],
            "signature": jsSign['signature']
        }
        return jsonify(j_j)
    except Exception,e:
        current_app.logger.error(str(e))
        return jsonify({"code": 0})

@weixin_controller.route("/app_id", methods=['GET'])
def app_id():
    appid = WxUtil.getAppid()
    current_app.logger.debug("app_id : "+ appid)
    return jsonify({"app_id": appid})


class Reply(object):
    """消息回复"""

    def __init__(self, xml):
        self.xml = xml
        self.xml["CreateTime"] = int(time.time())

    def textResponse(self, data):
        """文本消息回复"""
        self.xml["Content"] = data
        return _TEXT.format(**self.xml)

    def newsKey(self, ld):
        """图文消息列表转换为字典"""
        return dict(zip(["Title", "Description", "PicUrl", "Url"], ld))

    def newsResponse(self, data):
        """图文消息"""
        count = len(data)
        if count > 10:
            raise Exception("ArticleCount greater then 10")
        self.xml["Items"] = "".join([_ITEM.format(**d) for d in data])
        self.xml["ArticleCount"] = count
        return _NEWS.format(**self.xml)


_TEXT = """\
    <xml>
    <ToUserName><![CDATA[{FromUserName}]]></ToUserName>
    <FromUserName><![CDATA[{ToUserName}]]></FromUserName>
    <CreateTime>{CreateTime}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{Content}]]></Content>
    </xml>"""

_ITEM = """\
    <item>
    <Title><![CDATA[{Title}]]></Title>
    <Description><![CDATA[{Description}]]></Description>
    <PicUrl><![CDATA[{PicUrl}]]></PicUrl>
    <Url><![CDATA[{Url}]]></Url>
    </item>"""

_NEWS = """\
    <xml>
    <ToUserName><![CDATA[{FromUserName}]]></ToUserName>
    <FromUserName><![CDATA[{ToUserName}]]></FromUserName>
    <CreateTime>{CreateTime}</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>{ArticleCount}</ArticleCount>
    <Articles>
    {Items}
    </Articles>
    </xml>"""



