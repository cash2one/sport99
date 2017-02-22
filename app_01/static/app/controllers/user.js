var userController = angular.module('userController', []);

// 报名活动， 可带入
userController.controller('UserShowController',
	['$scope', '$rootScope', '$location', '$http', '$cookies', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $location, $http, $cookies, $routeParams, ngDialog){

    $scope.user = {}
    // 选择项目
    $http({
        url: "/users/show/" + $rootScope.user_id,
        method: "GET",
        params: {
            user_id: $rootScope.user_id,
            token: $rootScope.token
        }
    }).success(function(data){
        $scope.user = data.user;
        if($scope.user.sex == 1){
            $scope.user.sex = "男";
        }else{
            $scope.user.sex = "女";
        }
        console.log(data);
    }).error(function(e){
        console.log(e);
    });

    $scope.to_update = function(key){
        $rootScope.update_filed = key;
        $rootScope.update_value= $scope.user[key];
        var dialog = ngDialog.open({
            template: '/static/app/templates/user/update.html',
            className: 'ngdialog-theme-plain',
            appendTo: '#user_show',
            controller:  'UserUpdateController',
            scope: $scope
        });
        dialog.closePromise.then(function (data){
            console.log(data.value);
            if(data.value){
                $scope.user[$rootScope.update_filed] = $rootScope.update_value;
                // console.log($scope.user);
            }
            $rootScope.update_filed = null;
            $rootScope.update_value = null;

        });
    }
    $scope.to_update_qq = function(){
        $location.url("/clubs/create_step2?from=user");
    }
    $scope.finish = function(){
        var m_params = $scope.user;
        m_params.token = $rootScope.token;
        m_params.user_id = $rootScope.user_id;
        $http({
            url: "/users/update/" + $rootScope.user_id,
            method: "POST",
            params: m_params
        }).success(function(data){
            console.log(data);
            if(data.code == 1){
                $rootScope.alert("用户信息修改成功");
            }else{
                $rootScope.alert("用户信息修改失败");
            }
        }).error(function(e){
            console.log(e);
        });
    };
}]);


userController.controller('UserUpdateController',
	['$scope', '$rootScope', '$location', '$http', '$cookies', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $location, $http, $cookies, $routeParams, ngDialog){
    $scope.page_name = "创建俱乐部";
        //$scope.update_value = $rootScope.update_value;
        $scope.change = function(d){
            $rootScope.update_value = d;
        }
        $scope.sex_set = function(d){
            $rootScope.update_value = d;
        }
}]);


userController.controller('LoadingController',
    ['$scope', '$location', '$cookies', '$routeParams', '$http', '$rootScope',
    function($scope, $location, $cookies, $routeParams, $http, $rootScope){

//    if($rootScope.wx_client){
//        var this_url = window.location.toString();
//        if(this_url.indexOf("code")>0){
//            var code1 = this_url.split("?")[1].split("&")[0].split("=")[1];
//
//            $http({
//                url: "/api/wx/auth",
//                method: "GET",
//                params: {code: code1}
//            }).success(function(date){
//                alert(date);
//                $rootScope.user_id = d.user_id;
//                $rootScope.token = d.token;
//                localStorage.user_id = $rootScope.user_id;
//                localStorage.token = $rootScope.token;
//                window.location = localStorage.login_in_path;
//            }).error(function(date){
//                $rootScope.alert("页面初始化错误，请刷新页面重新加载");
//                alert("页面初始化错误，请刷新页面重新加载"+d)
//            });
//        }else{
//            // TODO 跳转到目标页
//        }
//
//    }
    if($location.path() == "/success" ){
        $rootScope.user_id = $location.search().user_id;
        $rootScope.token = $location.search().token;
        localStorage.user_id = $rootScope.user_id;
        localStorage.token = $rootScope.token;
        // alert(localStorage.login_in_path);
        window.location = localStorage.login_in_path;
    }
}]);