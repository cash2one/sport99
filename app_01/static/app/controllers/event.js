var eventController = angular.module('eventController', []);

// 报名活动， 可带入
eventController.controller('EventJoinController',
    ['$scope', '$rootScope', '$http', '$routeParams', 'ngDialog',
        function ($scope, $rootScope, $http, $routeParams, ngDialog) {

            $scope.join = function () {
                // 报名
                $http({
                    url: $rootScope.url_prefix + "/events/" + $routeParams.id + "/join",
                    method: "POST",
                    params: {
                        exit_count: $rootScope.exit_count,
                        join_count: $scope.join_count,
                        user_id: $rootScope.user_id,
                        token: $rootScope.token
                    }
                }).then(function (response) {
                    // 报名成功，通知主页面刷新
                    $scope.closeThisDialog($scope.join_count);
                }, function () {
                    // TODO 报名失败
                });
            }
        }]);

// 创建活动
eventController.controller('EventCreateStep1Controller',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http', 'ngDialog',
        function ($scope, $rootScope, $location, $routeParams, $http, ngDialog) {

            $scope.save = function () {
                $rootScope.putObject("event_creating", $scope.event);
            }

            var init = function () {
                $scope.event = {}

                $scope.event.category = "选择项目（必选）";
                // 时间选择
                date = new Date();
                // dd = moment([date.getFullYear(), date.getMonth(), date.getDate(), 20, 0]);
                sd = moment([date.getFullYear(), date.getMonth(), date.getDate(), 20, 0]);
                ed = moment([date.getFullYear(), date.getMonth(), date.getDate(), 22, 0]);
                $scope.time_min = sd.toDate();


                $scope.event.start_time = sd.toDate();
                $scope.event.end_time = ed.toDate();

                $scope.event.is_cycle = false;
                $scope.event.date_type = "datetime-local";
                $scope.event.is_aa = false;

                $scope.event.location = {};
                $scope.event.publish_qq_list = [];
                // 从服务器获取活动ID
                $http({
                    url: $rootScope.url_prefix + "event_id",
                    method: "GET",
                    params: {user_id: $rootScope.user_id, token: $rootScope.token}
                }).then(function (response) {
                    data = response.data;
                    console.log(data);
                    $scope.event.id = data.id;
                    $scope.event.mobile = data.mobile;
                    if (!response.data.club) {
                        $scope.cover_show = true;
                    } else {
                        $scope.event.club = response.data.club;
                    }
                    console.log($scope.event);
                    //初始化之后存入缓存
                    $scope.save();
                }, function (e) {
                    console.log(e);
                });
            }
            if ($rootScope.getObject("event_creating") && $rootScope.getObject("event_creating").club) {
                $scope.event = $rootScope.getObject("event_creating");
                $scope.event.start_time = new Date($scope.event.start_time);
                $scope.event.end_time = new Date($scope.event.end_time);

            } else {
                init();
                console.log("init");
            }
            $http({
                url: $rootScope.url_prefix + "users/clusters",
                method: "GET",
                params: {user_id: $rootScope.user_id, token: $rootScope.token}
            }).then(function (response) {
                data = response.data;
                $scope.clusters = data.clusters;
                $scope.qq_bind = data.qq_bind;

                //初始化之后存入缓存
                $scope.save();
            }, function (e) {
                console.log(e);
            });

            console.log("活动>>");

            $scope.to_add_club = function () {
                localStorage.finish_url = $location.url();
                $scope.save();
                $location.path("/clubs/create_step1");
            }
            $scope.fee_set = function () {
                $scope.event.is_aa = false;
            }
            // 选择项目
            $scope.category_pick = function () {
                var dialog = ngDialog.open({
                    template: '/static/app/templates/event/category_picker.html',
                    className: 'ngdialog-theme-plain page_category_picker',
                    appendTo: '#event_create',
                    controller: 'CategoryPickerController',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {
                    $scope.event.category = data.value;
                    $scope.save();
                });
            }
            $scope.days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

            // 选择周期
            $scope.cycle_pick = function () {
                var dialog = ngDialog.open({
                    template: '/static/app/templates/event/cycle_picker.html',
                    className: 'ngdialog-theme-plain ngdialog_page',
                    appendTo: '#event_create',
                    controller: 'CyclePickerController',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {

                    $scope.event.days = data.value;
                    if (data.value) {
                        $scope.event.day_show = "";
                        for (var i = 0; i < $scope.event.days.length; i++) {
                            $scope.event.day_show += $scope.days[$scope.event.days[i]] + ",";
                        }
                        $scope.event.day_show = $scope.event.day_show.substr(0, $scope.event.day_show.length - 1)
                        $scope.save();
                    }

                    console.log($scope.event.day_show);
                });
            }

            $scope.location_set = function () {
                $location.path("/location");
                $scope.save();
            }
            // AA制
            $scope.toggle_aa_set = function (t) {
                if (t == 2) {
                    $scope.event.is_aa = !$scope.event.is_aa;
                    if ($scope.event.is_aa) {
                        $scope.event.fee = null;
                    }
                } else {
                    $scope.event.is_aa = false;
                }

            }
            $scope.time_type_set = function (type) {
                if (type == 1) {
                    $scope.event.is_cycle = false;
                    $scope.event.day = null;
                    $scope.event.date_type = "datetime-local";
                }
                else {
                    $scope.event.is_cycle = true;
                    $scope.event.date_type = "time";
                    $scope.cycle_pick();
                }
                console.log($scope.date_type);
            }
            $scope.is_start_time_setting = false;
            $scope.is_end_time_setting = false;
            // 设置开始时间
            $scope.set_start_time = function () {
                //$scope.is_start_time_setting = true;
                $("#start_time_in").focus();
            };
            // 设置开始完毕
            $scope.start_time_change = function () {
                var date = $scope.event.start_time;
                $scope.time_min = moment(date).format("YYYY-MM-DDTHH:mm:ss");

                var ed = moment(date).add(2, "hours");
                $scope.event.end_time = ed.toDate();
                $scope.save();
            }
            // 设置结束事件
            $scope.set_end_time = function () {
                //$scope.is_end_time_setting = true;
                $("#end_time_in").focus();
                $scope.save();
            }

            $scope.qq_select = function (qq) {
                console.log(qq);

                if ($scope.event.publish_qq_list.indexOf(qq) < 0) {
                    $scope.event.publish_qq_list.push(qq);
                } else {
                    $scope.event.publish_qq_list.pop(qq);
                }
                console.log($scope.event.publish_qq_list);
                $scope.save();
            }
            $scope.qq_selected = function (qq) {

                if ($scope.event.publish_qq_list.indexOf(qq) >= 0)
                    return true;
                else
                    return false;
            }
            $scope.submit_enable = false;
            $scope.check_submit_enable = function () {
                console.log($rootScope);
                $scope.submit_enable = $scope.event.club;
                console.log($scope.submit_enable);
            }

            // 下一步
            $scope.submit = function () {
                var qqs = "";
                for (var i = 0; i < $scope.event.publish_qq_list.length; i++) {
                    qqs = qqs + $scope.event.publish_qq_list[i] + ",";
                }
                qqs = qqs.substr(0, qqs.length - 1);
                console.log($scope.event);

                m_params = {
                    user_id: $rootScope.user_id,
                    token: $rootScope.token,
                    id: $scope.event.id,

                    category: $scope.event.category,
                    //start_time: $scope.event.start_time,
                    //end_time: $scope.event.end_time,
                    start_time: moment($scope.event.start_time).unix(),
                    end_time: moment($scope.event.end_time).unix(),
                    place_num: $scope.event.place_num,
                    club_id: $scope.event.club.id,
                    clusters: qqs,
                    is_cycle: $scope.event.is_cycle,
                    introduce: $scope.event.introduce,

                }
                if (!$scope.event.name || $scope.event.name.length < 1) {
                    $rootScope.alert("活动名称不能为空");
                    return;
                }
                m_params.name = $scope.event.name;
                if (!$scope.event.category || $scope.event.category == "选择项目（必选）") {
                    $rootScope.alert("请选择选择项目类型");
                    return;
                }
                m_params.category = $scope.event.category;
                if (!$scope.event.members_count_limit) {
                    $rootScope.alert("人数不能为空");
                    return;
                }
                m_params.members_count_limit = $scope.event.members_count_limit;
                if ($scope.event.days) {
                    m_params.days = $scope.event.days.toString().substr(0, $scope.event.days.toString().length);
                }
                if (!$scope.event.mobile) {
                    $rootScope.alert("电话不能为空");
                    return;
                }
                m_params.mobile = $scope.event.mobile;
                if (!$scope.event.location.address) {
                    $rootScope.alert("场地不能为空");
                    return;
                }
                if (!$scope.event.fee && !$scope.event.is_aa) {
                    $rootScope.alert("请设置场地费用");
                    return;
                }
                m_params.fee = $scope.event.fee;
                m_params.is_aa = $scope.event.is_aa
                m_params.venue_title = $scope.event.location.title;
                m_params.venue_address = $scope.event.location.address;
                m_params.venue_phone = $scope.event.location.phone;
                m_params.venue_city = $scope.event.location.city;
                m_params.venue_lng = $scope.event.location.point.lng;
                m_params.venue_lat = $scope.event.location.point.lat;


                if (m_params.end_time - m_params.start_time > 3600 * 24 * 9) {
                    $rootScope.alert("时间跨度过长,请重新设计");
                    return;
                }
                localStorage.removeItem("event_creating");
                $http({
                    url: $rootScope.url_prefix + "events",
                    method: "POST",
                    params: m_params
                }).success(function (data) {
                    // console.log(data);

                    $location.path("/events");

                }).error(function (e) {
                    console.log(e);
                });
            };

            $scope.bind_show = function () {
                if ($scope.qq_bind) {
                    $location.path("/clubs/create_step3");
                } else {
                    var dialog = ngDialog.open({
                        template: 'band_qq',
                        className: 'ngdialog-theme-plain ngdialog_page',
                        appendTo: '#event_create'
                    });
                    dialog.closePromise.then(function (data) {
                        // 接受报名结果
                        if (data.value) {
                            $scope.save();
                            $location.path("/clubs/create_step2");
                        }
                    });

                }
            }
            if ($location.search().from && $location.search().from == "bind_qq") {
                // 从后台拿QQ列表
            }
            ;
        }]);


// 创建活动
eventController.controller('EventUpdateController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http', 'ngDialog',
        function ($scope, $rootScope, $location, $routeParams, $http, ngDialog) {

            $scope.save = function () {
                $rootScope.putObject("event_update" + $routeParams.id, $scope.event);
            }
            $scope.cover_show = false;
            $scope.update_page = true;
            $scope.days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
            var init = function () {
                // 从服务器获取活动ID
                $http({
                    url: $rootScope.url_prefix + "events/" + $routeParams.id,
                    method: "GET",
                    params: {user_id: $rootScope.user_id, token: $rootScope.token}
                }).then(function (response) {
                    $scope.event = response.data.event;
                    console.log($scope.event);
                    $scope.event.place_num = ($scope.event.place_num);
                    $scope.event.members_count_limit = parseInt($scope.event.members_count_limit);
                    $scope.event.start_time = moment.unix($scope.event.start_time).toDate();
                    $scope.event.end_time = moment.unix($scope.event.end_time).toDate();

                    $scope.event.location = $scope.event.venue;
                    $scope.event.location.point = $scope.event.venue.coordinate;
                    $scope.event.publish_qq_list = $scope.event.clusters;

                    if ($scope.event.is_cycle == 'false') {
                        $scope.event.is_cycle = false;
                    } else {
                        $scope.event.is_cycle = true;
                        $scope.event.day_show = "";
                        for (var i = 0; i < $scope.event.days.length; i++) {
                            $scope.event.day_show += $scope.days[$scope.event.days[i]] + ",";
                        }
                        $scope.event.day_show = $scope.event.day_show.substr(0, $scope.event.day_show.length - 1)
                    }
                    if ($scope.event.is_aa == 'false') {
                        $scope.event.is_aa = false;
                    }
                    console.log($scope.event);
                    $scope.save();
                }, function (e) {
                    console.log(e);
                });
            }
            if ($rootScope.getObject("event_update" + $routeParams.id)) {
                $scope.event = $rootScope.getObject("event_update" + $routeParams.id);
                $scope.event.start_time = moment($scope.event.start_time).toDate();
                $scope.event.end_time = moment($scope.event.end_time).toDate();
            } else {
                init();
            }
            $http({
                url: $rootScope.url_prefix + "users/clusters",
                method: "GET",
                params: {user_id: $rootScope.user_id, token: $rootScope.token}
            }).then(function (response) {
                data = response.data;
                $scope.clusters = data.clusters;
                $scope.qq_bind = data.qq_bind;
                //初始化之后存入缓存
                $scope.save();
            }, function (e) {
                console.log(e);
            });


            // 选择项目
            $scope.category_pick = function () {
                var dialog = ngDialog.open({
                    template: '/static/app/templates/event/category_picker.html',
                    className: 'ngdialog-theme-plain page_category_picker',
                    appendTo: '#event_create',
                    controller: 'CategoryPickerController',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {
                    $scope.event.category = data.value;
                    $scope.save();
                });
            }

            // 选择周期
            $scope.cycle_pick = function () {
                var dialog = ngDialog.open({
                    template: '/static/app/templates/event/cycle_picker.html',
                    className: 'ngdialog-theme-plain ngdialog_page',
                    appendTo: '#event_create',
                    controller: 'CyclePickerController',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {

                    $scope.event.days = data.value;
                    if (data.value) {
                        $scope.event.day_show = "";
                        for (var i = 0; i < $scope.event.days.length; i++) {
                            $scope.event.day_show += $scope.days[$scope.event.days[i]] + ",";
                        }
                        $scope.event.day_show = $scope.event.day_show.substr(0, $scope.event.day_show.length - 1)
                        $scope.event.is_cycle = true;
                    }

                    console.log($scope.event.day_show);
                    $scope.save();
                });
            }

            $scope.location_set = function () {
                $location.path("/location");
                $scope.save();
            }
            $scope.fee_set = function () {
                $scope.event.is_aa = false;
                $scope.save();
            }
            // AA制
            $scope.toggle_aa_set = function (t) {
                if (t == 2) {
                    $scope.event.is_aa = !$scope.event.is_aa;
                    if ($scope.event.is_aa) {
                        $scope.event.fee = null;
                    }
                } else {
                    $scope.event.is_aa = false;
                }

            }
            $scope.time_type_set = function (type) {
                if (type == 1) {
                    $scope.event.is_cycle = false;
                    $scope.event.day = null;
                }
                else {
                    $scope.event.is_cycle = true;
                    $scope.cycle_pick();
                }
            }
            $scope.is_start_time_setting = false;
            $scope.is_end_time_setting = false;
            // 设置开始时间
            $scope.set_start_time = function () {
                $("#start_time_in").focus();
            };
            // 设置开始完毕
            $scope.start_time_change = function () {
                var date = $scope.event.start_time;
                $scope.time_min = moment(date).format("YYYY-MM-DDTHH:mm:ss");

                var ed = moment(date).add(2, "hours");
                $scope.event.end_time = ed.toDate();
                $scope.save();
            }
            // 设置结束事件
            $scope.set_end_time = function () {
                $("#end_time_in").focus();
            }

            $scope.qq_select = function (qq) {
                if (!$scope.event.publish_qq_list) {
                    $scope.event.publish_qq_list = [];
                }
                if ($scope.event.publish_qq_list.toString().indexOf(qq) < 0) {
                    $scope.event.publish_qq_list.push(qq);
                } else {
                    //$scope.event.publish_qq_list.pop(qq);
                }
                console.log($scope.event.publish_qq_list);
                $scope.save();
            }
            $scope.qq_selected = function (qq) {
                if (!$scope.event) {
                    return;
                }
                if (!$scope.event.publish_qq_list) {
                    $scope.event.publish_qq_list = [];
                }
                if ($scope.event.publish_qq_list.toString().indexOf(qq) >= 0)
                    return true;
                else
                    return false;
            }
            $scope.submit_enable = false;
            $scope.check_submit_enable = function () {
                console.log($rootScope);
                $scope.submit_enable = $scope.event.club;
                console.log($scope.submit_enable);
            }

            // 下一步
            $scope.submit = function () {

                var qqs = $scope.event.publish_qq_list.toString();
                qqs = qqs.substr(0, qqs.length);

                m_params = {
                    user_id: $rootScope.user_id,
                    token: $rootScope.token,
                    name: $scope.event.name,
                    category: $scope.event.category,
                    start_time: moment($scope.event.start_time).unix(),
                    end_time: moment($scope.event.end_time).unix(),
                    fee: $scope.event.fee,
                    is_aa: $scope.event.is_aa,
                    members_count_limit: $scope.event.members_count_limit,
                    place_num: $scope.event.place_num,
                    mobile: $scope.event.mobile,
                    venue_title: $scope.event.location.title,
                    venue_address: $scope.event.location.address,
                    venue_phone: $scope.event.location.phone,
                    venue_city: $scope.event.location.city,
                    venue_lng: $scope.event.location.point.lng,
                    venue_lat: $scope.event.location.point.lat,
                    clusters: qqs,
                    is_cycle: $scope.event.is_cycle,
                    introduce: $scope.event.introduce,

                }
                if ($scope.event.days) {
                    m_params.days = $scope.event.days.toString().substr(0, $scope.event.days.toString().length);
                }

                $http({
                    url: $rootScope.url_prefix + "events/update/" + $routeParams.id,
                    method: "POST",
                    params: m_params
                }).success(function (data) {
                    localStorage.removeItem("event_update" + $routeParams.id);
                    $location.path("/events/show/" + $scope.event.id);
                }).error(function (e) {
                    console.log(e);
                });
            };

            $scope.bind_show = function () {
                if ($scope.qq_bind) {
                    $location.path("/clubs/create_step3");
                } else {
                    var dialog = ngDialog.open({
                        template: 'band_qq',
                        className: 'ngdialog-theme-plain ngdialog_page',
                        appendTo: '#event_create'
                    });
                    dialog.closePromise.then(function (data) {
                        // 接受报名结果
                        if (data.value) {
                            $scope.save();
                            $location.path("/clubs/create_step2");
                        }
                    });

                }
            }
            if ($location.search().from && $location.search().from == "bind_qq") {
                // 从后台拿QQ列表
            }
            ;
        }]);

// 类别选择
eventController.controller('CategoryPickerController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {
            $scope.category_list_1 = ["羽毛球", "篮球", "网球", "足球", "高尔夫", "乒乓球"];

            $scope.category_list_2 = ["骑行", "爬山", "跑步", "聚餐", "唱歌"];

            $scope.next_state = false;
            $scope.category = null;
            $scope.checkNextEnable = function () {
                if ($scope.categories.length >= 0 || $scope.other) {
                    $scope.next_state = true;
                }
            }
            $scope.categories = [];
            $scope.append_tag = function (tag) {
                var categories_copy = [];
                var has = null;
                for (var i = 0; i < $scope.categories.length; i++) {
                    if ($scope.categories[i] == tag) {
                        has = true;
                        continue;
                    }
                    categories_copy.push($scope.categories[i]);
                }
                $scope.categories = categories_copy;
                if (!has && $scope.categories.length < 3) {
                    $scope.categories.push(tag);
                }
                $scope.checkNextEnable();
            }
            $scope.has_me = function (c) {
                for (var i = 0; i < $scope.categories.length; i++) {
                    if ($scope.categories[i] == c) {
                        return "selected";
                    }
                }
            }

            $scope.finish = function () {
                if ($scope.other)
                    $scope.categories.push($scope.other);
                var tags = $scope.categories;
                var re_tags = "";
                for (var i = 0; i < tags.length; i++) {
                    re_tags += tags[i] + ","
                }
                re_tags = re_tags.substr(0, re_tags.length - 1);
                $scope.closeThisDialog(re_tags);
            }


        }]);

// 类别选择
eventController.controller('CyclePickerController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {

            $scope.days = [
                {id: 0, day: "周一"},
                {id: 1, day: "周二"},
                {id: 2, day: "周三"},
                {id: 3, day: "周四"},
                {id: 4, day: "周五"},
                {id: 5, day: "周六"},
                {id: 6, day: "周日"}
            ]
            $scope.next_state = false;

            $scope.checkNextEnable = function () {
                if ($scope.ds.length >= 0) {
                    $scope.next_state = true;
                }
            }
            $scope.ds = new Array();
            $scope.append_day = function (day_id) {
                console.log(day_id);
//        var days_copy = [];
//        var has = null;
//        for(var i=0; i< $scope.ds.length; i++){
//            if($scope.ds[i] == day_id){
//                has = true;
//                continue;
//            }
//            days_copy.push($scope.ds[i]);
//        }
//        $scope.ds = days_copy;
//        console.log($scope.ds);
//        if(!has){
//            $scope.ds.push(day_id);
//        }
                if ($scope.ds.toString().indexOf(day_id) >= 0) {
                    $scope.ds.pop(day_id);
                } else {
                    $scope.ds.push(day_id);
                }
                $scope.ds.sort();
                console.log($scope.ds);
                $scope.checkNextEnable();
            }
            $scope.has_me = function (c) {
                for (var i = 0; i < $scope.ds.length; i++) {
                    if ($scope.ds[i] == c) {
                        return "selected";
                    }
                }
            }

            $scope.finish = function () {
                $scope.closeThisDialog($scope.ds);
            }

        }]);


eventController.controller('LocationController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {
            $scope.result_returned = false;
            $scope.pois_show = false;
            $scope.search_value = "";

            var map = new BMap.Map("l-map");
            var point = new BMap.Point(116.404, 39.915);
            map.centerAndZoom(point, 15);

            var marker = new BMap.Marker(point);// 创建标注
            map.addOverlay(marker);

            map.addEventListener("dragend", function () {

                $scope.pois_show = true;
                var center = map.getCenter();
                console.log("地图中心点变更为：" + center.lng + ", " + center.lat);
                var pt = new BMap.Point(center.lng, center.lat);
                marker.setPosition(pt);
                var geoc = new BMap.Geocoder();
                geoc.getLocation(pt, function (rs) {
                    // var addComp = rs.addressComponents;
                    //alert(addComp.province + ", " + addComp.city + ", " + addComp.district + ", " + addComp.street + ", " + addComp.streetNumber);
                    $scope.current_address = rs.address;
                    console.log($scope.current_address);
                    $scope.near_pois = rs.surroundingPois;
                    console.log($scope.near_pois);
                    $scope.$apply();
                });
            });


            $scope.search = function () {
                $scope.pois_show = false;

                if ($scope.search_value == undefined) {
                    // map.centerAndZoom(point, 15);
                    $scope.result_returned = false;
                    map.reset();
                } else {
                    var options = {
                        onSearchComplete: function (results) {
                            if (local.getStatus() == BMAP_STATUS_SUCCESS) {
                                // 判断状态是否正确
                                var s = [];
                                for (var i = 0; i < results.getCurrentNumPois(); i++) {
                                    s.push(results.getPoi(i));
                                    console.log(results.getPoi(i));
                                }

                                $scope.search_pois = s;
                                console.log($scope.search_pois);
                                $scope.result_returned = true;
                                $scope.$apply();
                            }
                        }
                    };
                    var local = new BMap.LocalSearch(map, options);
                    local.search($scope.search_value);

                }
            }
            $scope.finish = function (poi) {
                var event = $rootScope.getObject("event_creating");
                event.location = poi;
                $rootScope.putObject("event_creating", event);
                $rootScope.back();
            }

        }]);


/************************************ 查：显示 *************************************/

eventController.controller('EventListController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http', 'ngDialog',
        function ($scope, $rootScope, $location, $routeParams, $http, ngDialog) {
            $scope.events = [];

            $scope.category_list = ["羽毛球", "篮球", "网球", "足球", "高尔夫", "乒乓球", "骑行", "爬山", "跑步", "聚餐", "唱歌"];

            $scope.city_selected = "北京市";
            $scope.cur_city = $scope.city_selected;
            $scope.filter_category = "全部";
            $scope.filter_weekday = "全部";
            $scope.filter_order = '默认排序';
            $scope.load = function () {
                var m_params = {
                    user_id: $rootScope.user_id,
                    token: $rootScope.token
                };
                if ($scope.city_selected) {
                    m_params.city = $scope.city_selected;
                }
                m_params.category = $scope.filter_category;
                m_params.weekday = $scope.filter_weekday;
                m_params.order = $scope.filter_order;
                $http({
                    url: $rootScope.url_prefix + "events",
                    method: "GET",
                    params: m_params
                }).success(function (data) {
                    $scope.events = data.events;
                    var weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
                    for (var i = 0; i < $scope.events.length; i++) {
                        if (moment.unix($scope.events[i].start_time).date() == moment.unix($scope.events[i].end_time).date()) {
                            $scope.events[i].time_str = moment.unix($scope.events[i].start_time).format('MM-DD HH:mm')
                                + " ~ " + moment.unix($scope.events[i].end_time).format('HH:mm')
                                + " (" + weekdays[$scope.events[i].weekday] + ")";
                        } else {
                            $scope.events[i].time_str = moment.unix($scope.events[i].start_time).format('MM-DD HH:mm')
                                + " ~ " + moment.unix($scope.events[i].end_time).format('MM-DD HH:mm');
                        }
                        if ($scope.category_list.indexOf($scope.events[i].category) >= 0) {
                            $scope.events[i].category_img = $scope.events[i].category;
                        } else {
                            $scope.events[i].category_img = "其他";
                        }
                    }

                    $scope.shareData = {
                        title: '运动99',
                        desc: '更多详情请关注公众号:\r\nyundong99',
                        link: $rootScope.url_prefix + "#/events",
                        imgUrl: $rootScope.url_prefix + '/static/app/img/headimgs/logo.png'
                    };
                    wx.ready(function () {
                        wx.onMenuShareAppMessage($scope.shareData);
                        wx.onMenuShareTimeline($scope.shareData);
                        wx.onMenuShareQQ($scope.shareData);
                        wx.onMenuShareWeibo($scope.shareData);
                    });
                }).error(function () {
                    $rootScope.alert("加载活动请求失败, 请刷新!")
                });
            }
            $scope.load();

            // 选择项目
            $scope.to_event_show = function (event_id) {
                $location.path("/events/show/" + event_id);
            }
            $scope.city_pick = function () {

                if ($scope.city_pick_opened) {
                    ngDialog.closeAll();
                    $scope.city_pick_opened = false;
                } else {
                    $scope.city_pick_opened = true;
                    var dialog = ngDialog.open({
                        template: '/static/app/templates/event/city_picker.html',
                        className: 'ngdialog-theme-plain',
                        appendTo: '#event_list',
                        controller: 'CityPickerController',
                        closeByDocument: true,
                        closeByEscape: true,
                        showClose: true,
                        scope: $scope
                    });

                    dialog.closePromise.then(function (data) {
                        $scope.city_pick_opened = false;
                        if (data.value && data.value != "$document") {
                            console.log(data.value);
                            $scope.city_selected = data.value;
                            $scope.load();
                        }

                    });
                }
            }
            $scope.filter_category_pick = function () {

                var dialog = ngDialog.open({
                    template: '/static/app/templates/event/filter_category.html',
                    className: 'ngdialog-theme-plain',
                    appendTo: '#event_list',
                    controller: 'FilterCategoryController',
                    closeByDocument: true,
                    closeByEscape: true,
                    showClose: true,
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {
                    $scope.category_pick_opened = false;
                    if (data.value && data.value != "$document") {
                        $scope.filter_category = data.value;
                        ngDialog.closeAll();
                        $scope.filter_pick();
                    }
                });
            }
            $scope.filter_weekday_pick = function () {
                var dialog = ngDialog.open({
                    template: '/static/app/templates/event/filter_weekday.html',
                    className: 'ngdialog-theme-plain',
                    appendTo: '#event_list',
                    controller: 'FilterWeekdayController',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {
                    $scope.category_pick_opened = false;
                    if (data.value && data.value != "$document") {
                        $scope.filter_weekday = data.value;
                        ngDialog.closeAll();
                        $scope.filter_pick();
                    }
                });
            }

            $scope.filter_order_pick = function () {
                var dialog = ngDialog.open({
                    template: '/static/app/templates/event/filter_order.html',
                    className: 'ngdialog-theme-plain',
                    appendTo: '#event_list',
                    controller: 'FilterOrderController',
                    closeByDocument: true,
                    closeByEscape: true,
                    showClose: true,
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {
                    $scope.category_pick_opened = false;
                    if (data.value && data.value != "$document") {
                        $scope.filter_order = data.value;
                        ngDialog.closeAll();
                        $scope.filter_pick();
                    }
                });
            }
            $scope.finish = function () {

            }
            // 选择项目
            $scope.filter_pick = function () {
                if ($scope.category_pick_opened) {
                    console.log($scope.category_pick_opened);
                    ngDialog.closeAll();
                    $scope.category_pick_opened = false;
                } else {
                    $scope.category_pick_opened = true;
                    var dialog = ngDialog.open({
                        template: '/static/app/templates/event/filter_picker.html',
                        className: 'ngdialog-theme-plain',
                        appendTo: '#event_list',
                        controller: 'FilterPickerController',
                        closeByDocument: true,
                        closeByEscape: true,
                        showClose: true,
                        scope: $scope
                    });
                    dialog.closePromise.then(function (data) {
                        $scope.category_pick_opened = false;
                        if (data.value && data.value != "$document") {
                            if (data.value == 1) {
                                $scope.filter_category_pick();
                            } else if (data.value == 2) {
                                $scope.filter_weekday_pick();
                            } else if (data.value == 3) {
                                $scope.filter_order_pick();
                            } else {
                                $scope.load();
                            }
                        }
                    });
                }
            }


        }]);


eventController.controller('CityPickerController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {

            $scope.main_cities = ["北京市", "上海市", "广州", "深圳"];
            $scope.cur_city = "北京市";
            $http({
                url: "/cities",
                method: "GET"
            }).success(function (data) {
                console.log(data);
                $scope.cities = data.cities;
            }).error(function () {

            });
        }]);


eventController.controller('FilterPickerController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {

            $scope.cities = ["北京", "上海", "广州", "厦门"];
            $scope.cur_city = "北京";
        }]);

eventController.controller('FilterCategoryController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {

            $scope.bool_categories = ["羽毛球", "网球", "篮球", "乒乓球", "高尔夫球", "足球"];
            $scope.out_categories = ["骑行", "爬山", "跑步", "其他"];
        }]);

eventController.controller('FilterWeekdayController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {

            $scope.weekdays = ["全部", "周一", "周二", "周三", "周四", "周五", "周六", "周日"];


        }]);
eventController.controller('FilterOrderController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {

        }]);


eventController.controller('EventPublishedController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http', 'ngDialog',
        function ($scope, $rootScope, $location, $routeParams, $http, ngDialog) {

            $scope.category_list = ["羽毛球", "篮球", "网球", "足球", "高尔夫", "乒乓球", "骑行", "爬山", "跑步", "聚餐", "唱歌"];

            $scope.page = "published";
            $scope.events = [];

            $scope.load = function () {
                var m_params = {};
                if ($scope.city_selected) {
                    m_params.city = $scope.city_selected;
                }
                $http({
                    url: $rootScope.url_prefix + "events/mine",
                    method: "GET",
                    params: {
                        user_id: $rootScope.user_id,
                        token: $rootScope.token,
                        page: "published"
                    }
                }).success(function (data) {
                    $scope.events = data.events;
                    var weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
                    for (var i = 0; i < $scope.events.length; i++) {
                        if (moment.unix($scope.events[i].start_time).date() == moment.unix($scope.events[i].end_time).date()) {
                            $scope.events[i].time_str = moment.unix($scope.events[i].start_time).format('MM-DD HH:mm')
                                + " ~ " + moment.unix($scope.events[i].end_time).format('HH:mm')
                                + " (" + weekdays[$scope.events[i].weekday] + ")";
                        } else {
                            $scope.events[i].time_str = moment.unix($scope.events[i].start_time).format('MM-DD HH:mm')
                                + " ~ " + moment.unix($scope.events[i].end_time).format('MM-DD HH:mm');
                        }
                        if ($scope.category_list.indexOf($scope.events[i].category) >= 0) {
                            $scope.events[i].category_img = $scope.events[i].category;
                        } else {
                            $scope.events[i].category_img = "其他";
                        }
                    }
                }).error(function () {
                    $rootScope.alert("加载活动请求失败, 请刷新!")
                });
            }
            $scope.load();
            $scope.to_event_show = function (event_id) {
                $location.path("/events/show/" + event_id);
            }
            $scope.finish = function () {

            }
        }]);


eventController.controller('EventJoinedController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http', 'ngDialog',
        function ($scope, $rootScope, $location, $routeParams, $http, ngDialog) {
            $scope.page = "joined";
            $scope.events = [];

            $scope.category_list = ["羽毛球", "篮球", "网球", "足球", "高尔夫", "乒乓球", "骑行", "爬山", "跑步", "聚餐", "唱歌"];

            $scope.load = function () {

                $http({
                    url: $rootScope.url_prefix + "events/mine",
                    method: "GET",
                    params: {
                        user_id: $rootScope.user_id,
                        token: $rootScope.token,
                        page: "joined"
                    }
                }).success(function (data) {
                    $scope.events = data.events;
                    var weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
                    for (var i = 0; i < $scope.events.length; i++) {
                        if (moment.unix($scope.events[i].start_time).date() == moment.unix($scope.events[i].end_time).date()) {
                            $scope.events[i].time_str = moment.unix($scope.events[i].start_time).format('MM-DD HH:mm')
                                + " ~ " + moment.unix($scope.events[i].end_time).format('HH:mm')
                                + " (" + weekdays[$scope.events[i].weekday] + ")";
                        } else {
                            $scope.events[i].time_str = moment.unix($scope.events[i].start_time).format('MM-DD HH:mm')
                                + " ~ " + moment.unix($scope.events[i].end_time).format('MM-DD HH:mm');
                        }

                        if ($scope.category_list.indexOf($scope.events[i].category) >= 0) {
                            $scope.events[i].category_img = $scope.events[i].category;
                        } else {
                            $scope.events[i].category_img = "其他";
                        }
                    }
                }).error(function () {
                    $rootScope.alert("加载活动请求失败, 请刷新!")
                });
            }
            $scope.load();

            $scope.to_event_show = function (event_id) {
                $location.path("/events/show/" + event_id);
            }

        }]);


eventController.controller('EventShowController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http', 'ngDialog',
        function ($scope, $rootScope, $location, $routeParams, $http, ngDialog) {

            $scope.category_list = ["羽毛球", "篮球", "网球", "足球", "高尔夫", "乒乓球", "骑行", "爬山", "跑步", "聚餐", "唱歌"];

            $scope.load = function () {
                $scope.cancel_enable = false;
                $scope.join_enable = false;
                $scope.exit_enable = false;
                $http({
                    url: "/events/" + $routeParams.id,
                    method: "GET",
                    params: {user_id: $rootScope.user_id, token: $rootScope.token}
                }).success(function (data) {
                    console.log(data);
                    $scope.event = data.event;
                    var weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
                    if (moment.unix($scope.event.start_time).date() == moment.unix($scope.event.end_time).date()) {
                        $scope.event.time_str = moment.unix($scope.event.start_time).format('YYYY-MM-DD HH:mm')
                            + " ~ " + moment.unix($scope.event.end_time).format('HH:mm')
                            + " (" + weekdays[$scope.event.weekday] + ")";
                        $scope.event.share_time_str = moment.unix($scope.event.start_time).format('MM-DD HH:mm')
                            + " ~ " + moment.unix($scope.event.end_time).format('HH:mm')
                            + " (" + weekdays[$scope.event.weekday] + ")";
                    } else {
                        $scope.event.time_str = moment.unix($scope.event.start_time).format('YYYY-MM-DD HH:mm')
                            + " ~ " + moment.unix($scope.event.end_time).format('YYYY-MM-DD HH:mm');
                        $scope.event.share_time_str = moment.unix($scope.event.start_time).format('YYYY-MM-DD HH:mm')
                            + " ~ " + moment.unix($scope.event.end_time).format('YYYY-MM-DD HH:mm');

                    }

                    if ($scope.category_list.indexOf($scope.event.category) >= 0) {
                        $scope.event.category_img = $scope.event.category;
                    } else {
                        $scope.event.category_img = "其他";
                    }

                    if ($scope.event.status == -1) {
                        $scope.canceled = true;
                        return;
                    } else {
                        if (data.is_creator) {
                            $scope.cancel_enable = true;
                        }
                    }

                    if (data.has_joined) {
                        $scope.exit_enable = true;
                        $scope.join_count = data.join_count;
                    } else {
                        $scope.join_enable = true;
                    }

                    $scope.shareData = {
                        title: $scope.event.name,
                        desc: '时间:' + $scope.event.share_time_str + "\r\n地点:" + $scope.event.venue.title,
                        link: $rootScope.url_prefix + "#/events/show/" + $routeParams.id,
                        imgUrl: $rootScope.url_prefix + '/static/app/img/headimgs/logo.png'
                    };
                    wx.ready(function () {
                        wx.onMenuShareAppMessage($scope.shareData);
                        wx.onMenuShareTimeline($scope.shareData);
                        wx.onMenuShareQQ($scope.shareData);
                        wx.onMenuShareWeibo($scope.shareData);
                    });
                }).error(function (e) {
                    console.log(e);
                });
            };
            $scope.load();
            $scope.to_club = function (club_d) {
                $location.path("/clubs/show/" + club_d);
            }
            $scope.to_members = function () {
                $location.path("/events/members/" + $scope.event.id);
            }
            $scope.cancel = function () {
                var dialog = ngDialog.open({
                    template: 'cancel',
                    className: 'ngdialog-theme-plain ngdialog_page',
                    appendTo: '#event',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {
                    $scope.event.category = data.value;
                    if (data.value == 1) {
                        $http({
                            url: "/events/" + $scope.event.id + "/cancel",
                            method: "POST"
                        }).success(function (data) {
                            console.log(data);
                            if (data.code == 1) {
                                $scope.canceled = true;
                                $scope.cancel_enable = false;
                                $rootScope.alert("取消活动成功");
                            }
                        }).error(function () {

                        });
                    }
                });

            };

            $scope.update = function () {
                $location.path("/events/update/" + $routeParams.id);
            }

            $scope.join = function () {
                var dialog = ngDialog.open({
                    template: 'join',
                    className: 'ngdialog-theme-plain join_page',
                    appendTo: '#event',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {
                    if (data.value > 0) {
                        $http({
                            url: $rootScope.url_prefix + "events/" + $scope.event.id + "/join",
                            method: "POST",
                            params: {
                                user_id: $rootScope.user_id,
                                token: $rootScope.token,
                                join_count: data.value,
                                exit_count: 0
                            }
                        }).success(function (data) {
                            if (data.code == "4002") {
                                $rootScope.alert("人数超出限制，报名失败");
                            }
                            $scope.load();
                        }).error(function (data) {
                            console.log(data);
                        });
                    }
                });

            };

            $scope.exit = function () {
                $http({
                    url: $rootScope.url_prefix + "events/" + $scope.event.id + "/join",
                    method: "POST",
                    params: {
                        user_id: $rootScope.user_id,
                        token: $rootScope.token,
                        join_count: 0,
                        exit_count: $scope.join_count
                    }
                }).success(function (data) {
                    console.log(data);
                    if (data.code == 1) {
                        $scope.exit_enable = false;
                        $scope.join_enable = true;
                        $scope.load();
                    }
                }).error(function (data) {
                    console.log(data);
                });
            }

        }]);


eventController.controller('EventMembersController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http', 'ngDialog',
        function ($scope, $rootScope, $location, $routeParams, $http, ngDialog) {
            $scope.event_id = $routeParams.id;
            var load = function () {
                $http({
                    url: $rootScope.url_prefix + "events/" + $routeParams.id + "/members",
                    method: "GET",
                    params: {user_id: $rootScope.user_id, token: $rootScope.token}
                }).success(function (data) {
                    console.log(data);
                    $scope.managers = data.managers;
                    for (var i = 0; i < $scope.managers.length; i++) {
                        console.log($scope.managers[i]);
                        if ($scope.managers[i].id == $rootScope.user_id) {
                            $scope.is_manager = true;
                        }
                    }
                    $scope.members = data.members;
                }).error(function () {

                });
            }
            load();

            $scope.ids = [];
            $scope.index_list = [];
            $scope.nicknames = [];
            $scope.toggle_select = function (index) {

                if (index in $scope.index_list) {
                    $scope.index_list.splice($scope.index_list.indexOf(index), 1);
                } else {
                    $scope.index_list.push(index);
                }
            }
            $scope.has_select = function (index) {
                if (index in $scope.index_list) {
                    return "selected";
                }
            }

            $scope.remove = function () {


                if ($scope.index_list.length == 0) {
                    return;
                } else {
                    for (var i = 0; i < $scope.index_list.length; i++) {
                        var m = $scope.members[$scope.index_list[i]];
                        if (m.id) {
                            $scope.ids.push(m.id);
                        } else {
                            $scope.nicknames.push(m.nickname);
                        }
                    }
                }
                var dialog = ngDialog.open({
                    template: 'remove',
                    className: 'ngdialog-theme-plain ngdialog_page',
                    appendTo: '#club_members',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {
                    console.log($scope.ids.toString());
                    if (data.value == "yes") {
                        console.log()
                        $http({
                            url: "/events/" + $routeParams.id + "/exit",
                            method: "POST",
                            params: {
                                ids: $scope.ids.toString(),
                                nicknames: $scope.nicknames.toString()
                            }
                        }).success(function (data) {
                            console.log(data);
                            if (data.code == 1) {
                                $rootScope.alert("删除成功成功");
                                window.history.back()
                            }
                        }).error(function () {

                        });
                    }
                });

            };

            $scope.add_picker = function () {
                //$scope.mate_count = 0;
                var dialog = ngDialog.open({
                    template: 'add',
                    className: 'ngdialog-theme-plain add_member_picker',
                    appendTo: '#club_members',
                    scope: $scope
                });
                dialog.closePromise.then(function (data) {

                    if (data.value != "$document") {
                        $scope.mate_count = data.value.mate_count;
                        if (!$scope.mate_count) {
                            $scope.mate_count = 0;
                        }
                        $http({
                            url: "/events/" + $routeParams.id + "/join",
                            method: "POST",
                            params: {
                                user_id: $rootScope.user_id,
                                token: $rootScope.token,
                                nickname: data.value.name,
                                join_count: parseInt($scope.mate_count) + 1
                            }
                        }).success(function (data) {
                            console.log(data);
                            if (data.code == 1) {
                                $rootScope.alert("添加成功");
                            } else {
                                $rootScope.alert("添加失败");
                            }
                            window.history.back()
                        }).error(function () {
                            $rootScope.alert("添加失败");
                        });
                    }
                });

            }


        }]);


eventController.controller('NavigateController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http',
        function ($scope, $rootScope, $location, $routeParams, $http) {
            // 获得活动地址

            $http({
                url: $rootScope.url_prefix + "events/" + $routeParams.id,
                method: "GET",
                params: {user_id: $rootScope.user_id, token: $rootScope.token}
            }).success(function (data) {
                $scope.venue = data.event.venue;
                var map = new BMap.Map("map");
                var lng = $scope.venue.coordinate[0];
                var lat = $scope.venue.coordinate[1];
                var point = new BMap.Point(lng, lat);
                map.centerAndZoom(point, 15);
                var marker = new BMap.Marker(point);// 创建标注
                map.addOverlay(marker);
            }).error(function () {

            });

        }]);