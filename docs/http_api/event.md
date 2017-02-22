# Events API

#### 1. 初始化活动
- url: /event_id
- method: GET,POST
- params:
           user_id int
- return:
{
  "code": 1,
  "club": club,
  "id": mid
}

#### 2. 保存活动
- url: /events
- method: POST
- params:

- return:
{
    code: 1
}

#### 3. 获取俱乐部的所有活动
- url: /club_events
- method: GET
- params:
        page_size   int
        page_index  int
        club_id     int
- return:
{
    "code": 1,
    "events": events_copy
}

#### 4. 用户所有活动
- url: /mine_all_events
- method: GET
- params:
        user_id   int
- return:
{
    "code": 1,
    "events": events_copy
}

#### 5. 所有活动
- url: /events
- method: GET
- params:

- return:
{
    "code": 1,
    "events": events_copy
}

#### 6. 用户参加尚未结束的活动
- url: /mine_joining_events
- method: GET
- params:
        user_id int
- return:
{
    "code": 1,
    "events": events_copy
}


#### 7. 用户参加尚未结束的活动
- url: /events/<e_id>
- method: GET
- params:
        e_id int
- return:
{
    "code": 1,
    "events": events_copy
}


#### 8. 活动的人员列表
- url: /events/<e_id>/members
- method: GET
- params:
        e_id int
- return:
{
    "code": 1,
    "events": events_copy
}


#### 9. 参加活动
- url: /events/<e_id>/join
- method: GET
- params:
        e_id int
- return:
{
    "code": 1,
    "events": events_copy
}

#### 9. 活动更新
- url: /events_update
- method: POST
- params:
        e_id int
- return:
{
    "code": 1,
    "events": events_copy
}


#### 10. 获取活动类别列表
- url: /categories
- method: GET
- params:
- return:
{
  "code": 1,
  "result": [
    {
      "code": "1",
      "days": 1,
      "is_cycle": 1,
      "name": "1",
      "status": 1,
      "venue_name": "1"
    }
  ]
}


#### 11. 获取活动等级列表
- url: /levels/<category>
- method: GET
- params:
       category 类别代码
- return:
{
  "code": 1,
  "result": [
    {
      "category": "ymq",
      "id": 3,
      "is_default": 0,
      "name": "2\u6bb5",
      "sort": 2,
      "summary": "\u4ec5\u4ec5\u638c\u63e1\u4e86
    }
}
