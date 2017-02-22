API标准
===
正确返回
---

	{
	    "retcode":0,  #结果码=0
	    "result":{}
	}
错误返回
---

	{
	    "retcode":242,  #不等于0的数字代表错误
	    "errmsg": "错误信息"
	}
	错误码编号：
	* other 发送错误信息到群
	* 1001 
	* 1002 返回错误信息直接发送
	* 1003 参数错误
	* 1004 活动不存在
	* 1005 已报名此活动
	* 1006 活动报名人数超过人数上限

Robot API
===
receive
-------
- url: /robot/receive
- method: POST
- params:
    * cmd String # getActivityList | getActivityDetail | joinActivity | cancelJoinActivity | helpJoinActivity | helpCancelJoinActivity | speJoinActivity | speCancelJoinActivity | sendNormalIM | sendTmpIM
    * data String # json string
- return:

		{
			"retcode": 0,
			"result": {}
		}

### cmd
###### getActivityList
- data: 

	    {
	        "robot":123456,
	        "externalId": 123456,
	        "qq": 123456,
	    }

- result:

	    [
	        {
	            "sign": 1,
	            "name": 123,
	            "placeName": qqq,
	            "beginDate": 123,
	            "beginTime": 123,
	            "endTime": 123,
	        },
	        ...
	    ]

###### getActivityDetail
- data: 

	    {
	        "sign": 123,
	        "robot":123456,
	        "externalId": 123456,
	        "qq": 123456,
	    }

- result:

	    {
	        "sign": 1,
	        "name": 123,
	        "placeName": qqq,
	        "beginDate": 123,
	        "beginTime": 123,
	        "endTime": 123,
	        "createUser":123,
	        "mobile": 123,
	        "totalNumber": 123,
	        "id": 123,
	        "userList":
	        [
	            {
	                "nick":213,
	                "qq":123,
	                "help_qq":123,
	                "type":123,
	            }
	            ...
	        ]
	        
	    }

###### joinActivity
- data: 

	    {
	        "sign": 123,
	        "robot":123456,
	        "externalId": 123456,
	        "qq": 123456,
	        "gua": 2,
	    }

###### cancelJoinActivity
- data: 

	    {
	        "sign": 123,
	        "robot":123456,
	        "externalId": 123456,
	        "qq": 123456,
	    }

- result:

	    [
	        {
	            "sign": 123,
	            "placeName": 123,
	        }
	        ...
	    ]

###### helpJoinActivity
- data: 
 
	    {
	        "sign": 123,
	        "robot":123456,
	        "externalId": 123456,
	        "qq": 123456,
	        "gua":1,
	        "friendQQ": 13,
	    }

###### helpCancelJoinActivity
- data: 

	    {
	        "sign": 123,
	        "robot":123456,
	        "externalId": 123456,
	        "qq": 123456,
	        "friendQQ": 13,
	    }

- result:

	    [
	        {
	            "sign"： 123，
	            "placeName": 123,
	        }
	        ...
	    ]

###### speJoinActivity
- data: 

	    {
	        sign: 123,
	        robot:123456,
	        externalId: 123456,
	        qq: 123456,
	        gua: 13,
	        friendQQ: 13,
	    }

###### speCancelJoinActivity
- data: 

	    {
	        sign: 123,
	        robot:123456,
	        externalId: 123456,
	        qq: 123456,
	        gua: 13,
	        friend: 13,
	    }

- result:

	    [
	        {
	            sign： 123，
	            placeName: 123,
	        }
	        ...
	    ]

###### sendNormalIM
- data: 

	    {
	        robot:123456,
	        qq: 123456,
	        message: 13,
	        sendTime: 13,
	    }

###### sendTmpIM
- data: 

	    {
	        robot:123456,
	        qq: 123456,
	        message: 13,
	        sendTime: 13,
	    }

sync
---
- url: /robot/sync
- method: POST
- params:
    * cmd String # saveUser | removeUser | saveCluster | removeCluster | addToCluster
    * data String # json string
- return:

		{
			"retcode": 0,
			"result": {}
		}

###### saveUser
- data: 

	    {
	        robot:123456,
	        externalId:123,
	        qq: 123456,
	        nick: 123,
	        isAdmin: 1,
	        qAge: 123,
	        card: 123,
	        black: 123,
	    }

###### removeUser
- data: 
 
	    {
	        robot:123456,
	        externalId:123,
	        qq: 123456,
	    }

###### saveCluster
- data: 

		{
		    robot:123456,
		    externalId:123,
		    name: 123456,
		    creator: 123,
		    members:
		     [
		        {
		            externalId: 123,
		            qq: 123,
		            nick: 123,
		            aQge: 123,
		            card: 123,
		            black: 123,
		            
		        },
		        ...
		    ]
		   
		}

###### removeCluster
- data: 

	    {
	        robot:123456,
	        externalId:123,
	        qq: 123456,
	    }

###### addToCluster
- data: 

	    {
	        robot:123456,
	        externalId:123,
	    }

push
---
- url: /robot/push
- method: POST
- params:
    * cmd String # doPush
    * data String # json string
- return:

		{
			"retcode": 0,
			"result": {}
		}

###### doPush
- data:

	    {
	        robot:123456,
	    }

- result:

	    [
	       {
	            type: 1,
	            
	       }
	       ...
	    ]

### Type:
###### SendTmpMsg

		{
		    type: 1,
		    externalId: 123,
		    qq: 123,
		    msg: 123,
		}

###### SaveCluster

		{
		    type: 2,
		    externalId: 123,
		}

###### SaveAllClusters

		{
		    type: 3,
		}

###### SendClusterMsg

		{
		    type: 4,
		    externalId: 123,
		    msg: 123,
		}

###### SendMsg

		{
		    type: 5,
		    qq: 123,
		    msg: 123,
		}

###### SendAttetion

		{
		    type:6,
		}

###### JoinCluster

		{
		    type: 7,
		    externalId: 123,
		    msg: 123,
		}

###### default

		{
		    type: other,
		}
