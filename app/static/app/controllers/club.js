var clubController = angular.module('clubController', []);

// 报名活动， 可带入
clubController.controller('ClubCreateStep1Controller',
	['$scope', '$rootScope', '$location', '$http', '$cookies', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $location, $http, $cookies, $routeParams, ngDialog){
    $scope.page_name = "创建俱乐部";
    $scope.club = {tags: "请选择"}
    if($cookies.getObject("club_creating")){
        $scope.club = $cookies.getObject("club_creating");
    }

    $scope.bg_img_set = function(){

        var dialog = ngDialog.open({ template: '/static/app/templates/club/head_bg_picker.html',
            className: 'ngdialog-theme-plain ngdialog_page',
            appendTo: '#club_create',
            controller:  'ClubHeadBGPickerController',
            scope: $scope
        });
        dialog.closePromise.then(function (data){
            // $scope.club.tags = data.value;
            var path = "/static/app/img/bgimgs/club/"+ data.value +".png"
            $scope.club.bg_img_url = path;
            document.getElementById("upload_container").style.backgroundImage = "url("+ path +")";
            $cookies.putObject("club_creating", $scope.club);
        });
    }
    if($scope.club.bg_img_url){
        document.getElementById("upload_container").style.backgroundImage = "url("+ $scope.club.bg_img_url +")";
    }
    // 选择项目
    $scope.category_pick = function(){
        var dialog = ngDialog.open({ template: '/static/app/templates/club/categories_picker.html',
            className: 'ngdialog-theme-plain page_category_picker',
            appendTo: '#club_create',
            controller:  'CategoryPickerController',
            scope: $scope
        });
        dialog.closePromise.then(function (data){

            $scope.club.tags = data.value;
            console.log(data);
            $cookies.putObject("club_creating", $scope.club);
        });
    }

    // 设置俱乐部头像
    if($rootScope.load_qiniu)
        $rootScope.load_qiniu("club_logo_url/"+$rootScope.user_id, function(domain, res){
            console.log(domain);
            console.log(res);
            $scope.club.logo_url = domain + res.key + "-icon"; //获取上传成功后的文件的Url

            document.getElementById("pickfiles").src = $scope.club.logo_url;
            $cookies.putObject("club_creating", $scope.club);
        });
    else{
        $rootScope.alert("页面加载出现问题");
    }

    $scope.submit = function(){
        var club = $cookies.getObject("club_creating");

        m_params = {
            "user_id": $rootScope.user_id,
            "token": $rootScope.token,
            "name": club.name,
            "tags": club.tags,
            "logo_url": club.logo_url,
            "bg_img_url": club.bg_img_url,
            "bind_qq": club.bind_qq
        }
        $http({
            url: "/clubs",
            method: "POST",
            params: m_params
        }).success(function(d){
            console.log(d);
            if(d.code==1){

                if($cookies.get("finish_url")){
                    $location.url($cookies.get("finish_url"));
                }else{
                    $location.path("/clubs");
                }
            }
        }).error(function(d){
            console.log("创建俱乐部失败");
        })
    }


}]);

clubController.controller('ClubHeadBGPickerController',
	['$scope', '$rootScope', '$http', '$routeParams',
	function($scope, $rootScope, $http, $routeParams){
        $scope.page_name = "选择背景图片";
        $scope.img_urls = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"];

}]);


clubController.controller('ClubCreateStep2Controller',
	['$scope', '$rootScope', '$http', '$location', '$cookies', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $http, $location, $cookies, $routeParams, ngDialog){
    $scope.page_name = "创建俱乐部";

    // $scope.club = $cookies.getObject("club_creating");

    $scope.submit = function(){
        //$cookies.putObject("club_creating", $scope.club);
        $http({
            url: "users/update/" + $rootScope.user_id,
            method: "POST",
            params: {
                user_id: $rootScope.user_id,
                token: $rootScope.token,
                qq: $scope.bind_qq
            }
        }).success(function(){
            $location.url("/clubs/create_step3?from=events_create")
        }).error(function(){
            console.log("绑定QQ出错");
        });
    }
}]);


clubController.controller('ClubCreateStep3Controller',
	['$window', '$scope', '$rootScope', '$http', '$location', '$cookies', '$routeParams', 'ngDialog',
	function($window ,$scope, $rootScope, $http, $location, $cookies, $routeParams, ngDialog){
    $scope.page_name = "创建俱乐部";

    $scope.qq = '2138409857';
    $scope.copy = function(){
        // $window.clipboardData.setData("Text", $scope.qq);
        if ( window.clipboardData ) {
            window.clipboardData.setData("Text", $scope.qq);
        }else{
            alert("复制版不可用，请手动复制");
        }
    }

    $scope.submit = function(){
        $location.url("/qq_clusters?from=events_create");
    }
}]);


clubController.controller('QQClustersController',
	['$window', '$scope', '$rootScope', '$http', '$location', '$cookies', '$routeParams', 'ngDialog',
	function($window ,$scope, $rootScope, $http, $location, $cookies, $routeParams, ngDialog){

    $http({
        url: "users/clusters",
        method: "GET",
        params: {
            user_id: $rootScope.user_id,
            token: $rootScope.token
        }
    }).success(function(data){
        $scope.clusters = data.clusters
    }).error(function(){
        console.log("加载失败");
    });
    $scope.submit = function(){
        if($location.search() && $location.search().from == "events_create"){
            $location.url("/events/create_step1?from=bind_qq");
        }

    }
}]);


clubController.controller('ClubMembersController',
	['$scope', '$rootScope', '$http', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $http, $routeParams, ngDialog){
        $http({
            url: $rootScope.url_prefix + "clubs/"+$routeParams.id+"/members",
            method: "GET",
            params: {user_id: $rootScope.user_id, token: $rootScope.token}
        }).success(function(data){
            console.log(data);
            $scope.managers = data.managers;
            $scope.members = data.members;
        }).error(function(){

        });


}]);

clubController.controller('ClubShowController',
	['$scope', '$rootScope', '$http', '$routeParams', '$location', 'ngDialog',
	function($scope, $rootScope, $http, $routeParams, $location, ngDialog){
        $scope.is_follow_enable = false;
        $http({
            url: "/clubs/show/"+$routeParams.id,
            method: "GET",
            params: {user_id: $rootScope.user_id, token: $rootScope.token}
        }).success(function(data){
            $scope.club = data.club;
            if(!$scope.club.bg_img_url || $scope.club.bg_img_url == ""){
                $scope.club.bg_img_url = "/static/app/img/bgimgs/club/P1.png"
            }
            console.log(data);
            if(data.role < 0){
                $scope.is_follow_enable = true;
            }
        }).error(function(e){
            console.log(e);
        });
        $http({
            url: "/events/club",
            method: "GET",
            params: {
                user_id: $rootScope.user_id,
                token: $rootScope.token,
                club_id: $routeParams.id
            }
        }).success(function(data){
            console.log(data);
            eval(data.events);
            data.events.forEach(function(e){
                e.start_time = moment(e.start_time*1000).format('YYYY-MM-DD HH:mm');
            });

            $scope.events = data.events;
            $scope.club.events_count= $scope.events.length;
        }).error(function(e){
            console.log(e);
        });

        $scope.follow = function(){
            $http({
                url: "/clubs/follow/"+$routeParams.id,
                method: "POST",
                params: {user_id: $rootScope.user_id, token: $rootScope.token}
            }).success(function(data){

                if(data.code == 1){
                    $scope.is_follow_enable = false;
                }
            }).error(function(e){
                console.log(e);
            });
        }


}]);

clubController.controller('ClubMineController',
	['$scope', '$rootScope', '$http', '$routeParams', '$location','$cookies', 'ngDialog',
	function($scope, $rootScope, $http, $routeParams, $location, $cookies, ngDialog){
    $scope.to_add_club = function(){
        $cookies.put("finish_url", $location.url());
        $location.path("/clubs/create_step1");
    }
    $scope.to_club_show = function(club_id){
        $location.path("/clubs/show/"+club_id);
    }
    $http({
        url: "/mine_clubs",
        method: "GET",
        params: {
            user_id: $rootScope.user_id,
            token: $rootScope.token
        }
    }).success(function(d){
        console.log(d);
        $scope.club = d.club;
        $scope.follow_clubs = d.follow_clubs;
    }).error(function(d){
        console.log("创建俱乐部失败");
    })

}]);