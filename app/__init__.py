# -*- coding:utf-8 -*-
__author__ = 'Van.zx'

from flask import Flask, jsonify, request,redirect
# from flask.ext.bootstrap import Bootstrap
# from flask.ext.mail import Mail
# from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config_dict

import sys

from flask.ext.login import LoginManager,current_user


import logging
from logging.handlers import RotatingFileHandler

# 线程池
from threadpool import ThreadPool

# bootstrap = Bootstrap()
# mail = Mail()
# moment = Moment()
db = SQLAlchemy()
db_session = db.session
# convert python's encoding to utf8
try:
    from imp import reload
    reload(sys)
    sys.setdefaultencoding('utf8')
except (AttributeError, NameError):
    pass


def _import_submodules_from_package(package):
    import pkgutil

    modules = []
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__,
                                                         prefix=package.__name__ + "."):
        modules.append(__import__(modname, fromlist="dummy"))
    return modules



# If you're using Flask-Login, this would be a good time to set that up.
login_manager = LoginManager()
# None 、 basic  、 strong
login_manager.session_protection = 'strong'
# 登录页面的端点
login_manager.login_view = 'auth_controller.login'

mypool = ThreadPool(20)

from flask_apscheduler import APScheduler
scheduler = APScheduler()


def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_mode])
    config_dict[config_mode].init_app(app)
    app.config_mode = config_mode

    # 内部日志
    rotating_handler1 = RotatingFileHandler('logs/info.log', maxBytes=1 * 1024 * 1024, backupCount=5)
    rotating_handler2 = RotatingFileHandler('logs/error.log', maxBytes=1 * 1024 * 1024, backupCount=2)

    formatter1 = logging.Formatter("-" * 100 +
                                   '\n %(asctime)s %(levelname)s - '
                                   'in %(funcName)s [%(filename)s:%(lineno)d]:\n %(message)s')

    rotating_handler1.setFormatter(formatter1)
    rotating_handler2.setFormatter(formatter1)
    app.logger.addHandler(rotating_handler1)
    app.logger.addHandler(rotating_handler2)

    app.logger.setLevel(logging.INFO)
    rotating_handler2.setLevel(logging.ERROR)
    if app.config.get("DEBUG"):
        # app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.DEBUG)

    # bootstrap.init_app(app)
    # mail.init_app(app)
    # moment.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)

    from .controllers import index
    app.register_blueprint(index.main)

    from .controllers.activity_controller import activity_controller as activity_blueprint
    app.register_blueprint(activity_blueprint)
    from .controllers.robot_controller import robot_controller as robot_blueprint
    app.register_blueprint(robot_blueprint)
    from .controllers.club_controller import club_controller as club_blueprint
    app.register_blueprint(club_blueprint)
    from .controllers.venue_controller import venue_controller as venue_blueprint
    app.register_blueprint(venue_blueprint)
    from .controllers.user_controller import user_controller as user_blueprint
    app.register_blueprint(user_blueprint)
    from .controllers.club_member_controller import club_member_controller as club_member_blueprint
    app.register_blueprint(club_member_blueprint)
    from .controllers.area_controller import area_controller as area_blueprint
    app.register_blueprint(area_blueprint)
    from .controllers.auth_controller import auth_controller as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .controllers.weixin_controller import weixin_controller as weixin_blueprint
    app.register_blueprint(weixin_blueprint)

    from .controllers.qiniu_controller import api
    app.register_blueprint(api)

    scheduler.init_app(app)

    return app

