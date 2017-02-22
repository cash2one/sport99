/**
 * Created by zhaojm on 4/22/16.
 */

//路由设定
adminApp.config(function ($routeProvider) {
    $routeProvider.when('/club/list', {
            templateUrl: templates_root + 'club/list.html',
            controller: 'ClubListCtrl'
        })
        .when('/club/detail/:id', {
            templateUrl: templates_root + 'club/detail.html',
            controller: 'ClubDetailCtrl'
        })
        .when('/club/modify/:id', {
            templateUrl: templates_root + 'club/modify.html',
            controller: 'ClubModifyCtrl'
        })
        .when('/club/create', {
            templateUrl: templates_root + 'club/create.html',
            controller: 'ClubCreateCtrl'
        })
        .when('/event/list', {
            templateUrl: templates_root + 'event/list.html',
            controller: 'EventListCtrl'
        })
        .when('/event/list_of_club/:club_id', {
            templateUrl: templates_root + 'event/list.html',
            controller: 'EventsOfClubCtrl'
        })
        .when('/event/detail/:id', {
            templateUrl: templates_root + 'event/detail.html',
            controller: 'EventDetailCtrl'
        })
        .when('/event/create', {
            templateUrl: templates_root + 'event/create.html',
            controller: 'EventCreateCtrl'
        })
        .when('/event/modify/:id', {
            templateUrl: templates_root + 'event/modify.html',
            controller: 'EventModifyCtrl'
        })
        .when('/login', {
            templateUrl: templates_root + 'admin/login.html',
            controller: 'LoginCtrl'
        })
        .otherwise({redirectTo: '/event/list'})
})