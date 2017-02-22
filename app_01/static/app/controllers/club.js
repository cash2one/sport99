var clubController = angular.module('clubController', []);

// 报名活动， 可带入
clubController.controller('ClubCreateStep1Controller',
	['$scope', '$rootScope', '$location', '$http', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $location, $http, $routeParams, ngDialog){

    var ask = function(){
        var dialog = ngDialog.open({ template: 'tell_you',
            className: 'ngdialog-theme-plain ngdialog_page',
            appendTo: '#club_create',
            scope: $scope
        });
        dialog.closePromise.then(function (data){
          //if(data.value == 'yes'){
                $location.path("/clubs");
            //}
        });
    }
    if(localStorage.getItem("club_exist")){
        //$location.path("/clubs");
        ask();
    }else{
        $http({
            url: "/has_club",
            method: "GET",
            params: {user_id: $rootScope.user_id, token:$rootScope.token}
        }).success(function(d){
            if(d.code==1){
                //$location.path("/clubs");
                ask();
            }
        }).error(function(d){
        })
    }

    $scope.save = function(){
        $rootScope.putObject("club_creating", $scope.club);
    }

    $scope.club = {
        tags: "请选择",
        bg_img_url: '/static/app/img/bgimgs/club/P2.png'
    }
    if($rootScope.getObject("club_creating")){
        $scope.club = $rootScope.getObject("club_creating");
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
            $scope.save();
        });
    }
    if($scope.club.bg_img_url){
        document.getElementById("upload_container").style.backgroundImage = "url("+$scope.club.bg_img_url +")";
    }else{
        document.getElementById("upload_container").style.backgroundImage = "url('/static/app/img/bgimgs/club/P2.png')";
    }
    // 设置俱乐部头像
    if($scope.club.logo_url){
        document.getElementById("logo_img").style.backgroundImage = "url("+$scope.club.logo_url +")";
    }
    //alert($rootScope.qiniu_bucket_domain);

    var uploader = Qiniu.uploader({
        runtimes: 'html5,flash,html4',    //上传模式,依次退化
        browse_button: 'logo_img',       //上传选择的点选按钮，**必需**
        uptoken_url: '/qiniu/up_token',
        get_new_uptoken: true,
        //save_key: true,
        domain: $rootScope.qiniu_bucket_domain, //bucket 域名，下载资源时用到，**必需**
        container: 'upload_container',           //上传区域DOM ID，默认是browser_button的父元素，
        max_file_size: '10mb',           //最大文件体积限制
        flash_swf_url: 'js/plupload/Moxie.swf',  //引入flash,相对路径
        max_retries: 3,                   //上传失败最大重试次数
        dragdrop: false,                   //开启可拖曳上传
        drop_element: '',        //拖曳上传区域元素的ID，拖曳文件或文件夹后可触发上传
        chunk_size: '4mb',                //分块上传时，每片的体积
        auto_start: true,                 //选择文件后自动上传，若关闭需要自己绑定事件触发上传
        init: {
            'FilesAdded': function(up, files) {
//                    plupload.each(files, function(file) {
//                        // 文件添加进队列后,处理相关的事情
//                    });
            },
            'BeforeUpload': function(up, file) {
                $rootScope.uploading = true;
                $scope.upload_percent = file.percent;
                $rootScope.$apply();
            },
            'UploadProgress': function(up, file) {
                   // 每个文件上传时,处理相关的事情
                   $scope.upload_percent = file.percent;
                   $scope.$apply();
            },
            'FileUploaded': function(up, file, info) {
                var res = $.parseJSON(info);
                var logo_url = "http://"+$rootScope.qiniu_bucket_domain+"/"+res.key+"-icon";
                ///alert(logo_url);
                document.getElementById("logo_img").style.backgroundImage = "url("+ logo_url +")";
                $scope.club.logo_url = logo_url;
                $scope.save();
            },
            'Error': function(up, err, errTip) {
                   console.log(err);
                   $rootScope.alert("头像跟新失败！");
            },
            'UploadComplete': function() {
                   //队列文件处理完毕后,处理相关的事情
            },
            'Key': function(up, file){
                var today=new Date();
                var time = today.getHours()+""+today.getMinutes()+""+today.getSeconds();
                var k = 'clubs/logo_url/'+time;
                return k;
            }
        }
    });

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
            $scope.save();
        });
    }

    $scope.submit = function(){
        if(!$scope.club.logo_url){
            $scope.club.logo_url = '/static/app/img/headimgs/club1.png';
        }
        m_params = {
            "user_id": $rootScope.user_id,
            "token": $rootScope.token,
            "name": $scope.club.name,
            "tags": $scope.club.tags,
            "logo_url": $scope.club.logo_url,
            "bg_img_url": $scope.club.bg_img_url,
            "bind_qq": $scope.club.bind_qq
        }
        $http({
            url: "/clubs",
            method: "POST",
            params: m_params
        }).success(function(d){
            if(d.code==1){
                localStorage.setItem("club_exist", "1");
                localStorage.removeItem("club_creating");
                $scope.bind_show();
            }
        }).error(function(d){
            console.log("创建俱乐部失败");
        })
    }
    $scope.bind_show = function(){
        if($scope.qq_bind){
            $location.path("/clubs/create_step3");
        }else{
            var dialog = ngDialog.open({ template: 'band_qq',
                className: 'ngdialog-theme-plain ngdialog_page',
                appendTo: '#club_create'
            });
            dialog.closePromise.then(function (data) {
                // 接受报名结果
                if(data.value == 'yes'){
                    $scope.save();
                    $location.path("/clubs/create_step2");
                }else{
                    $location.url(localStorage.getItem("finish_url"));
                }
            });

        }
    }

}]);


clubController.controller('ClubUpdateController',
	['$scope', '$rootScope', '$location', '$http', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $location, $http, $routeParams, ngDialog){

	$scope.save = function(){
        $rootScope.putObject("club_updating", $scope.club);
    }
    if($rootScope.getObject("club_updating") ){
        $scope.club = $rootScope.getObject("club_updating");
    }else{
        $http({
            url: "/clubs/show/"+$routeParams.id,
            method: "GET",
            params: {user_id: $rootScope.user_id, token: $rootScope.token}
        }).success(function(data){
            $scope.club = data.club;
            if($scope.club.bg_img_url){
                document.getElementById("upload_container").style.backgroundImage = "url("+$scope.club.bg_img_url +")";
            }else{
                document.getElementById("upload_container").style.backgroundImage = "url('/static/app/img/bgimgs/club/P2.png')";
            }
            if($scope.club && $scope.club.logo_url){
                document.getElementById("logo_img").style.backgroundImage = "url("+$scope.club.logo_url +")";
            }
        }).error(function(e){
            console.log(e);
        });
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
            $scope.save();
        });
    }
    if($scope.club && $scope.club.bg_img_url){
        document.getElementById("upload_container").style.backgroundImage = "url("+$scope.club.bg_img_url +")";
    }else{
        document.getElementById("upload_container").style.backgroundImage = "url('/static/app/img/bgimgs/club/P2.png')";
    }
    // 设置俱乐部头像
    if($scope.club && $scope.club.logo_url){
        document.getElementById("logo_img").style.backgroundImage = "url("+$scope.club.logo_url +")";
    }
    //alert($rootScope.qiniu_bucket_domain);

    var uploader = Qiniu.uploader({
        runtimes: 'html5,flash,html4',    //上传模式,依次退化
        browse_button: 'logo_img',       //上传选择的点选按钮，**必需**
        uptoken_url: '/qiniu/up_token',
        get_new_uptoken: true,
        //save_key: true,
        domain: $rootScope.qiniu_bucket_domain, //bucket 域名，下载资源时用到，**必需**
        container: 'upload_container',           //上传区域DOM ID，默认是browser_button的父元素，
        max_file_size: '10mb',           //最大文件体积限制
        flash_swf_url: 'js/plupload/Moxie.swf',  //引入flash,相对路径
        max_retries: 3,                   //上传失败最大重试次数
        dragdrop: false,                   //开启可拖曳上传
        drop_element: '',        //拖曳上传区域元素的ID，拖曳文件或文件夹后可触发上传
        chunk_size: '4mb',                //分块上传时，每片的体积
        auto_start: true,                 //选择文件后自动上传，若关闭需要自己绑定事件触发上传
        init: {
            'FilesAdded': function(up, files) {
//                    plupload.each(files, function(file) {
//                        // 文件添加进队列后,处理相关的事情
//                    });
            },
            'BeforeUpload': function(up, file) {
                $rootScope.uploading = true;
                $scope.upload_percent = file.percent;
                $rootScope.$apply();
            },
            'UploadProgress': function(up, file) {
                   // 每个文件上传时,处理相关的事情
                   $scope.upload_percent = file.percent;
                   $scope.$apply();
            },
            'FileUploaded': function(up, file, info) {
                var res = $.parseJSON(info);
                var logo_url = "http://"+$rootScope.qiniu_bucket_domain+"/"+res.key+"-icon";
                ///alert(logo_url);
                document.getElementById("logo_img").style.backgroundImage = "url("+ logo_url +")";
                $scope.club.logo_url = logo_url;
                $scope.save();
            },
            'Error': function(up, err, errTip) {
                   console.log(err);
                   $rootScope.alert("头像跟新失败！");
            },
            'UploadComplete': function() {
                   //队列文件处理完毕后,处理相关的事情
            },
            'Key': function(up, file){
                var today=new Date();
                var time = today.getHours()+""+today.getMinutes()+""+today.getSeconds();
                var k = 'clubs/logo_url/'+time;
                return k;
            }
        }
    });

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
            $scope.save();
        });
    }

    $scope.submit = function(){
        m_params = {
            "user_id": $rootScope.user_id,
            "token": $rootScope.token,
            "name": $scope.club.name,
            "tags": $scope.club.tags,
            "logo_url": $scope.club.logo_url,
            "bg_img_url": $scope.club.bg_img_url
        }
        $http({
            url: "/clubs/update/"+$routeParams.id,
            method: "POST",
            params: m_params
        }).success(function(d){
            console.log(d);
            if(d.code==1){
                localStorage.removeItem("club_updating");
                $location.path("/clubs/show/"+$routeParams.id);
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
	['$scope', '$rootScope', '$http', '$location', '$routeParams', 'ngDialog',
	function($scope, $rootScope, $http, $location, $routeParams, ngDialog){

    $scope.page_name = "创建俱乐部";

    $scope.submit = function(){
        $http({
            url: "users/update/" + $rootScope.user_id,
            method: "POST",
            params: {
                user_id: $rootScope.user_id,
                token: $rootScope.token,
                qq: $scope.bind_qq
            }
        }).success(function(){
            localStorage.setItem("qq", $scope.bind_qq);
            $location.path("/clubs/create_step3")
        }).error(function(){
            console.log("绑定QQ出错");
        });
    }
}]);


clubController.controller('ClubCreateStep3Controller',
	['$window', '$scope', '$rootScope', '$http', '$location', '$routeParams', 'ngDialog',
	function($window ,$scope, $rootScope, $http, $location, $routeParams, ngDialog){

    $scope.page_name = "创建俱乐部";

    $scope.qq = '2295458282';
    $scope.copy = function(){
        // $window.clipboardData.setData("Text", $scope.qq);
        if ( window.clipboardData ) {
            window.clipboardData.setData("Text", $scope.qq);
        }else{
            alert("复制版不可用，请手动复制");
        }
    }

    $scope.submit = function(){
        $http({
            url: "/users/clusters",
            method: "GET",
            params: {user_id: $rootScope.user_id, token:$rootScope.token}
        }).then(function(response){
            data = response.data;
            if(data.qq_bind && data.qq == localStorage.getItem("qq")){
                $location.path("/qq_clusters");
            }else{
                $rootScope.alert("您还没有完成QQ验证");
            }
        },function(e){
            console.log(e);
        });
    }
}]);


clubController.controller('QQClustersController',
	['$window', '$scope', '$rootScope', '$http', '$location', '$routeParams', 'ngDialog',
	function($window ,$scope, $rootScope, $http, $location, $routeParams, ngDialog){

    $http({
        url: "users/clusters",
        method: "GET",
        params: {
            user_id: $rootScope.user_id,
            token: $rootScope.token
        }
    }).success(function(data){
        $scope.clusters = data.clusters
        console.log($scope.clusters);
    }).error(function(){
        console.log("加载失败");
    });
    $scope.submit = function(){
        if($location.search() && $location.search().from == "events_create"){
            $location.url("/events/create_step1?from=bind_qq");
        }else if($routeParams.from == "club"){
            $location.url("/clubs/show/"+$routeParams.club_id+"?from=bind_qq");
        }else if($routeParams.from == "user"){
            $location.url("/users/show?from=bind_qq");
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
            if(!$scope.club.bg_img_url){
                $scope.club.bg_img_url = '/static/app/img/bgimgs/club/P4.png';
            }
            if(!$scope.club.logo_url){
                $scope.club.logo_url = '/static/app/img/headimgs/club1.png';
            }
            console.log(data);
            if(data.role < 0){
                $scope.is_follow_enable = true;
            }else if(data.role < 2 && data.role >= 0){
                $scope.is_creator = true;
            }
            $scope.clusters_count = data.clusters_count;
            $scope.qq_bind = data.qq_bind;
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
                $scope.events = data.events;
                $scope.club.events_count= $scope.events.length;
            }).error(function(e){
                console.log(e);
            });
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
        $scope.to_clusters = function(){
            if(!$scope.qq_bind){
                $scope.bind_show();
            }else{
                $location.path("/club_clusters");
            }
        }

        $scope.bind_show = function(){
            var dialog = ngDialog.open({ template: 'band_qq',
                className: 'ngdialog-theme-plain ngdialog_page',
                appendTo: '#club_show'
            });
            dialog.closePromise.then(function (data) {
                // 接受报名结果
                if(data.value){
                    $location.url("/clubs/create_step2?from=club&club_id="+$scope.club.id);
                }
            });
        }
        $scope.to_event_show = function(id){
            $location.path("/events/show/"+id);
        }


}]);


clubController.controller('ClubMineController',
	['$scope', '$rootScope', '$http', '$routeParams', '$location', 'ngDialog',
	function($scope, $rootScope, $http, $routeParams, $location, ngDialog){

    $scope.to_add_club = function(){
        localStorage.setItem("finish_url", $location.url());
        $location.path("/clubs/create_step1");
    }
    $scope.to_club_show = function(club_id){
        $location.path("/clubs/show/"+club_id);
    }
    var load = function(){
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
    }
    load();

    $scope.cancel = function(did){
        $http({
            url: "/clubs/"+did+"/cancel_follow",
            method: "POST",
            params: {
                user_id: $rootScope.user_id,
                token: $rootScope.token
            }
        }).success(function(d){
            if(d.code == 1){
                $rootScope.alert("取消关注成功");
                load();
            }
        }).error(function(d){
            console.log("创建俱乐部失败");
        })
    }
}]);