# -*- coding:utf-8 -*-
__author__ = 'Van.zx'

from flask import Flask, jsonify, render_template

# from flask.ext.bootstrap import Bootstrap
# from flask.ext.mail import Mail
# from flask.ext.moment import Moment
# from flask.ext.sqlalchemy import SQLAlchemy
from config import config_dict
import sys

import logging
from logging.handlers import RotatingFileHandler
# bootstrap = Bootstrap()
# mail = Mail()
# moment = Moment()
# db = SQLAlchemy()
# convert python's encoding to utf8
try:
    from imp import reload
    reload(sys)
    sys.setdefaultencoding('utf8')
except (AttributeError, NameError):
    print "set default coding utf-8 error"
    pass


def _import_submodules_from_package(package):
    import pkgutil

    modules = []
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__,
                                                         prefix=package.__name__ + "."):
        modules.append(__import__(modname, fromlist="dummy"))
    return modules


def register_routes(app):
    from . import controllers
    from flask.blueprints import Blueprint

    for module in _import_submodules_from_package(controllers):
        if hasattr(module, 'main'):
            bp = getattr(module, 'main')
        elif hasattr(module, 'wx'):
            bp = getattr(module, 'wx')
        else:
            bp = getattr(module, 'api')

        if bp and isinstance(bp, Blueprint):
            app.register_blueprint(bp)

    @app.errorhandler(403)
    def page_403(error):
        app.logger.error("403")
        return jsonify({"error": "Auth error"}), 403

    # @app.before_request
    # def before_request():
    #     log_fields = []
    #     values = ""
    #     for k, v in request.args:
    #         s = '%s=%s' % (k, v)
    #         values += s
    #     # session.request_start_time = time.time()
    #     log_fields.append('method=%s' % request.method)
    #     log_fields.append('path=%s' % request.path)
    #     log_fields.append('values=(%s)' % values)
    #     app.logger.info(" ".join(log_fields))
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
    # db.init_app(app)
    register_routes(app)
    # 定时器
    scheduler.init_app(app)
    scheduler.start()
    # from apps.routes import main
    # app.register_blueprint(main)

    return app
