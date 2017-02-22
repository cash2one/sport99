var eventController = angular.module('eventController', []);

// 报名活动， 可带入
eventController.controller('EventJoinController',
	['$scope', '$rootScope', '$http', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $http, $routeParams, ngDialog){

    $scope.join = function(){
        // 报名
        $http({
            url: $rootScope.url_prefix + "/events/" + $routeParams.id + "/join",
            method: "POST",
            params: {exit_count:$rootScope.exit_count, join_count: $scope.join_count, user_id: $rootScope.user_id, token: $rootScope.token}
        }).then(function(response){
            // 报名成功，通知主页面刷新
            $scope.closeThisDialog($scope.join_count);
        },function(){
            // TODO 报名失败
        });
    }
}]);

// 创建活动
eventController.controller('EventCreateStep1Controller',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies', 'ngDialog',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies, ngDialog){

	//设置头部和主页导航按钮

    var init = function(){
	    $scope.event = {}

        // 时间选择
        date = new Date();
        // dd = moment([date.getFullYear(), date.getMonth(), date.getDate(), 20, 0]);
        sd = moment([date.getFullYear(), date.getMonth(), date.getDate(), 20, 0]);
        ed = moment([date.getFullYear(), date.getMonth(), date.getDate(), 22, 0]);
        $scope.time_min = sd.toDate();

        $scope.event.start_time = sd.toDate();
        $scope.event.end_time = ed.toDate();

        $scope.event.is_cycle = false;
        $scope.event.is_aa = false;

        $scope.event.location = {};
        $scope.event.publish_qq_list = [];
        // 从服务器获取活动ID
        $http({
            url: $rootScope.url_prefix + "event_id",
            method: "GET",
            params: {user_id: $rootScope.user_id, token:$rootScope.token}
        }).then(function(response){
            data = response.data;
            $scope.event.id = data.id;
            $scope.event.clusters = data.cluster_list;
            //$scope.event.clusters = [1222,3345];

            //初始化之后存入缓存
            $cookies.putObject("event_creating", $scope.event);
        },function(e){
            console.log(e);
        });
	}
	if($cookies.getObject("event_creating")){
        $scope.event = $cookies.getObject("event_creating");
        $scope.event.start_time = new Date($scope.event.start_time);
	    $scope.event.end_time = new Date($scope.event.end_time);

	}else{
	    init();
	}
    $http({
        url: $rootScope.url_prefix + "users/clusters",
        method: "GET",
        params: {user_id: $rootScope.user_id, token:$rootScope.token}
    }).then(function(response){
        //data = response.data;
        data = {"clusters": [{"external_id": "111520689", "name": "ITBirds"}], "qq_bind": true, "code": 1}
        $scope.clusters = data.clusters;
        $scope.qq_bind = data.qq_bind;
        //初始化之后存入缓存
        $cookies.putObject("event_creating", $scope.event);
    },function(e){
        console.log(e);
    });
	if($scope.club== undefined){
	    $http({
            url: "mine_clubs",
            method: "GET",
            params: {
                user_id: $rootScope.user_id,
                token: $rootScope.token
            }
        }).success(function(d){
            console.log(d);
            $scope.club = d.club;
        }).error(function(d){
            console.log("创建俱乐部失败");
        })
	}
	console.log("活动》");
    console.log($scope.event);

    $scope.to_add_club = function(){
        $cookies.put("finish_url", $location.url());
        $location.path("/clubs/create_step1");
    }
    $scope.fee_set = function(){
        $scope.event.is_aa = false;
    }
    // 选择项目
    $scope.category_pick = function(){
        var dialog = ngDialog.open({ template: '/static/app/templates/event/category_picker.html',
            className: 'ngdialog-theme-plain page_category_picker',
            appendTo: '#event_create',
            controller:  'CategoryPickerController',
            scope: $scope
        });
        dialog.closePromise.then(function (data){
            $scope.event.category = data.value;
        });
    }
    $scope.days = [
        {id: 1, day: "周一"},
        {id: 2, day: "周二"},
        {id: 3, day: "周三"},
        {id: 4, day: "周四"},
        {id: 5, day: "周五"},
        {id: 6, day: "周六"},
        {id: 7, day: "周日"}
    ]
    // 选择周期
    $scope.cycle_pick = function(){
        var dialog = ngDialog.open({ template: '/static/app/templates/event/cycle_picker.html',
            className: 'ngdialog-theme-plain ngdialog_page',
            appendTo: '#event_create',
            controller:  'CyclePickerController',
            scope: $scope
        });
        dialog.closePromise.then(function (data){

            $scope.event.days = data.value;
            if(data.value){
                $scope.event.day_show = "";
                for(var i=0; i<$scope.event.days.length-1; i++){
                    $scope.event.day_show += $scope.days[$scope.event.days[i]].day+",";
                }
                $scope.event.day_show += $scope.days[$scope.event.days.length-1].day;
            }

            console.log($scope.event.day_show);
        });
    }

    $scope.location_set = function(){
        $location.path("/location");
        $cookies.putObject("event_creating", $scope.event);
    }
    // AA制
    $scope.toggle_aa_set = function(t){
        if(t == 2){
            $scope.event.is_aa = !$scope.event.is_aa;
            if($scope.event.is_aa){
                $scope.event.fee = null;
            }
        }else{
            $scope.event.is_aa = false;
        }

    }
    $scope.time_type_set = function(type){
        if(type == 1){
            $scope.event.is_cycle = false;
            $scope.event.day = null;
        }
        else{
            $scope.event.is_cycle = true;
            $scope.cycle_pick();
        }
    }
    $scope.is_start_time_setting = false;
    $scope.is_end_time_setting = false;
    // 设置开始时间
    $scope.set_start_time = function(){
        //$scope.is_start_time_setting = true;
        $("#start_time_in").focus();
    };
    // 设置开始完毕
    $scope.start_time_change = function(){
        var date = $scope.event.start_time;
        $scope.time_min = moment(date).format("YYYY-MM-DDTHH:mm:ss");

        var ed = moment(date).add(2, "hours");
        $scope.event.end_time = ed.toDate();

    }
    // 设置结束事件
    $scope.set_end_time = function(){
        //$scope.is_end_time_setting = true;
        $("#end_time_in").focus();
    }

    $scope.qq_select = function(qq){
        console.log(qq);

        if($scope.event.publish_qq_list.indexOf(qq)<0){
            $scope.event.publish_qq_list.push(qq);
        }else{
            $scope.event.publish_qq_list.pop(qq);
        }
        console.log($scope.event.publish_qq_list);
    }
    $scope.qq_selected = function(qq){
        if($scope.event.publish_qq_list.indexOf(qq)>=0)
            return true;
        else
            return false;
    }
    $scope.submit_enable = false;
    $scope.check_submit_enable = function(){
        console.log($rootScope);
        $scope.submit_enable = $scope.event.club;
        console.log($scope.submit_enable);
    }

    // 下一步
    $scope.submit = function(){
        var qqs = "";
        for(var i=0; i<$scope.event.publish_qq_list.length; i++){
            qqs =qqs+ $scope.event.publish_qq_list[i]+",";
        }
        qqs = qqs.substr(0, qqs.length-1);
        console.log(qqs);
        m_params = {
            user_id : $rootScope.user_id,
            token : $rootScope.token,
            id: $scope.event.id,
            name: $scope.event.name,
            category: $scope.event.category,
            //start_time: $scope.event.start_time,
            //end_time: $scope.event.end_time,
            start_time: moment($scope.event.start_time).format("YYYY-MM-DD HH:mm"),
            end_time: moment($scope.event.end_time).format("YYYY-MM-DD HH:mm"),
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
            club_id: $scope.club.id,
            clusters: qqs
        }

        $cookies.remove("event_creating");
        $http({
            url: $rootScope.url_prefix + "events",
            method: "POST",
            params: m_params,
            headers:{"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}
        }).success(function(data){
            // console.log(data);
            //$cookies.putObject("event", $scope.event);
            //$cookies.remove("event_creating");
            $location.path("/events/show/"+$scope.event.id);

        }).error(function(e){
            console.log(e);
        });
    };

    $scope.bind_show = function(){
        if($scope.qq_bind){
            $location.path("/clubs/create_step3");
        }else{
            var dialog = ngDialog.open({ template: 'band_qq',
                className: 'ngdialog-theme-plain',
                appendTo: '#event_create'
            });
            dialog.closePromise.then(function (data) {
                // 接受报名结果
                if(data.value){
                    $cookies.putObject("event_creating", $scope.event);
                    $location.path("/clubs/create_step2");
                }
            });

        }
    }
    if($location.search().from && $location.search().from == "bind_qq"){
        // 从后台拿QQ列表
    };
 }]);

  // 类别选择
 eventController.controller('CategoryPickerController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){
    $scope.category_list_1 = ["羽毛球", "篮球", "网球", "足球", "高尔夫", "乒乓球"];

    $scope.category_list_2 = ["骑行", "爬山", "跑步", "聚餐", "唱歌"];

    $scope.next_state = false;
    $scope.category = null;
    $scope.checkNextEnable = function(){
        if($scope.categories.length >=0 || $scope.other){
            $scope.next_state = true;
        }
    }
    $scope.categories = [];
    $scope.append_tag = function(tag){
        var categories_copy = [];
        var has = null;
        for(var i=0; i< $scope.categories.length; i++){
            if($scope.categories[i] == tag){
                has = true;
                continue;
            }
            categories_copy.push($scope.categories[i]);
        }
        $scope.categories = categories_copy;
        if(!has && $scope.categories.length<3){
            $scope.categories.push(tag);
        }
        $scope.checkNextEnable();
    }
    $scope.has_me = function(c){
        for(var i=0; i< $scope.categories.length; i++){
            if($scope.categories[i] == c){
                return "selected";
            }
        }
    }

    $scope.finish = function(){
        if($scope.other)
            $scope.categories.push($scope.other);
        var tags = $scope.categories;
        var re_tags = "";
        for(var i=0; i< tags.length; i++){
            re_tags += tags[i]+","
        }
        re_tags = re_tags.substr(0, re_tags.length-1);
        $scope.closeThisDialog(re_tags);
    }



 }]);

  // 类别选择
 eventController.controller('CyclePickerController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){

    $scope.days = [
        {id: 1, day: "周一"},
        {id: 2, day: "周二"},
        {id: 3, day: "周三"},
        {id: 4, day: "周四"},
        {id: 5, day: "周五"},
        {id: 6, day: "周六"},
        {id: 7, day: "周日"}
    ]
    $scope.next_state = false;

    $scope.checkNextEnable = function(){
        if($scope.ds.length >=0){
            $scope.next_state = true;
        }
    }
    $scope.ds = [];
    $scope.append_day = function(day_id){
        console.log(day_id);
        var days_copy = [];
        var has = null;
        for(var i=0; i< $scope.ds.length; i++){
            if($scope.ds[i] == day_id){
                has = true;
                continue;
            }
            days_copy.push($scope.ds[i]);
        }
        $scope.ds = days_copy;
        console.log($scope.ds);
        if(!has){
            $scope.ds.push(day_id);
        }
        $scope.checkNextEnable();
    }
    $scope.has_me = function(c){
        for(var i=0; i< $scope.ds.length; i++){
            if($scope.ds[i] == c){
                return "selected";
            }
        }
    }

    $scope.finish = function(){
        $scope.closeThisDialog($scope.ds);
    }

 }]);

 eventController.controller('LocationController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){
    $scope.result_returned = false;
    $scope.pois_show = false;
    $scope.search_value = "";

    var map = new BMap.Map("l-map");
    var point = new BMap.Point(116.404, 39.915);
	map.centerAndZoom(point, 15);

    var marker = new BMap.Marker(point);// 创建标注
    map.addOverlay(marker);

	map.addEventListener("dragend", function(){

	    $scope.pois_show= true;
        var center = map.getCenter();
        console.log("地图中心点变更为：" + center.lng + ", " + center.lat);
        var pt = new BMap.Point(center.lng, center.lat);
	    marker.setPosition(pt);
	    var geoc = new BMap.Geocoder();
	    geoc.getLocation(pt, function(rs){
			// var addComp = rs.addressComponents;
			//alert(addComp.province + ", " + addComp.city + ", " + addComp.district + ", " + addComp.street + ", " + addComp.streetNumber);
		    $scope.current_address = rs.address;
		    console.log($scope.current_address);
		    $scope.near_pois = rs.surroundingPois;
		    console.log($scope.near_pois);
		    $scope.$apply();
		});
    });


    $scope.search= function(){
        $scope.pois_show= false;

	    if($scope.search_value == undefined){
            // map.centerAndZoom(point, 15);
            $scope.result_returned = false;
            map.reset();
	    }else{
	        var options = {
                onSearchComplete: function(results){
                    if (local.getStatus() == BMAP_STATUS_SUCCESS){
                        // 判断状态是否正确
                        var s = [];
                        for (var i = 0; i < results.getCurrentNumPois(); i ++){
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
    $scope.finish = function(poi){
        var event = $cookies.getObject("event_creating");
        event.location = poi;
        $cookies.putObject("event_creating", event);
        $rootScope.back();
    }

 }]);


 /************************************ 查：显示 *************************************/

 eventController.controller('EventListController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies', 'ngDialog',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies, ngDialog){
    $scope.events = [];

    $scope.city_selected = "北京";
    $scope.cur_city = $scope.city_selected;
    $scope.filter_category = "全部";
    $scope.filter_weekday = "全部";
    $scope.filter_order = '默认排序';
    $scope.load = function(){
        console.log($scope.city_selected);
        console.log($scope.filter_category);
        console.log($scope.filter_weekday);
        console.log($scope.filter_order);
        var m_params = {

        };
        if($scope.city_selected){
            m_params.city = $scope.city_selected;
        }
        m_params.category = $scope.filter_category;
        m_params.weekday = $scope.filter_weekday;
        m_params.order = $scope.filter_order;
        $http({
            url: $rootScope.url_prefix + "events",
            method: "GET",
            params: m_params
        }).success(function(data){
            eval(data.events);
            data.events.forEach(function(e){
                e.start_time = moment(e.start_time*1000).format('YYYY-MM-DD HH:mm');
            });
            $scope.events = data.events;

        }).error(function(){
            $rootScope.alert("加载活动请求失败, 请刷新!")
        });
    }
    $scope.load();

    // 选择项目
    $scope.to_event_show = function(event_id){
        $location.path("/events/show/" + event_id);
    }
    $scope.city_pick = function(){

        if($scope.city_pick_opened){
            ngDialog.closeAll();
            $scope.city_pick_opened = false;
        }else{
            $scope.city_pick_opened = true;
            var dialog = ngDialog.open({ template: '/static/app/templates/event/city_picker.html',
                className: 'ngdialog-theme-plain',
                appendTo: '#event_list',
                controller:  'CityPickerController',
                closeByDocument: true,
                closeByEscape: true,
                showClose: true,
                scope: $scope
            });

            dialog.closePromise.then(function (data){
                $scope.city_pick_opened = false;
                if(data.value && data.value != "$document"){
                    console.log(data.value);
                    $scope.city_selected = data.value;
                    $scope.load();
                }

            });
        }
    }
    $scope.filter_category_pick = function(){

        var dialog = ngDialog.open({ template: '/static/app/templates/event/filter_category.html',
            className: 'ngdialog-theme-plain',
            appendTo: '#event_list',
            controller:  'FilterCategoryController',
            closeByDocument: true,
            closeByEscape: true,
            showClose: true,
            scope: $scope
        });
        dialog.closePromise.then(function (data){
            $scope.category_pick_opened = false;
            if(data.value && data.value != "$document"){
                $scope.filter_category = data.value;
                $scope.filter_pick();
            }
        });
    }
    $scope.filter_weekday_pick = function(){
        var dialog = ngDialog.open({ template: '/static/app/templates/event/filter_weekday.html',
            className: 'ngdialog-theme-plain',
            appendTo: '#event_list',
            controller:  'FilterWeekdayController',
            scope: $scope
        });
        dialog.closePromise.then(function (data){
            $scope.category_pick_opened = false;
            if(data.value && data.value != "$document"){
                $scope.filter_weekday = data.value;
                $scope.filter_pick();
            }
        });
    }

    $scope.filter_order_pick = function(){
        var dialog = ngDialog.open({ template: '/static/app/templates/event/filter_order.html',
            className: 'ngdialog-theme-plain',
            appendTo: '#event_list',
            controller:  'FilterOrderController',
            closeByDocument: true,
            closeByEscape: true,
            showClose: true,
            scope: $scope
        });
        dialog.closePromise.then(function (data){
            $scope.category_pick_opened = false;
            if(data.value && data.value != "$document"){
                $scope.filter_order = data.value;
                $scope.filter_pick();
            }
        });
    }
    $scope.finish = function(){

    }
    // 选择项目
    $scope.filter_pick = function(){
        if($scope.category_pick_opened){
            console.log($scope.category_pick_opened);
            ngDialog.closeAll();
            $scope.category_pick_opened = false;
        }else{
            $scope.category_pick_opened = true;
            var dialog = ngDialog.open({ template: '/static/app/templates/event/filter_picker.html',
                className: 'ngdialog-theme-plain',
                appendTo: '#event_list',
                controller:  'FilterPickerController',
                closeByDocument: true,
                closeByEscape: true,
                showClose: true,
                scope: $scope
            });
            dialog.closePromise.then(function (data){
                $scope.category_pick_opened = false;
                if(data.value && data.value != "$document"){
                    if(data.value == 1){
                        $scope.filter_category_pick();
                    }else if(data.value == 2){
                        $scope.filter_weekday_pick();
                    }else if(data.value == 3){
                        $scope.filter_order_pick();
                    }else{
                        $scope.load();
                    }
                }
            });
        }
    }


 }]);

eventController.controller('CityPickerController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){

    $scope.main_cities = ["北京市", "上海市", "广州", "深圳"];
    $scope.cur_city = "北京市";
    $http({
        url: "/cities",
        method: "GET"
    }).success(function(data){
        console.log(data);
        $scope.cities = data.cities;
    }).error(function(){

    });
 }]);

eventController.controller('FilterPickerController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){

    $scope.cities = ["北京", "上海", "广州", "厦门"];
    $scope.cur_city = "北京";
 }]);

 eventController.controller('FilterCategoryController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){

    $scope.bool_categories = ["羽毛球", "网球", "篮球", "高尔夫球", "足球"];
    $scope.out_categories = ["骑行", "爬山", "跑步", "其他"];
 }]);

 eventController.controller('FilterWeekdayController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){

    $scope.weekdays = ["全部", "周一", "周二", "周三",  "周四", "周五", "周六", "周日"];


 }]);
 eventController.controller('FilterOrderController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){

 }]);


eventController.controller('EventPublishedController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies', 'ngDialog',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies, ngDialog){
    $scope.page = "published";
    $scope.events = [];

    $scope.load = function(){
        var m_params = {};
        if($scope.city_selected){
            m_params.city = $scope.city_selected;
        }
        $http({
            url: $rootScope.url_prefix + "events/mine",
            method: "GET",
            params: {
                user_id: $rootScope.user_id,
                token: $rootScope.token,
                page: "joined"
            }
        }).success(function(data){
            $scope.events = data.events;
        }).error(function(){
            $rootScope.alert("加载活动请求失败, 请刷新!")
        });
    }
    $scope.load();
    $scope.to_event_show = function(event_id){
        $location.path("/events/show/" + event_id);
    }
    $scope.finish = function(){

    }
 }]);

eventController.controller('EventJoinedController',
['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies', 'ngDialog',
function($scope, $rootScope, $location, $routeParams, $http, $cookies, ngDialog){
    $scope.page = "joined";
    $scope.events = [];

    $scope.load = function(){

        $http({
            url: $rootScope.url_prefix + "events/mine",
            method: "GET",
            params: {
                user_id: $rootScope.user_id,
                token: $rootScope.token,
                page: "joined"
            }
        }).success(function(data){
            $scope.events = data.events;
        }).error(function(){
            $rootScope.alert("加载活动请求失败, 请刷新!")
        });
    }
    $scope.load();

    $scope.to_event_show = function(event_id){
        $location.path("/events/show/" + event_id);
    }

}]);



eventController.controller('EventShowController',
['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
function($scope, $rootScope, $location, $routeParams, $http, $cookies){

    $scope.cancel_enable = false;
    $scope.join_enable = false;
    $scope.exit_enable = false;

    $http({
        url: $rootScope.url_prefix + "events/"+$routeParams.id,
        method: "GET",
        params: {user_id: $rootScope.user_id, token: $rootScope.token}
    }).success(function(data){
        console.log(data);
        $scope.event = data.event;
        $scope.event.member_count = $scope.event.member_count;
        $scope.event.start_time = moment($scope.event.start_time*1000).format('YYYY-MM-DD HH:mm');
        if($scope.event.member_count == 0){
            $scope.event.percent = "0%";
        }else{
            $scope.event.percent = ($scope.event.member_count/$scope.event.member_count_limit) + "%";
        }
        if($scope.event.status == -1){
            $scope.canceled = true;
        }else{
            if(data.is_creator){
                $scope.cancel_enable = true;
            }
        }

        if(data.has_joined){
            $scope.exit_enable = true;
        }else{
            $scope.join_enable = true;
        }
    }).error(function(){

    });
    $scope.to_club = function(club_d){
        $location.path("/clubs/show/"+club_d);
    }
    $scope.to_members = function(){
        $location.path("/events/members/"+$scope.event.id);
    }
    $scope.cancel = function(){
        $http({
            url: $rootScope.url_prefix + "/events/"+$scope.event.id+"/cancel",
            method: "POST"
        }).success(function(data){
            if(data.code == 1){
                $scope.canceled = true;
                $scope.cancel_enable= false;
            }
        }).error(function(){

        });
    };

    $scope.join = function(){
        $http({
            url: $rootScope.url_prefix + "events/"+$scope.event.id+"/join",
            method: "POST",
            params:{
                user_id: $rootScope.user_id,
                token: $rootScope.token,
                join_count: 1,
                exit_count: 0
            }
        }).success(function(data){
            console.log(data);
            if(data.code == 1){
                $scope.exit_enable = true;
                $scope.join_enable = false;
            }

        }).error(function(data){
            console.log(data);
        });
    };

    $scope.exit = function(){
        $http({
            url: $rootScope.url_prefix + "events/"+$scope.event.id+"/join",
            method: "POST",
            params:{
                user_id: $rootScope.user_id,
                token: $rootScope.token,
                join_count: 0,
                exit_count: 1
            }
        }).success(function(data){
            console.log(data);
            if(data.code == 1){
                $scope.exit_enable = false;
                $scope.join_enable = true;
            }

        }).error(function(data){
            console.log(data);
        });
    }

}]);


eventController.controller('EventMembersController',
	['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
	function($scope, $rootScope, $location, $routeParams, $http, $cookies){
    $http({
        url: $rootScope.url_prefix + "events/"+$routeParams.id+"/members",
        method: "GET",
        params: {user_id: $rootScope.user_id, token: $rootScope.token}
    }).success(function(data){
        console.log(data);
        $scope.managers = data.managers;
        $scope.members = data.members;
    }).error(function(){

    });


 }]);


   // 类别选择
eventController.controller('NavigateController',
    ['$scope', '$rootScope', '$location', '$routeParams', '$http', '$cookies',
    function($scope, $rootScope, $location, $routeParams, $http, $cookies){
    // 获得活动地址

    $http({
        url: $rootScope.url_prefix + "events/"+$routeParams.id,
        method: "GET",
        params: {user_id: $rootScope.user_id, token: $rootScope.token}
    }).success(function(data){
        $scope.venue = data.event.venue;
        var map = new BMap.Map("map");
        var lng = $scope.venue.coordinate[0];
        var lat = $scope.venue.coordinate[1];
        var point = new BMap.Point(lng, lat);
        map.centerAndZoom(point, 15);
        var marker = new BMap.Marker(point);// 创建标注
        map.addOverlay(marker);
    }).error(function(){

    });

}]);