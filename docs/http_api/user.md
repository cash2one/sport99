# User API

#### 1. 创建用户
- url: /user/post
- method: POST
- data:
{
    ‘必须字段
    id: 123,
    nick: 123,
    head_url: 123,
    sex: 123,
    interest: 122,
    mobile: 123,
    
    '非必须字段
    height:123,
    weight:123,
    qq:123,
    email:123,
    
    
}

- return:
{
    code: 1,
}


#### 更新用户信息
- url:/user/update
- method:POST
- data:
{
   User obj
}
- return:
{
    code: 1,
}

