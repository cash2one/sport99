# coding:utf-8
__author__ = 'zhaojm'

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 每次请求结束后都会自动提交数据库中的变动
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(Config):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,'data-test.sqlite')
    # mysql://username:password@hostname/database
    DOMAIN = "test.yundong99.net"
    WECHAT_TOKEN = "yundongjiujiu"
    WECHAT_APP_ID = "wx605507267852f897"
    WECHAT_APP_SECRET = "34b08f598ec28a60a4ce15b5ba4cae6c"
    WECHAT_NONCE = "18612596605"

    QINIU_ACCESS_KEY = "OA6lt_AVO1EYXROD0PK4QV7EgYAA-1_bw2CX_ozX"
    QINIU_SECRET_KEY = "VCAdMwflUf5f_34AK4ytGhfb6-HM91sZ2m0XU29a"
    QINIU_BUCKET_NAME = "test"
    QINIU_BUCKET_DOMAIN = "7xscpa.com1.z0.glb.clouddn.com"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,'data-test.sqlite')
    # mysql://username:password@hostname/database


class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    # mysql://username:password@hostname/database
    DOMAIN = "www.yundong99.net"
    WECHAT_TOKEN = "yundongjiujiu"
    WECHAT_APP_ID = "wx44822e4f3edf361c"
    WECHAT_APP_SECRET = "b6e5e2f4f17670bba2dadc634cf9d3f3"
    WECHAT_NONCE = "18612596605"

    QINIU_ACCESS_KEY = "84u2D_4dZfQCZkfg1IqQMuVh-VKnBRvF419P2_IU"
    QINIU_SECRET_KEY = "J7OBFZAuN1_vS7Ta5hRCrr_i3e_KSctkXXfrO2sb"
    QINIU_BUCKET_NAME = "yundong99"
    QINIU_BUCKET_DOMAIN = "7xsnwq.com1.z0.glb.clouddn.com"

    JOBS = [
        {
            'id': 'create_event',
            'func': 'app_01.helpers.views_helper:create_event',
            'trigger': 'cron',
            'second': 1,
            'day_of_week':'0-7',
            'hour':'1',
            'minute':1
        },
#        {
#            'id': 'auto_sign',
#            'func': 'app_01.helpers.views_helper:auto_sign',
#            'trigger': 'cron',
#            'second': 1,
#            'day_of_week':'0-7',
#            'hour':'2'
#        },
        {
           'id':'test',
           'func': 'app_01.helpers.views_helper:test_scheduler',
           'trigger': 'cron',
           'second': 1,
           'day_of_week':'0-7',
           'hour':'1-23',
           'minute': '1-59'
        }

    ]
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}
