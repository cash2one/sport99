# Weixin API

#### 1. 获取js验证参数
- url: /wx/get_tx_signature
- method: GET
- params:
- return:
{
  "app_id": "wx605507267852f897",
  "code": 1,
  "noncestr": "YIfPiXmZRXaLxUN",
  "signature": "011b3d0a100dd8b57e2c056b98e5be6778fcb7f8",
  "timestamp": 1458133410
}

#### 2. 通过code获取用户信息并登录
- url: /wx/auth
- method: GET
- params:
        code String 微信授权code
- return:
{
  "code": 1 ,
  "user_id": 1,
  "open_id": "oAdput_4NEjIFI2TW6LXo4nA99bw"
}



