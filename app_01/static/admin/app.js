/**
 * Created by zhaojm on 4/22/16.
 */
templates_root = '/static/admin/templates/';

var adminApp = angular.module('adminApp', [
    'ng',
    'ngRoute',
    'ngAnimate',
    'loginCtrl',
    'eventCtrl',
    'clubCtrl'
], function ($httpProvider) {
    // Use x-www-form-urlencoded Content-Type
    $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';
    $httpProvider.defaults.headers.put['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';

});


adminApp.run(['$location', '$rootScope', '$http',
    function ($location, $rootScope, $http) {


        // 页面跳转后
        $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {
            var present_route = $location.$$path; //获取当前路由

        });


        /*********************************** 全局方法区 e***************************************/
            // 对象存储
        $rootScope.putObject = function (key, value) {
            localStorage.setItem(key, angular.toJson(value));
        };
        $rootScope.getObject = function (key) {
            return angular.fromJson(localStorage.getItem(key))
        };

        $rootScope.close_alert = function () {
            $rootScope.alert_show = null;
        };
        $rootScope.alert = function (data) {
            $rootScope.alert_show = true;
            if (data) {
                $rootScope.alert_str = data;
                setTimeout(function () {
                    $rootScope.alert_show = null;
                    $rootScope.$apply();
                }, 3000);
            } else {
                $rootScope.alert_str = "未知错误";
            }
        };

        $rootScope.check_user = function () {
            $rootScope.admin_info = $rootScope.getObject("admin_info");
            //console.log($rootScope.admin_info);
            if ($rootScope.admin_info) {
                return $rootScope.admin_info.id;
            } else {
                return false;
            }
        };


        if (!window.localStorage) {
            alert('This browser does NOT support localStorage');
        }
        if (!$rootScope.check_user()) {
            $location.path("/login");
        }


    }]);