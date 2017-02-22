#coding=utf8
'''
2016-02-29

@author: jiangzhuang
'''
import json
import time
import random
import string
import urllib
import urllib2
import hashlib
import threading
import traceback
import requests
import re

import xml.etree.ElementTree as ET

from functools import wraps

from config import WxPayConf

try:
    import pycurl
    from cStringIO import StringIO
except ImportError:
    pycurl = None

try:
    import requests
except ImportError:
    requests = None

def catch(func):
    @wraps(func)
    def wrap(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            print(traceback.format_exc())
            return None
    return wrap

class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


class Singleton(object):
    """可配置单例模式"""

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    impl = cls.configure() if hasattr(cls, "configure") else cls
                    instance = super(Singleton, cls).__new__(impl, *args, **kwargs)
                    if not isinstance(instance, cls):
                        instance.__init__(*args, **kwargs)
                    cls._instance = instance
        return cls._instance


class class_property(object):
    """ A property can decorator class or instance

    class Foo(object):
        @class_property
        def foo(cls):
            return 42


    print(Foo.foo)
    print(Foo().foo)

    """
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        value = self.func(type)
        return value

class BaseHttpClient(object):
    include_ssl = False

    def get(self, url, second=30):
        if self.include_ssl:
            return self.postXmlSSL(None, url, second, False, False)
        else:
            return self.postXml(None, url, second)

    def postXml(self, xml, url, second=30):
        if self.include_ssl:
            return self.postXmlSSL(xml, url, second, cert=False)
        else:
            raise NotImplementedError("please implement postXML")

    def postXmlSSL(self, xml, url, second=30, cert=True, post=True):
        raise NotImplementedError("please implement postXMLSSL")


class UrllibClient(BaseHttpClient):
    """使用urlib2发送请求"""
    def postXml(self, xml, url, second=30):
        """不使用证书"""
        r = requests.get(url, params=xml)

 #       data = urllib2.urlopen(url, xml, timeout=second).read()

        return r.json()


class CurlClient(BaseHttpClient):
    """使用Curl发送请求"""
    include_ssl = True

    def __init__(self):
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYHOST, False)
        self.curl.setopt(pycurl.SSL_VERIFYPEER, False)
        #设置不输出header
        self.curl.setopt(pycurl.HEADER, False)

    def postXmlSSL(self, xml, url, second=30, cert=True, post=True):
        """使用证书"""
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.TIMEOUT, second)
        #设置证书
        #使用证书：cert 与 key 分别属于两个.pem文件
        #默认格式为PEM，可以注释
        if cert:
            self.curl.setopt(pycurl.SSLKEYTYPE, "PEM")
            self.curl.setopt(pycurl.SSLKEY, WxPayConf.SSLKEY_PATH)
            self.curl.setopt(pycurl.SSLCERTTYPE, "PEM")
            self.curl.setopt(pycurl.SSLCERT, WxPayConf.SSLCERT_PATH)
        #post提交方式
        if post:
            self.curl.setopt(pycurl.POST, True)
            self.curl.setopt(pycurl.POSTFIELDS, xml)
        buff = StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buff.write)

        self.curl.perform()
        return buff.getvalue()


class RequestsClient(BaseHttpClient):
    include_ssl = True

    def postXmlSSL(self, xml, url, second=30, cert=True, post=True):
        if cert:
            cert_config = (WxPayConf.SSLCERT_PATH, WxPayConf.SSLKEY_PATH)
        else:
            cert_config = None
        if post:
            res = requests.post(url, data=xml, second=30, cert=cert_config)
        else:
            res = requests.get(url, timeout=second, cert=cert_config)
        return res.content

class HttpClient(Singleton, BaseHttpClient):
    @classmethod
    def configure(cls):
        config_client =  WxPayConf.HTTP_CLIENT
        client_cls = {"urllib": UrllibClient,
                      "curl": CurlClient,
                      "requests": RequestsClient}.get(config_client.lower(), None)
        if client_cls:
            return client_cls

        if pycurl is not None:
            print("HTTP_CLIENT config error, Use 'CURL'")
            return CurlClient
        if requests is not None:
            print("HTTP_CLIENT config error, Use 'REQUESTS'")
            return RequestsClient
        else:
            print("HTTP_CLIENT config error, Use 'URLLIB'")
            return UrllibClient


#微信基本接口封装   http://mp.weixin.qq.com/wiki/home/index.html
class WeixinHelper(object):
    #微信对接签名校验
    @classmethod
    def checkSignature(cls, signature, timestamp, nonce):
        '''
        :param signature:
        :param timestamp:
        :param nonce:
        :return:
        '''
        tmp = [WxPayConf.TOKEN, timestamp, nonce]
        tmp.sort()
        code = hashlib.sha1("".join(tmp)).hexdigest()
        return code == signature
    #随机数
    @classmethod
    def nonceStr(cls, length):
        '''
        :param length:  长度
        :return:
        '''
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    #将xml转为array
    @classmethod
    def xmlToArray(cls, xml):
        return dict((child.tag, child.text) for child in ET.fromstring(xml))

    #网页授权获取用户信息 http://mp.weixin.qq.com/wiki/4/9ac2e7b1f1d22e9e57260f6553822520.html
    @classmethod
    def oauth2_info(cls, redirect_uri, state , scope="snsapi_base"):
        '''
        :param redirect_uri: 回调链接地址，需urlencode处理
        :param scope:        snsapi_userinfo：需用户同意  snsapi_base：静默
        :param state:        回传参数，用于记录特殊信息
        :return:
        '''
        strinfo = re.compile('/')

        _OAUTH_URL = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={0}&redirect_uri={1}&response_type=code&scope={3}&state={2}#wechat_redirect"
        return _OAUTH_URL.format(WxPayConf.APPID,strinfo.sub('%2F',urllib.quote(redirect_uri)) , state, scope)

    #获取access_token  http://mp.weixin.qq.com/wiki/14/9f9c82c1af308e3b14ba9b973f99a8ba.html
    @classmethod
    def getAccessToken(cls):
        '''
        公众号的全局唯一票据
        :return:  需要进行缓存，512个字符空间，有效期2个小时
        '''
        _ACCESS_URL = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}"
        return HttpClient().get(_ACCESS_URL.format(WxPayConf.APPID, WxPayConf.APPSECRET))

    #获取用户基本信息   http://mp.weixin.qq.com/wiki/1/8a5ce6257f1d3b2afb20f83e72b72ce9.html
    @classmethod
    def getUserInfo(cls, access_token, openid, lang="zh_CN"):
        _USER_URL = "https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}&openid={1}&lang={2}"
        return HttpClient().get(_USER_URL.format(access_token, openid, lang))

    #通过code换取网页授权access_token ，较短时间 配合 refreshAccessToken使用  http://mp.weixin.qq.com/wiki/4/9ac2e7b1f1d22e9e57260f6553822520.html
    @classmethod
    def getAccessTokenByCode(cls, code):
        _CODEACCESS_URL = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&grant_type=authorization_code"
        #res = requests.get(_CODEACCESS_URL.format(WxPayConf.APPID, WxPayConf.APPSECRET, code))
        #return res.content
        return HttpClient().get(_CODEACCESS_URL.format(WxPayConf.APPID, WxPayConf.APPSECRET, code))

    #刷新access_token, 使用getAccessTokenByCode()返回的refresh_token刷新access_token，可获得较长时间有效期
    @classmethod
    def refreshAccessToken(cls, refresh_token):
        _REFRESHTOKRN_URL = "https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={0}&grant_type=refresh_token&refresh_token={1}"
        return HttpClient().get(_REFRESHTOKRN_URL.format(WxPayConf.APPID, refresh_token))


    #拉取用户信息(通过网页授权)
    @classmethod
    def getSnsapiUserInfo(cls, access_token, openid, lang="zh_CN"):
        _SNSUSER_URL = "https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang={2}"
        return HttpClient().get(_SNSUSER_URL.format(access_token, openid, lang))

    #检验授权凭证（access_token）是否有效
    @classmethod
    def validateAccessToken(cls, access_token, openid):
        _VALIDATE_URL = "https://api.weixin.qq.com/sns/auth?access_token={0}&openid={1}"
        return HttpClient().get(_VALIDATE_URL.format(access_token, openid))

    #发送客服消息接口  http://mp.weixin.qq.com/wiki/11/c88c270ae8935291626538f9c64bd123.html
    @classmethod
    def send(cls, data, access_token):
        _SEND_URL ="https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={0}"
        data = json.dumps(data, ensure_ascii=False)
        return HttpClient().postXml(data, _SEND_URL.format(access_token))

    #发送文本消息
    @classmethod
    def sendTextMessage(cls, openid, message, access_token):
        data = {
            "touser": openid,
            "msgtype":"text",
            "text":
            {
                "content": message
            }
        }
        return cls.send(data, access_token)

    #发送图文消息
    @classmethod
    def sendNews(cls, openid, message, access_token):
        data = {
            "touser": openid,
            "msgtype":"news",
            "news":
            {
                 "articles": [
                     {
                         "title":"tuwen1",
                         "description":"Is Really A Happy Day",
                         "url":"URL",
                         "picurl":"PIC_URL"
                     },
                     {
                         "title":"tuwen2",
                         "description":"Is Really A Happy Day",
                         "url":"URL",
                         "picurl":"PIC_URL"
                     }
                 ]
            }
        }
        return cls.send(data, access_token)

    #获取jsapi_tocket  http://mp.weixin.qq.com/wiki/11/74ad127cc054f6b80759c40f77ec03db.html
    @classmethod
    def getJsapiTicket(cls, access_token):
        '''
        jsapi_ticket的有效期为7200秒,需要进行缓存
        :param access_token:
        :return:
        '''
        _JSAPI_URL = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={0}&type=jsapi"
        return HttpClient().get(_JSAPI_URL.format(access_token))

    #jsapi_ticket 签名
    @classmethod
    def jsapiSign(cls, jsapi_ticket,url):
        sign = {
            'nonceStr': cls.nonceStr(15),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': int(time.time()),
            'url': url
        }
        signature = '&'.join(['%s=%s' % (key.lower(), sign[key]) for key in sorted(sign)])
        sign["signature"] = hashlib.sha1(signature).hexdigest()
        return sign

    # 创建自定义菜单    https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN
    @classmethod
    def createMenu(cls,data,access_token):
        _MENU_CREATE_URL = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token={0}"
        return HttpClient().postXml(data, _MENU_CREATE_URL.format(access_token))

    # 删除自定义菜单    https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=ACCESS_TOKEN
    @classmethod
    def deleteMenu(cls,access_token):
        _MENU_DELETE_URL = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={0}"
        return HttpClient().get(_MENU_DELETE_URL.format(access_token))

    # 获取appid
    @classmethod
    def getAppId(cls):
        return WxPayConf.APPID

     # 获取appid
    @classmethod
    def getAppSecret(cls):
        return  WxPayConf.APPSECRET