/* App Module */
templates_root = '/static/app/templates/';

var app = angular.module('app', [
    'ngRoute',
    'ngCookies',
    'ngDialog',
    'userController',
    //'baseController',
    'clubController',
    'eventController'
  ],function($httpProvider) {
      // Use x-www-form-urlencoded Content-Type
      $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';
      $httpProvider.defaults.headers.put['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';

        var param = function(obj) {
        var query = '', name, value, fullSubName, subName, subValue, innerObj, i;

        for(name in obj) {
          value = obj[name];

          if(value instanceof Array) {
            for(i=0; i<value.length; ++i) {
              subValue = value[i];
              fullSubName = name + '[' + i + ']';
              innerObj = {};
              innerObj[fullSubName] = subValue;
              query += param(innerObj) + '&';
            }
          }
          else if(value instanceof Object) {
            for(subName in value) {
              subValue = value[subName];
              fullSubName = name + '[' + subName + ']';
              innerObj = {};
              innerObj[fullSubName] = subValue;
              query += param(innerObj) + '&';
            }
          }
          else if(value !== undefined && value !== null)
            query += encodeURIComponent(name) + '=' + encodeURIComponent(value) + '&';
        }

        return query.length ? query.substr(0, query.length - 1) : query;
      };

      // Override $http service's default transformRequest
      $httpProvider.defaults.transformRequest = [function(data) {
        return angular.isObject(data) && String(data) !== '[object File]' ? param(data) : data;
      }];
    }
);

app.run(['$location', '$rootScope', '$http',
    function($location, $rootScope, $http) {

    /************************************ 全局常亮定义区 **********************************/
    $rootScope.url_prefix = $location.protocol() + "://" + $location.host() + ":" + $location.port() + "/";
    $rootScope.templates_path =  $rootScope.url_prefix + "static/app/templates/";
    // 各个模版路径
    $rootScope.title_url = $rootScope.templates_path + "widgets/title.html";
    $rootScope.title_dialog_url = $rootScope.templates_path + "widgets/title_dialog.html";
    $rootScope.nav_url = $rootScope.templates_path + "widgets/nav.html";
    $rootScope.title_search_url = $rootScope.templates_path + "widgets/title_search.html";
    $rootScope.alert_url = $rootScope.templates_path + "widgets/alert.html";
    $rootScope.category_picker_path = $rootScope.templates_path + "tools/category_picker.html";

    /*********************************************************************
        END
    **********************************************************************/

    // 浏览器鉴别
    var ua = navigator.userAgent.toLowerCase();
    $rootScope.wx_client = ua.indexOf('micromessenger') != -1;

    // var isAndroid = ua.indexOf('android') != -1;
    $rootScope.isIos = (ua.indexOf('iphone') != -1) || (ua.indexOf('ipad') != -1);

    // 微信初始化
    if($rootScope.wx_client){
        $http({
            url: $rootScope.url_prefix + "api/wx/get_tx_signature",
            method: "GET",
            // params: $scope.club
        }).success(function(d){
            $rootScope.qiniu_bucket_domain = d.qiniu_bucket_domain;
            wx.config({
                debug: false,
                appId: d.app_id,
                timestamp: d.timestamp,
                nonceStr: d.noncestr,
                signature: d.signature,
                jsApiList: ["checkJsApi","onMenuShareTimeline","onMenuShareAppMessage","onMenuShareQQ","onMenuShareWeibo","hideMenuItems","showMenuItems","hideAllNonBaseMenuItem","showAllNonBaseMenuItem","translateVoice"],

            });

            wx.ready(function(){

            });
        }).error(function(data){
            // TODO 请求用户信息异常
        });
    }
    // 页面跳转后
    $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {


            var present_route = $location.$$path; //获取当前路由
            if(present_route == "/events"){//列表
                //$rootScope.alert("/events");
            }else if(present_route.indexOf("/events/show/")>-1){//详情
                //$rootScope.alert("/event/show/");
            }else{//其他 无需分享页面
                function onBridgeReady(){
                    WeixinJSBridge.call('hideOptionMenu');
                }
                if (typeof WeixinJSBridge == "undefined"){
                    if( document.addEventListener ){
                        document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
                    }else if (document.attachEvent){
                        document.attachEvent('WeixinJSBridgeReady', onBridgeReady);
                        document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
                    }
                }else{
                    onBridgeReady();
                }
            }

    });

    /*********************************** 全局方法区 e***************************************/
    // 对象存储
    $rootScope.putObject =function(key, value){
        localStorage.setItem(key, angular.toJson(value));
    };
    $rootScope.getObject =function(key){
        return angular.fromJson(localStorage.getItem(key))
    };
    // 处理返回
    $rootScope.path_history_stack = new Array();
    $rootScope.path_history_stack.push($location.path());
    $rootScope.back = function(){
        // 返回 取出上一个path 存入当前path
        $rootScope.is_back = true;
        if($rootScope.back_path){
            console.log("BACK TO:"+$rootScope.back_path);
            $location.path($rootScope.back_path);
        }else{
            window.history.back();
        }
    }
    $rootScope.close_alert = function(){
        $rootScope.alert_show = null;
    }
    $rootScope.alert = function(data){
        $rootScope.alert_show = true;
        if(data){
            $rootScope.alert_str = data;
            setTimeout(function(){
                $rootScope.alert_show = null;
                $rootScope.$apply();
                }, 3000);
        }else{
            $rootScope.alert_str = "未知错误";
        }
    }
    if(!window.localStorage){
        alert('This browser does NOT support localStorage');
    }
    $rootScope.qiniu_bucket_domain = "mr-van-apps.qiniudn.com";
    var check_user = function(){
        $rootScope.user_id = localStorage.user_id;
        $rootScope.token = localStorage.token;
        return $rootScope.user_id;
    }
    if($location.path() != "/success"){
         localStorage.login_in_path = window.location.toString();

         if(!check_user() ){
            if($rootScope.wx_client){
                window.location = "/api/wx/login";
            }else{
                $rootScope.user_id = 9;
                $rootScope.token = 9;
            }
         }

        // 验证登录是否失效
        if($rootScope.wx_client){
            $http({
                url: $rootScope.url_prefix + "api/wx/is_token_expired",
                method: "POST",
                params: {
                    user_id: $rootScope.user_id,
                    token: $rootScope.token
                }
            }).success(function(data){
                if(data.code == 1 ){
                    var keys = document.cookie.match(/[^ =;]+(?=\=)/g);
                    if (keys) {
                    for (var i = keys.length; i--;)
                        document.cookie=keys[i]+'=0;expires=' + new Date( 0).toUTCString()
                    }
                    localStorage.login_in_path = window.location.toString();
                    window.location = "/api/wx/login";
                }
            }).error(function(d){
                // TODO login error
                $rootScope.alert('验证过期出现问题');
            });
        }
    }
}]);
