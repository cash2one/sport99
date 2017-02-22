/**
 * Created by zhaojm on 4/23/16.
 */
var loginCtrl = angular.module('loginCtrl', []);

loginCtrl.controller('LoginCtrl', function ($http, $scope, $rootScope, $location) {
    $scope.loginPost = {
        "username": "",
        "password": ""
    };
    var check_params = function (params) {
        if (params.username == "" || params.password == "") {
            console.log("username or password is empty")
            return false;
        }
        return true;
    };
    $scope.submit = function () {
        var m_params = $scope.loginPost;
        if (!check_params(m_params)) return;
        $http({
            url: "/admin/login",
            method: "POST",
            params: m_params
        }).success(function (d) {
            if (d.retcode == 0) {
                console.log(d.result);
                $rootScope.admin_info = d.result;
                $rootScope.putObject("admin_info", d.result);
                $location.path("/club/list");
            }
            else {
                console.log(d);
            }

        }).error(function (d) {
            console.log("login error");
            $location.path("/login");
        })
    };

    //if ($rootScope.check_user()) {
    //    //$location.path("/");
    //}


});
