# Club API


#### 1. 请求创建俱乐部信息
- url: /club/init/<user_id>/<token>
- method: GET

- return:
{
    code: 1,
    result:
    {
        club_id: 123,
    }
    error: 123,
   
}




#### 创建俱乐部信息
- url: /club/post
- method: POST,
- data:
{
    club_id:123,
    name:123,
    head_url:123,
    tags:123,
    creator_id:123,
}

- return:
{
    code: 1,
    error: 123,
}



#### 更新俱乐部信息
- url: /club/update
- method: PUT,
- data:
{
    club_id:123,
    name:123,
    head_url:123,
    tags:123,
}

- return:
{
    code: 1,
    error: 123,
}

#### 获取俱乐部信息
- url: /club/detail/<club_id>
- method: GET


- return:
{
    code: 1,
    result:
    {
        club obj
        
    }
}



#### 通过用户 获取俱乐部列表
- url: /club/club_list/<user_id>
- method: GET

- return:
{
    code: 1,
    result:
    [
        {
            Club obj
        }
    ]
}


#### 通过用户, 俱乐部id, 删除俱乐部
- url: /club/remove/<creator_id>/<club_id>
- method: DELETE
-return:
{
    code: 1,
    error: '',
    result: {},
    
}
