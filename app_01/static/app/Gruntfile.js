module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    concat: {
      options: {
      },
      js: {
        src: [  // '<%= pkg.name %>.js',
          'node_modules/jquery/dist/jquery.min.js',
          'node_modules/plupload/js/plupload.full.min.js',
          'node_modules/qiniu/src/qiniu.min.js',
          'node_modules/angular/angular.min.js',
          'node_modules/angular-route/angular-route.min.js',
          'node_modules/angular-cookies/angular-cookies.min.js',
          'node_modules/ng-dialog/js/ngDialog.min.js',
          'node_modules/moment/min/moment.min.js',
          'controllers/*.js',
          'app.js',
          'route.js'
          //'dist/m.js'
        ],
        dest: 'dist/<%= pkg.name %>.min.<%= pkg.version %>.js' //合并文件
      },
      css: {
        src: [
          'node_modules/bootstrap/dist/css/bootstrap.min.css',
          'node_modules/ng-dialog/css/ngDialog.min.css',
          'css/me.min.css'
        ],
        dest: 'dist/<%= pkg.name %>.min.<%= pkg.version %>.css'
      }
    },
    less: {
        css: {
            src: 'less/style.less', //将之前的all.css
            dest: 'css/me.css' //压缩
        }
    },
    cssmin: { //css文件压缩
      css: {
        src: 'css/me.css', //将之前的all.css
        dest: 'css/me.min.css' //压缩
      }
    },
    uglify: {
      options: {
        // banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: ['controllers/club.js', 'app.js', 'route.js'],
        dest: 'dist/m.js'
      }
    },
    clean: {
      start: {
        src: ['dist/*'],
        filter: 'isFile'
      },
      end: {
        src: ['css/*'],
        filter: 'isFile'
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-concat');

  grunt.registerTask('default', ['clean:start', 'less', 'cssmin', 'concat', 'clean:end']);

};