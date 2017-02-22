#coding=utf8
'''
2016-02-29

@author: jiangzhuang
'''
import time
from collections import defaultdict
from .wxapi import WeixinHelper, ObjectDict


#微信<->服务器 核心消息处理器
class MessageHandle(object):
    handler = defaultdict(dict)
    def __init__(self, xml):
        self.xml = ObjectDict(WeixinHelper.xmlToArray(xml))

    #开始消息处理
    def start(self):

        msgtype = self.xml.MsgType
        if msgtype == "event":
            key = self.xml.Event
        elif msgtype == "text":
            key = "all"
        else:
            key = ""

        return self.call(msgtype, key)

    #回调事件
    def call(self, type, key):

        assert type in self.handler
        data = self.handler[type][key](self.xml)
        response = self.render(data)
        return response

    #注册事件
    @classmethod
    def register(cls, type, key, func):

        assert key not in cls.handler
        cls.handler[type][key] = func

    #消息回复
    def render(self, data):
        if not data:
            return ""
        reply = Reply(self.xml)
        if isinstance(data, str):
            res = reply.textResponse(data)
        elif isinstance(data, dict):
            res = reply.newsResponse([data])
        elif isinstance(data, list): #只有图片可多条消息
            data = [reply.newsKey(d) for d in data]
            res = reply.newsResponse(data)
        else:
            raise Exception("unknown message response")

        return res


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



R = MessageHandle.register

#关注事件
def subscribe(func):
    R("event", "subscribe", func)
    return func
#取消关注
def unsubscribe(func):
    R("event", "unsubscribe", func)
    return func
#点击事件
def click(func):
    R("event", "CLICK", func)
    return func

#文本消息
def text(func):
    R("text", "all", func)
    return func

