/**
 * Created by zhaojm on 4/23/16.
 */

var eventCtrl = angular.module('eventCtrl', []);

eventCtrl.controller('EventCreateCtrl', function ($http, $scope, $rootScope, $location) {
    $scope.event = {
        "category": "",
        "name": "",
        "is_cycle": false,
        //"type": "event",
        "start_time": 0,
        "end_time": 0,
        "venue": {
            "title": "",
            "address": "",
        },
        //"place_name": "",
        "fee": 0,
        "is_aa": false,
        "members_count_limit": 1,
        "place_num": "",
        "mobile": "",
        "introduce": "",


        "creator_id": "",
        "club_id": "",


        "weekday": 1,

        "days": [],

        //"date_type": "datetime-local",
        //"publish_qq_list": [],


    };


    $scope.category_list_1 = ["羽毛球", "篮球", "网球", "足球", "高尔夫", "乒乓球"];
    $scope.category_list_2 = ["骑行", "爬山", "跑步", "聚餐", "唱歌"];


    $scope.days = [
        {"id": 1, "model": false, "text": "周一"},
        {"id": 2, "model": false, "text": "周二"},
        {"id": 3, "model": false, "text": "周三"},
        {"id": 4, "model": false, "text": "周四"},
        {"id": 5, "model": false, "text": "周五"},
        {"id": 6, "model": false, "text": "周六"},
        {"id": 7, "model": false, "text": "周日"}
    ];
    var check_params = function (params) {
        return true;
    };
    $scope.submit = function () {

        $scope.event.days = [];
        $scope.days.forEach(function (day) {
            if (day.model) {
                $scope.event.days.push(day.id);
            }
        });
        //console.log($scope.event.days);
        var m_params = {
            "category": $scope.event.category,
            "name": $scope.event.name,
            "is_cycle": $scope.event.is_cycle,
            //"type": $scope.event.type,
            "start_time": moment($scope.event.start_time).unix(),
            "end_time": moment($scope.event.end_time).unix(),
            "venue_address": $scope.event.venue.address,
            "venue_title": $scope.event.venue.title,
            "fee": $scope.event.fee,
            "is_aa": $scope.event.is_aa,
            "members_count_limit": $scope.event.members_count_limit,
            "place_num": $scope.event.place_num,
            //"place_name": $scope.event.place_name,
            "mobile": $scope.event.mobile,
            "introduce": $scope.event.introduce,


            "creator_id": $scope.event.creator_id,
            "club_id": $scope.event.club_id,

            "weekday": $scope.event.weekday,
            "days": $scope.event.days.toString().substr(0, $scope.event.days.toString().length)
        };

        m_params.token = $rootScope.admin_info.token;
        m_params.admin_id = $rootScope.admin_info.id;
        console.log(m_params);
        if (!check_params(m_params)) return;
        $http({
            url: "/admin/event/new",
            method: "POST",
            params: m_params
        }).success(function (d) {
            if (d.retcode == 0) {
                $location.path("/event/list");
                console.log(d.result);
            } else {
                console.log(d.errmsg);
            }


        }).error(function (d) {
            console.log("create event error");
            $location.path("/login");
        });
    };

    $scope.set_category = function (category) {
        $scope.event.category = category;
    };


    var init = function () {

        // 时间选择
        date = new Date();
        // dd = moment([date.getFullYear(), date.getMonth(), date.getDate(), 20, 0]);
        sd = moment([date.getFullYear(), date.getMonth(), date.getDate(), 20, 0]);
        ed = moment([date.getFullYear(), date.getMonth(), date.getDate(), 22, 0]);

        $scope.event.start_time = sd.toDate();
        $scope.event.end_time = ed.toDate();

        var user_and_club = $rootScope.getObject("user_and_club");
        //console.log("user_and_club", user_and_club);

        $scope.event.creator_id = user_and_club.user_id;
        $scope.event.club_id = user_and_club.club_id;
        $scope.event.mobile = user_and_club.mobile;

    };

    init();


});

eventCtrl.controller('EventListCtrl', function ($http, $scope, $rootScope, $location) {
    $scope.events = [
        {"id": 1, "name": "test event"},
    ];

    $scope.event_detail = function (event_id) {
        $location.path('/event/detail/' + event_id);
    };
    $scope.event_modify = function (event_id) {
        $location.path('/event/modify/' + event_id);
    };
    $scope.event_delete = function (event_id) {
        var m_params = {};
        m_params.token = $rootScope.admin_info.token;
        m_params.admin_id = $rootScope.admin_info.id;
        $http({
            url: "/admin/event/delete/" + event_id,
            method: "DELETE",
            params: m_params
        }).success(function (d) {
            if (d.retcode == -1) {
                console.log(d.errmsg);
            }
            else if (d.retcode == 0) {
                console.log(d.result);
                for (var i = 0; i < $scope.events.length; i++) {
                    var event = $scope.events[i];
                    if (event.id == event_id) {
                        $scope.events.splice(i, 1);
                        break;
                    }
                }
            }

        }).error(function (d) {
            console.log("get events error");
        });
    };

    $scope.event_search = function (params) {

    };

    var m_params = {};
    m_params.token = $rootScope.admin_info.token;
    m_params.admin_id = $rootScope.admin_info.id;
    $http({
        url: "/admin/event/list",
        method: "GET",
        params: m_params
    }).success(function (d) {
        if (d.retcode == 0) {
            $scope.events = d.result;
            console.log(d.result);
        } else {
            console.log(d.errmsg);
        }


    }).error(function (d) {
        console.log("get event list error");
        console.log(d);
        $location.path("/login");
    });

});

eventCtrl.controller('EventDetailCtrl', function ($http, $scope, $rootScope, $routeParams, $location) {
    $scope.event = {
        "category": "",
        "name": "",
        "is_cycle": false,
        //"type": "event",
        "start_time": 0,
        "end_time": 0,
        "venue": {
            "title": "",
            "address": "",
        },
        //"place_name": "",
        "fee": 0,
        "is_aa": false,
        "members_count_limit": 1,
        "place_num": "",
        "mobile": "",
        "introduce": "",


        "creator_id": "",
        "club_id": "",


        "weekday": 1,

        "days": "",//[],

        //"date_type": "",
        //"publish_qq_list": [],


    };

    $scope.days = [
        {"id": 1, "model": false, "text": "周一"},
        {"id": 2, "model": false, "text": "周二"},
        {"id": 3, "model": false, "text": "周三"},
        {"id": 4, "model": false, "text": "周四"},
        {"id": 5, "model": false, "text": "周五"},
        {"id": 6, "model": false, "text": "周六"},
        {"id": 7, "model": false, "text": "周日"}
    ];

    $scope.event_detail = function (event_id) {
        $location.path('/event/detail/' + event_id);
    };
    $scope.event_modify = function (event_id) {
        $location.path('/event/modify/' + event_id);
    };
    $scope.event_delete = function (event_id) {
        var m_params = {};
        m_params.token = $rootScope.admin_info.token;
        m_params.admin_id = $rootScope.admin_info.id;
        $http({
            url: "/admin/event/delete/" + event_id,
            method: "DELETE",
            params: m_params
        }).success(function (d) {
            if (d.retcode == -1) {
                console.log(d.errmsg);
            }
            else if (d.retcode == 0) {
                $location.path('/event/list');
                console.log(d.result);
            }

        }).error(function (d) {
            console.log("get events error");
        });
    };

    var m_params = {};
    m_params.token = $rootScope.admin_info.token;
    m_params.admin_id = $rootScope.admin_info.id;

    $http({
        url: "/admin/event/detail/" + $routeParams.id,
        method: "GET",
        params: m_params
    }).success(function (d) {
        if (d.retcode == 0) {
            console.log(d.result);
            $scope.event = d.result;
            if ($scope.event.is_aa == "true") {
                $scope.event.is_aa = true;
            }
            if ($scope.event.is_aa == "false") {
                $scope.event.is_aa = false;
            }
            if ($scope.event.is_cycle == "true") {
                $scope.event.is_cycle = true;
            }
            if ($scope.event.is_cycle == "false") {
                $scope.event.is_cycle = false;
            }

            if ($scope.event.is_cycle) {
                $scope.days.forEach(function (day) {

                    if ($scope.event.days.indexOf(day.id) > -1) {
                        day.model = true;
                    } else {
                        day.model = false;
                    }
                });
                //console.log($scope.days);
            }
        } else {
            console.log(d.errmsg);

        }


    }).error(function (d) {
        console.log("get event detail error");
        console.log(d);
        $location.path("/login");
    });
});

eventCtrl.controller('EventModifyCtrl', function ($http, $scope, $rootScope, $routeParams, $location) {
    $scope.event = {
        "id": -1,
        "category": "",
        "name": "",
        "is_cycle": false,
        //"type": "event",
        "start_time": "",
        "end_time": "",
        "venue": {
            "title": "",
            "address": "",
        },
        //"place_name": "",
        "fee": 0,
        "is_aa": false,
        "members_count_limit": 1,
        "place_num": "",
        "mobile": "",
        "introduce": "",


        "creator_id": "",
        "club_id": "",


        "weekday": 1,

        "days": [],

        //"date_type": "",
        //"publish_qq_list": [],


    };

    $scope.category_list_1 = ["羽毛球", "篮球", "网球", "足球", "高尔夫", "乒乓球"];
    $scope.category_list_2 = ["骑行", "爬山", "跑步", "聚餐", "唱歌"];


    $scope.days = [
        {"id": 1, "model": false, "text": "周一"},
        {"id": 2, "model": false, "text": "周二"},
        {"id": 3, "model": false, "text": "周三"},
        {"id": 4, "model": false, "text": "周四"},
        {"id": 5, "model": false, "text": "周五"},
        {"id": 6, "model": false, "text": "周六"},
        {"id": 7, "model": false, "text": "周日"}
    ];

    var check_params = function (params) {
        return true;
    };
    $scope.submit = function () {
        $scope.event.days = [];
        $scope.days.forEach(function (day) {
            if (day.model) {
                $scope.event.days.push(day.id);
            }
        });
        var m_params = {
            "id": $scope.event.id,
            "category": $scope.event.category,
            "name": $scope.event.name,
            "is_cycle": $scope.event.is_cycle,
            //"type": $scope.event.type,
            "start_time": moment($scope.event.start_time).unix(),
            "end_time": moment($scope.event.end_time).unix(),
            "venue_address": $scope.event.venue.address,
            "venue_title": $scope.event.venue.title,
            "fee": $scope.event.fee,
            "is_aa": $scope.event.is_aa,
            "members_count_limit": $scope.event.members_count_limit,
            "place_num": $scope.event.place_num,
            //"place_name": $scope.event.place_name,
            "mobile": $scope.event.mobile,
            "introduce": $scope.event.introduce,


            "creator_id": $scope.event.creator_id,
            "club_id": $scope.event.club_id,

            "weekday": $scope.event.weekday,
            "days": $scope.event.days.toString().substr(0, $scope.event.days.toString().length)
        };

        m_params.token = $rootScope.admin_info.token;
        m_params.admin_id = $rootScope.admin_info.id;
        if (!check_params(m_params)) return;
        $http({
            url: "/admin/event/modify",
            method: "PUT",
            params: m_params
        }).success(function (d) {
            if (d.retcode == 0) {
                $location.path("/event/detail/" + $scope.event.id);
                console.log(d.result);

            } else {
                console.log(d.errmsg);
            }


        }).error(function (d) {
            console.log("event modify error");
            $location.path("/login")
        });
    };

    $scope.set_category = function (category) {
        $scope.event.category = category;
    };

    var m_params = {};
    m_params.token = $rootScope.admin_info.token;
    m_params.admin_id = $rootScope.admin_info.id;
    $http({
        url: "/admin/event/detail/" + $routeParams.id,
        method: "GET",
        params: m_params
    }).success(function (d) {
        if (d.retcode == 0) {
            console.log(d.result);
            //console.log($scope.event);
            $scope.event = d.result;
            if ($scope.event.is_aa == "true") {
                $scope.event.is_aa = true;
            }
            if ($scope.event.is_aa == "false") {
                $scope.event.is_aa = false;
            }
            if ($scope.event.is_cycle == "true") {
                $scope.event.is_cycle = true;
            }
            if ($scope.event.is_cycle == "false") {
                $scope.event.is_cycle = false;
            }
            $scope.event.start_time = moment.unix(d.result.start_time).toDate();
            $scope.event.end_time = moment.unix(d.result.end_time).toDate();

            if ($scope.event.is_cycle) {
                $scope.days.forEach(function (day) {

                    if ($scope.event.days.indexOf(day.id) > -1) {
                        day.model = true;
                    } else {
                        day.model = false;
                    }
                });

                //console.log($scope.days);
            }


        } else {
            console.log(d.errmsg);
        }

    }).error(function (d) {
        console.log("get event detail error");
        $location.path("/login")
    });

});

eventCtrl.controller('EventsOfClubCtrl', function ($http, $scope, $rootScope, $routeParams, $location) {
    $scope.events = [
        {"id": 1, "name": "test event"},
    ];

    $scope.event_detail = function (event_id) {
        $location.path('/event/detail/' + event_id);
    };
    $scope.event_modify = function (event_id) {
        $location.path('/event/modify/' + event_id);
    };
    $scope.event_delete = function (event_id) {
        $http({
            url: "/admin/event/delete/" + event_id,
            method: "DELETE"
        }).success(function (d) {
            if (d.retcode == -1) {
                console.log(d.errmsg);
            }
            else if (d.retcode == 0) {
                console.log(d.result);
                for (var i = 0; i < $scope.events.length; i++) {
                    var event = $scope.events[i];
                    if (event.id == event_id) {
                        $scope.events.splice(i, 1);
                        break;
                    }
                }

            }

        }).error(function (d) {
            console.log("get events error");
        });
    };

    var m_params = {};
    m_params.token = $rootScope.admin_info.token;
    m_params.admin_id = $rootScope.admin_info.id;

    $http({
        url: "/admin/event/list_of_club/" + $routeParams.club_id,
        method: "GET",
        params: m_params
    }).success(function (d) {
        if (d.retcode == 0) {
            $scope.events = d.result;
            console.log(d.result);
        }
        else {
            console.log(d.errmsg);
        }
    }).error(function (d) {
        console.log("get event list error");
        $location.path("/login");
    });

});

