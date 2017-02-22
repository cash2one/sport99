# coding=utf8
__author__ = 'jiangzhuang'

import json
from werkzeug.security import check_password_hash,generate_password_hash
class User():
    def __init__(self,id,email):
        self.id = id
        self.email = email

def convert_to_builtin_type(obj):
    print 'default(', repr(obj), ')' # 把MyObj对象转换成dict类型的对象
    d = {  }
    d.update(obj.__dict__)
    return d

def _decode_list(data):
  rv = []
  for item in data:
    if isinstance(item, unicode):
      item = item.encode('utf-8')
    elif isinstance(item, list):
      item = _decode_list(item)
    elif isinstance(item, dict):
      item = _decode_dict(item)
    rv.append(item)
  return rv

def _decode_dict(data):
  rv = {}
  for key, value in data.iteritems():
    if isinstance(key, unicode):
      key = key.encode('utf-8')
    if isinstance(value, unicode):
      value = value.encode('utf-8')
    elif isinstance(value, list):
      value = _decode_list(value)
    elif isinstance(value, dict):
      value = _decode_dict(value)
    rv[key] = value
  return rv

user = User('11111','285964105@qq.com')

unicodeJson = "{u'province': u'\u5317\u4eac', u'city': u'\u660c\u5e73',u'subscribe_time': 1457670000, u'headimgurl': u'http://wx.qlogo.cn/mmopen/uADAIDXblylwxL0BvicXpJ10ElDknzariaJvHar59baiaEcusP2GO7wdbfKE2dDqwKP4PFKdVGnBoeLhOW6E8v58MjcVvs0tCbE/0', u'language': u'zh_CN',u'openid': u'oAdput_4NEjIFI2TW6LXo4nA99bw', u'country': u'\u4e2d\u56fd',u'remark': u'',u'sex': 1,u'subscribe': 1,u'nickname': u'\u8d4c',u'groupid': 0}"

#json_string=json.dumps(unicodeJson,ensure_ascii=False)
#print str(json.JSONDecoder(unicodeJson))

#fp = unicodeJson.decode("ascii").encode("utf-8")
#str1 = json.loads(unicodeJson)


#print str(json_string)
d = json.loads(unicodeJson)
print str(d.openid)



