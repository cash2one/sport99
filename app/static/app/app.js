/* App Module */
templates_root = '/static/app/templates/';

var app = angular.module('app', [
  'ngRoute',
  'ngCookies',
  'ngDialog',
  'userController',
  //'baseController',
  'clubController',
  'eventController',
  //'toolController'
]);

app.run(['$location', '$rootScope', '$http', '$cookies',
    function($location, $rootScope, $http, $cookies) {

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

    /************************************ END **********************************/

    // 浏览器鉴别
    var ua = navigator.userAgent.toLowerCase();
    $rootScope.wx_client = ua.indexOf('micromessenger') != -1;

    // var isAndroid = ua.indexOf('android') != -1;
    // var isIos = (ua.indexOf('iphone') != -1) || (ua.indexOf('ipad') != -1);

     $http({
            url: $rootScope.url_prefix + "qiniu/init/",
            method: "GET",
            // params: $scope.club
        }).then(function(response){
        // 七牛配置根据不同环境配置
        $rootScope.qiniu_bucket_domain = response.data.qiniu_bucket_domain;
        $rootScope.load_qiniu = function(k, callback_f){
            var uploader = Qiniu.uploader({
                runtimes: 'html5,flash,html4',    //上传模式,依次退化
                browse_button: 'pickfiles',       //上传选择的点选按钮，**必需**
                uptoken_url:  $rootScope.url_prefix + 'qiniu/up_token?key=' + k,
                domain: 'http://qiniu-plupload.qiniudn.com/', //bucket 域名，下载资源时用到，**必需**
                container: 'upload_container',           //上传区域DOM ID，默认是browser_button的父元素，
                max_file_size: '10mb',           //最大文件体积限制
                flash_swf_url: 'js/plupload/Moxie.swf',  //引入flash,相对路径
                max_retries: 3,                   //上传失败最大重试次数
                dragdrop: true,                   //开启可拖曳上传
                drop_element: 'upload_container',        //拖曳上传区域元素的ID，拖曳文件或文件夹后可触发上传
                chunk_size: '4mb',                //分块上传时，每片的体积
                auto_start: true,                 //选择文件后自动上传，若关闭需要自己绑定事件触发上传
                init: {
                    'FilesAdded': function(up, files) {
                        plupload.each(files, function(file) {
                            // 文件添加进队列后,处理相关的事情
                        });
                    },
                    'BeforeUpload': function(up, file) {
                           // 每个文件上传前,处理相关的事情
                    },
                    'UploadProgress': function(up, file) {
                           // 每个文件上传时,处理相关的事情
                    },
                    'FileUploaded': function(up, file, info) {
                           var domain = $rootScope.qiniu_bucket_domain; //up.getOption('domain');
                           var res = $.parseJSON(info);
                           callback_f(domain, res);
                    },
                    'Error': function(up, err, errTip) {
                           //上传出错时,处理相关的事情
                    },
                    'UploadComplete': function() {
                           //队列文件处理完毕后,处理相关的事情
                    },
                    'Key': function(up, file) {
                        // 若想在前端对每个文件的key进行个性化处理，可以配置该函数
                        // 该配置必须要在 unique_names: false , save_key: false 时才生效
                        var key = k;
                        return key
                    }
                }
            });
        };
    },function(){
        $rootScope.alert("加载出现问题, 请刷新从新加载");
    });


    // 微信初始化
    if($rootScope.wx_client){
        $http({
            url: $rootScope.url_prefix + "api/wx/get_tx_signature",
            method: "GET",
            // params: $scope.club
        }).success(function(d){
            wx.config({
                debug: true,
                appId: d.app_id,
                timestamp: d.timestamp,
                nonceStr: d.noncestr,
                signature: d.signature,
                jsApiList: [
                  'checkJsApi',
                  //'getLocation'
                ]
            });

//            wx.ready(function(){
//                wx.hideMenuItems({
//                    menuList: [
//                        'menuItem:share:timeline',
//                        'menuItem:share:appMessage'
//                    ]
//                });
//            });
        }).error(function(data){
            // TODO 请求用户信息异常
        });
    }
    // 页面跳转后
    $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {

    });

    /*********************************** 全局方法区 e***************************************/

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


    var check_user = function(){
        $rootScope.user_id = $cookies.get("user_id");
        $rootScope.token = $cookies.get("token");
        console.log($rootScope.user_id&&$rootScope.token);
        return $rootScope.user_id&&$rootScope.token;
    }

    if(!check_user()) {
        if($rootScope.wx_client){
            // 微信登录跳转回来的
            if($cookies.get("login_in_path")){
                var this_url = window.location.toString();
                if(this_url.indexOf("code")>0){
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
            }else{
                $cookies.put("login_in_path", $location.path());
                alert($cookies.get("login_in_path"));
                if($cookies.get("login_in_path")){
                    window.location = "api/wx/login";
                }
            }

        }else{
            $rootScope.user_id = 10;
            $rootScope.token = 10;
            $cookies.put("user_id", $rootScope.user_id);
            $cookies.put("token", $rootScope.token);
        }

    }
}]);
