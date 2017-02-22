__author__ = 'Van'

import os
import sys
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
from app.models import Venue, Activity, CycleActivity, Club, \
    ClubMember, ActivityMember, ActivityCluster, User, Robot, Cluster, ClusterMember, QQUser,\
    TokenTemp, ActivityCategory, ActivityLevel, WeixinMenu, WeixinUser, OauthUrl, Area, QQBindCode

print "************* CURRENT CONFIG MODE: ", os.getenv('YUNDONG99_APP_CONFIG_MODE')
mode = os.getenv('YUNDONG99_APP_CONFIG_MODE') or 'default'
if mode:
    mode = mode.lower()
    # print 'current config mode %s' % mode
app = create_app(mode)
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db,
                Venue=Venue,
                Activity=Activity,
                CycleActivity=CycleActivity,
                Club=Club,
                ClubMember=ClubMember,
                ActivityMember=ActivityMember,
                ActivityCluster=ActivityCluster,
                User=User,
                Robot=Robot,
                Cluster=Cluster,
                ClusterMember=ClusterMember,
                QQUser=QQUser,
                TokenTemp=TokenTemp,
                ActivityCategory=ActivityCategory,
                ActivityLevel=ActivityLevel,
                WeixinMenu=WeixinMenu,
                WexinUser=WeixinUser,
                OauthUrl=OauthUrl,
                Area=Area,
                QQBindCode=QQBindCode
                )
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """aRun the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=4999)

    manager.run()
