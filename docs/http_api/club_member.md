# ClubMember API


#### 关注俱乐部
- url: /club_member/add
- method:POST
- data:
{
    club_id: 123,
    user_id: 123,
}

- return:
{
    code: 1,
    error: ''
}


#### 删除俱乐部成员
- url: /club_member/remove/<user_id>/<club_id>
- method:DELETE

- return:
{
    code: 1,
    error: ''
}



