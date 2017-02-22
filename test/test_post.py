# coding=utf8
__author__ = 'zhaojm'


import requests
from flask import json
'''
#地址保存 /venue/post
url = '/venue/post'
data = {
    'name': '测试地址',
    'address': '测试地址的详细地址',
    'coordinate_lng':'123',
    'coordinate_lat':222.21,
    'category':'',
    'link_man_mobile':'18027075210'

}
'''
'''
#用户修改 /user/update
url = '/user/update'
data = {
    'id': 1,
    'nick': '测试名称23r2',
    'height':11,
    'weight':222,
    'qq':'222222222',
    'email':'222222222@qq.com',
    'mobile':11,
    'password':'1'
}
'''

'''
#用户查询 /user/detail
url = '/user/detail'
data = {
    'userid': 1
}
'''

'''
#城市列表获取 /area/ajax_list
url = '/area/area_list'
data = {}
'''

'''
# 初始化活动 '/activity/init'
url = '/activity/init'
data = {
    'user_id': 2
}
'''
'''

# 查询活动 '/activity/detail/1'
url = '/activity/detail/2'
data = {}
'''

'''
# 活动等级列表 '/activity/act_level_list'
url = '/mine_clubs'
data = {
    'user_id' : 1
}
'''


'''
# 活动等级列表 '/activity/categories'

url = '/activity/categories'
data = {}
'''

'''

# 登录测试  '/auth/login'
url = '/auth/login'
data = {
    'account':'222222222',
    'password':'1'
}
'''
'''
# 登录测试  '/auth/logout'
url = '/auth/logout'
data = {
}
'''

'''

# 测试微信用户关注 /weixin/index
url = '/weixin/index'
data = '<xml><URL><![CDATA[http://101.201.28.157/weixin/index]]></URL><ToUserName><![CDATA[oAdput_4NEjIFI2TW6LXo4nA99bw]]></ToUserName><FromUserName><![CDATA[oAdput_4NEjIFI2TW6LXo4nA99bw]]></FromUserName><CreateTime>1231231231231</CreateTime><MsgType><![CDATA[event]]></MsgType><Event><![CDATA[subscribe]]></Event><Latitude></Latitude><Longitude></Longitude><Precision></Precision><MsgId>12345678123456781234567812345678123456781234567812345678</MsgId></xml>'
'''

'''

# 测试菜单 /weixin/createMenu
#url = 'https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=GCSCfMg_BwQpHQdoFje1EOnfdxC9yekvylG3T0GHVWJFPMRHQM77WU6FYda2ndVPv0f3pJ45ki9oqbmtE4fYpll7wsRDIgCcEqfDbedcHvnTC7-rmEB1bYA94tIzLt5YFADjAEANIL'
url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=GCSCfMg_BwQpHQdoFje1EOnfdxC9yekvylG3T0GHVWJFPMRHQM77WU6FYda2ndVPv0f3pJ45ki9oqbmtE4fYpll7wsRDIgCcEqfDbedcHvnTC7-rmEB1bYA94tIzLt5YFADjAEANIL'
data = '{"button": [' \
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
'''

'''
# 微信参数接口
url = '/wx/get_tx_signature'
data = {

}
'''

'''

# 保存活动
url = '/events'
data = {
    'id' : 6,
    'category' : 'ymq',
    'club_id' : 3,
    'end_time' : '2016-03-18 22:00',
    'fee' : 6,
    'is_aa' : 'false',
    'members_count_limit' : 5,
    'name' : 'asdaf',
    'place_num' : '13',
    'start_time' : '2016-03-18 20:00',
    'user_id' : 123,
    'venue_address' : '受到了房间啊算了',
    'venue_lat' : 39.915168,
    'venue_lng' : 116.403874,
    'venue_title' : '测试title',
    'venue_city' : '北京'

}
'''


#r = requests.post(url, data=data)
#r = requests.get(url, data=None)

# 活动详情
url = '/events/6'
data = {}

#r = requests.post("http://127.0.0.1:5000"+url, data=data)
r = requests.get("http://127.0.0.1:5000"+url,data=data)
print(r.text)