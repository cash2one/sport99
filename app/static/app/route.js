app.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/users/show', {
        templateUrl: templates_root+'user/show.html',
        controller: 'UserShowController'
      }).
      when('/info_set', {
        templateUrl: templates_root+'user/show.html',
        controller: 'UserShowController'
      }).
      when('/users/update/:id', {
        templateUrl: templates_root+'users/update.html',
        controller: 'UserUpdateController'
      }).
      when('/clubs/create_step1', {
        templateUrl: templates_root+'club/create_step1.html',
        controller: 'ClubCreateStep1Controller'
      }).
      /************************** 俱乐部 ****************************/
      when('/clubs/head_bg_picker', {
        templateUrl: templates_root+'club/head_bg_picker.html',
        controller: 'ClubHeadBGPickerController'
      }).
      when('/clubs/create_step2', {
        templateUrl: templates_root+'club/create_step2.html',
        controller: 'ClubCreateStep2Controller'
      }).
      when('/clubs/create_step3', {
        templateUrl: templates_root+'club/create_step3.html',
        controller: 'ClubCreateStep3Controller'
      }).
      when('/clubs/members/:id', {
        templateUrl: templates_root+'club/members.html',
        controller: 'ClubMembersController'
      }).
      when('/clubs', {
        templateUrl: templates_root+'club/mine.html',
        controller: 'ClubMineController'
      }).
      when('/clubs/show/:id', {
        templateUrl: templates_root+'club/show.html',
        controller: 'ClubShowController'
      }).
      when('/events/create_step1', {
        templateUrl: templates_root+'event/create_step1.html',
        controller: 'EventCreateStep1Controller'
      }).
      when('/category_picker', {
        templateUrl: templates_root+'event/category_picker.html',
        controller: 'CategoryPickerController'
      }).
      when('/city_picker', {
        templateUrl: templates_root+'event/city_picker.html',
        controller: 'CityPickerController'
      }).
      when('/filter_picker', {
        templateUrl: templates_root+'event/filter_picker.html',
        controller: 'FilterPickerController'
      }).
      when('/filter_category', {
        templateUrl: templates_root+'event/filter_category.html',
        controller: 'FilterCategoryController'
      }).
      when('/location', {
        templateUrl: templates_root+'location.html',
        controller: 'LocationController'
      }).
      when('/events/show/:id', {
        templateUrl: templates_root+'event/event_show.html',
        controller: 'EventShowController'
      }).
      when('/events', {
        templateUrl: templates_root+'event/event_list.html',
        controller: 'EventListController'
      }).
      when('/events/mine_published', {
        templateUrl: templates_root+'event/mine_publish.html',
        controller: 'EventPublishedController'
      }).
      when('/mine_events', {  // 我的活动
        templateUrl: templates_root+'event/mine_publish.html',
        controller: 'EventJoinedController'
      }).
      when('/events/mine_joined', {
        templateUrl: templates_root+'event/mine_publish.html',
        controller: 'EventJoinedController'
      }).
      when('/events/members/:id', {
        templateUrl: templates_root+'event/members.html',
        controller: 'EventMembersController'
      }).
      when('/navigate/:id', {
        templateUrl: templates_root+'event/navigate.html',
        controller: 'NavigateController'
      }).
      when('/qq_clusters', {
        templateUrl: templates_root+'club/qq_clusters.html',
        controller: 'QQClustersController'
      }).
      otherwise({
        templateUrl: templates_root+'loading.html',
        controller: 'LoadingController'
    });
  }]);