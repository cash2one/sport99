var userController = angular.module('userController', []);

// 报名活动， 可带入
userController.controller('UserShowController',
	['$scope', '$rootScope', '$location', '$http', '$cookies', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $location, $http, $cookies, $routeParams, ngDialog){
    $scope.page_name = "创建俱乐部";
    $scope.user = {}
    // 选择项目
    $http({
        url: $rootScope.url_prefix + "api/users/show/" + $rootScope.user_id,
        method: "GET",
        params: {
            user_id: $rootScope.user_id,
            token: $rootScope.token
        }
    }).success(function(data){
        $scope.user = data.user;
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
    $scope.finish = function(){
        var m_params = $scope.user;
        m_params.token = $rootScope.token;
        m_params.user_id = $rootScope.user_id;
        m_params.head_img_url = "http://7xry52.com2.z0.glb.qiniucdn.com/IMG_5891.PNG-icon";
        $http({
            url: "/api/users/update/" + $rootScope.user_id,
            method: "GET",
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
    $scope.text = '登录成功'
    var this_url = window.location.toString();
    if(this_url.indexOf("code")>0 && $rootScope.user_id){
        //http://test.gogo2020.com/?code=0210a9bc4bf627817c73d8a5880e40e0&state=1
        var code = this_url.split("?")[1].split("&")[0].split("=")[1];

        $http({
            url: $rootScope.url_prefix + "api/wx/auth",
            method: "GET",
            params: {code: code}
        }).success(function(d){
            $rootScope.user_id = d.user_id;
            $rootScope.token = d.token;
            $cookies.put("user_id", $rootScope.user_id);
            $cookies.put("token", $rootScope.token);
            var p = $cookies.get("login_in_path");
            $cookies.remove("login_in_path");
            $location.path(p);
        }).error(function(d){
            // TODO login error
            alert('error'+d)
        });
    }else{
        console.log(404);
    }
}]);