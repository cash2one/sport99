/**
 * Created by zhaojm on 4/23/16.
 */

var clubCtrl = angular.module('clubCtrl', []);

clubCtrl.controller('ClubCreateCtrl', function ($http, $scope, $rootScope, $location) {
    $scope.user_and_club = {mobile: '', nickname: '', club_name: '', tags: ''};
    var check_params = function (params) {
        return true;
    };
    $scope.submit = function () {

        var m_params = $scope.user_and_club;
        m_params.token = $rootScope.admin_info.token;
        m_params.admin_id = $rootScope.admin_info.id;

        if (!check_params(m_params)) return;

        $http({
            url: "/admin/club/new",
            method: "POST",
            params: m_params
        }).success(function (d) {
            if (d.retcode == 0) {
                $location.path("/club/list");
            } else {
                console.log(d.errmsg);
            }

        }).error(function (d) {
            console.log("create club error");
            $location.path("/login");
        })
    };


});

clubCtrl.controller('ClubListCtrl', function ($http, $scope, $rootScope, $location) {
    $scope.clubs = [
        {"id": 1, "name": 'test1'},
        {"id": 2, "name": 'test2'},
        {"id": 3, "name": 'test3'}
    ];

    $scope.club_detail = function (club_id) {
        //console.log(club_id)
        $location.path('/club/detail/' + club_id);
    };
    $scope.club_modify = function (club_id) {
        $location.path('/club/modify/' + club_id);
    };
    $scope.club_delete = function (club_id) {
        $location.path('/club/delete/' + club_id);
    };

    var m_params = {};
    m_params.token = $rootScope.admin_info.token;
    m_params.admin_id = $rootScope.admin_info.id;

    $http({
        url: "/admin/club/list",
        method: "GET",
        params: m_params
    }).success(function (d) {
        if (d.retcode == 0) {
            console.log(d.result);
            $scope.clubs = d.result;
        } else {
            console.log(d.errmsg);
        }

    }).error(function (d) {
        console.log("get club list error");
        $location.path("/login");
    });


});

clubCtrl.controller('ClubDetailCtrl', function ($http, $scope, $rootScope, $routeParams, $location) {
    //console.log("club detail ctrl")
    $scope.user_and_club = {"user_id": "", "club_id": "", "mobile": '', "nickname": '', "club_name": '', "tags": ''};

    $scope.event_create = function () {
        $rootScope.putObject("user_and_club", $scope.user_and_club);
        $location.path('/event/create');
    };

    $scope.club_detail = function (club_id) {
        //console.log(club_id)
        $location.path('/club/detail/' + club_id);
    };
    $scope.club_events = function (club_id) {
        //console.log(club_id)
        $location.path('/event/list_of_club/' + club_id);
    };
    $scope.club_modify = function (club_id) {
        $location.path('/club/modify/' + club_id);
    };
    $scope.club_delete = function (club_id) {
        $location.path('/club/delete/' + club_id);
    };

    var m_params = {};
    m_params.token = $rootScope.admin_info.token;
    m_params.admin_id = $rootScope.admin_info.id;
    $http({
        url: "/admin/club/detail/" + $routeParams.id,
        method: "GET",
        params: m_params,
    }).success(function (d) {
        if (d.retcode == 0) {
            $scope.user_and_club = d.result;
            console.log(d.result);
        } else {
            console.log(d.errmsg);
        }

    }).error(function (d) {
        console.log("get club detail error");
        $location.path("/login");
    });
});

clubCtrl.controller('ClubModifyCtrl', function ($http, $scope, $rootScope, $routeParams, $location) {
    $scope.user_and_club = {"user_id": "", "club_id": "", "mobile": '', "nickname": '', "club_name": '', "tags": ''};
    var check_params = function (params) {
        return true;
    };
    $scope.submit = function () {

        var m_params = $scope.user_and_club;
        m_params.token = $rootScope.admin_info.token;
        m_params.admin_id = $rootScope.admin_info.id;
        if (!check_params(m_params)) return;
        $http({
            url: "/admin/club/modify",
            method: "PUT",
            params: m_params
        }).success(function (d) {
            if (d.retcode == 0) {
                $location.path("/club/detail/" + $scope.user_and_club.club_id);
                console.log(d.result);
            } else {
                console.log(d.errmsg);
            }


        }).error(function (d) {
            console.log("modify club error");
            $location.path("/login");
        })
    };

    var m_params = {};
    m_params.token = $rootScope.admin_info.token;
    m_params.admin_id = $rootScope.admin_info.id;

    $http({
        url: "/admin/club/detail/" + $routeParams.id,
        method: "GET",
        params: m_params
    }).success(function (d) {
        if (d.retcode == 0) {
            $scope.user_and_club = d.result;
            console.log(d.result);
        } else {
            console.log(d.errmsg);
        }


    }).error(function (d) {
        console.log("get club detail error");
        $location.path("/login");
    });


});




