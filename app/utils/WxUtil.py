# coding=utf-8
# _author_ = jiangzhuang
from app import db_session
from weixin.wxapi import WeixinHelper
from app.models import TokenTemp, WeixinUser,User,OauthUrl
from flask import request, session, redirect, current_app
import time,json
from app.utils.common import randomStr

# 微信接口调用封装工具
class WxUtil(object):
    # 获取access_token
    @classmethod
    def getAccessToken(cls):
        '''
        从数据库中取
           有  直接返回
           没有  调用wxapi接口从微信服务器获取,并保存到数据库
        '''
        # 获取当前时间戳 单位：秒
        dt = int(time.time()) * 1000 - 110 * 60 * 1000
        tokenTemp = db_session.query(TokenTemp).filter(TokenTemp.name == 'access_token',
                                                       TokenTemp.update_time > str(dt)).first()
        if tokenTemp != None:
            access_token = tokenTemp.token
        else:
            accessTokenObj = WeixinHelper.getAccessToken()
            access_token = accessTokenObj['access_token']
            # 更新到数据库
            db_session.query(TokenTemp).filter(TokenTemp.name=='access_token').update({'token': access_token, 'update_time': str(int(time.time())*1000)})
            db_session.commit()

        return access_token

    # 获取js_token
    @classmethod
    def getJsToken(cls):
        '''
        从数据库中取
           有  直接返回
           没有  调用wxapi接口从微信服务器获取 ,并保存到数据库
        '''
        dt = int(time.time()) * 1000 - 110 * 60 * 1000
        tokenTemp = db_session.query(TokenTemp).filter(TokenTemp.name == 'js_token',
                                                       TokenTemp.update_time > str(dt)).first()
        js_token = ''
        if tokenTemp != None:
            js_token = tokenTemp.token
        else:
            access_token = cls.getAccessToken()
            js_token = WeixinHelper.getJsapiTicket(access_token)
            # 更新到数据库
            db_session.query(TokenTemp).filter(TokenTemp.name=='js_token').update({'token': access_token, 'update_time': str(int(time.time())*1000)})
            db_session.commit()
        return js_token

    # 获取微信用户资料
    @classmethod
    def getUserInfo(cls, openid):

        access_token = cls.getAccessToken()
        userInfo = WeixinHelper.getUserInfo(access_token, openid)
        current_app.logger.debug('getUserInfo userInfo : ' + str(cls.byteify(userInfo)))
        return cls.byteify(userInfo)

    # 获取网页授权access_token
    @classmethod
    def getAccessTokenByCode(cls):
        '''
        从数据库中取
           有  直接返回
           没有  调用wxapi接口从微信服务器获取 ,并保存到数据库
        '''
        dt = int(time.time()) * 1000 - 110 * 60 * 1000
        tokenTemp = db_session.query(TokenTemp).filter(TokenTemp.name == 'flush_token',
                                                       TokenTemp.update_time > str(dt)).first()
        flush_token = ''
        if tokenTemp != None:
            flush_token = tokenTemp.token
        else:
            access_token = cls.getAccessToken()
            flushTokenObj = WeixinHelper.getAccessTokenByCode(access_token)
            if 'access_token' in flushTokenObj:
                flush_token = flushTokenObj['access_token']
                flushTokenObj = WeixinHelper.refreshAccessToken(flush_token)
                if 'access_token' in flushTokenObj:
                    flush_token = flushTokenObj['access_token']
                    # 更新到数据库
                    db_session.query(TokenTemp).filter(TokenTemp.name=='flush_token').update({'token': flush_token, 'update_time': str(int(time.time())*1000)})
                    db_session.commit()
        return flush_token

    # 网页授权获取微信id
    @classmethod
    def getOpenId(cls,code):
        flushTokenObj = WeixinHelper.getAccessTokenByCode(code)
        current_app.logger.debug('授权获取到返回信息：' + str(flushTokenObj))
        # 判断成功失败
        if 'errcode' in flushTokenObj:
            return ''
        else:
            openid = flushTokenObj['openid']
            current_app.logger.debug('授权获取到微信id ：' + openid)
            return openid

    # 授权登录
    @classmethod
    def isOauth(cls):
        try:
            serverOauthUrl = 'http://test.yundong99.net/weixin/oauth'
            #serverOauthUrl = '123.206.25.118/weixin/oauth'
            url = request.url   # 跳转授权url
            # 保存需要授权的url
            authUrl = OauthUrl()
            authUrl.url = url
            authUrl.id = randomStr(16)
            db_session.add(authUrl)

            current_app.logger.debug(' oauth redirect url : ' + url)
            return WeixinHelper.oauth2_info(serverOauthUrl,authUrl.id)
        except Exception,e:
            current_app.logger.error(str(e))
            return


    # 关注
    @classmethod
    def subscribe(cls, dict):
        try:
            # if 'FromUserName' in dict and dict.FromUserName:
            weixinid = dict.FromUserName
            lat = dict.Latitude
            lng = dict.Longitude

            current_app.logger.debug(' weixinid = ' + weixinid )
            # 根据weixinid判断用户是否存在
            weixinUser = db_session.query(WeixinUser).filter(WeixinUser.openid == weixinid).first()
            if weixinUser:
                if weixinUser.subscribe == 0:
                    weixinUser.subscribe == 1
                weixinUser.coordinate_lat = lat
                weixinUser.coordinate_lng = lng
                weixinUser.update_time = str(int(time.time()) * 1000)
                # 更新微信用户信息
                WeixinUser().update(weixinUser)
                return
            else:  # 从微信获取用户信息并保存
                userinfo = cls.getUserInfo(weixinid)
                weixinUser = WeixinUser()
                weixinUser.openid = userinfo.get('openid')
                weixinUser.nickname = userinfo.get('nickname')
                weixinUser.sex = userinfo.get('sex')
                weixinUser.pic = userinfo.get('headimgurl')
                weixinUser.create_time = str(int(time.time()) * 1000)
                weixinUser.subscribe = userinfo.get('subscribe')
                weixinUser.coordinate_lng = lng
                weixinUser.coordinate_lat = lat
                weixinUser.update_time = str(int(time.time()) * 1000)
                WeixinUser().add(weixinUser)

                return
        except Exception, e:
            current_app.logger.error(str(e))
            return

    # 取消关注
    @classmethod
    def unsubscribe(cls, dict):
        try:
            weixinid = dict.FromUserName
            lat = dict.Latitude
            lng = dict.Longitude
            # 根据weixinid判断用户是否存在
            weixinUser = db_session.query(WeixinUser).filter(WeixinUser.openid == weixinid).first()
            if weixinUser:
                if weixinUser.subscribe == 1:
                    weixinUser.subscribe == 0
                weixinUser.coordinate_lat = lat
                weixinUser.coordinate_lng = lng
                weixinUser.update_time = str(int(time.time()) * 1000)
                # 更新微信用户信息
                WeixinUser().update(weixinUser)
                return
            else:
                return
        except Exception, e:
            current_app.logger.error(str(e))
            return

    # json 字符串 处理
    '''
           json_string=json.dumps(access_token)
           obj =  json.loads(json_string)
    '''

    @classmethod
    def byteify(cls,input):
        if isinstance(input, dict):
            return {cls.byteify(key): cls.byteify(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [cls.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input


    @classmethod
    def createMenu(cls,menuJson):
        access_token = cls.getAccessToken()
        resJson = cls.byteify(WeixinHelper.deleteMenu(access_token))
        current_app.logger.debug('delete menu result : ' + str(resJson))
        resJson = cls.byteify(WeixinHelper.createMenu(menuJson,access_token))
        current_app.logger.debug('menu json :' + menuJson)
        current_app.logger.debug('create menu result : ' + str(resJson))
        return resJson

    @classmethod
    def getJsSign(cls,url):
        jsapi_ticket = cls.getJsToken()
        res = WeixinHelper.jsapiSign(jsapi_ticket,url)
        current_app.logger.debug(res)
        return res

    @classmethod
    def getAppid(cls):
        appid = WeixinHelper.getAppId()
        return appid