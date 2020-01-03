import logging
from flask import (Flask, render_template, flash, jsonify,
                   request, g, session, redirect, Response)

from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Server
from flask_login import LoginManager, login_required

from PyAccessPoint import pyaccesspoint

from threading import Thread, Lock
from datetime import timedelta, datetime, date

from apscheduler.schedulers.background import BackgroundScheduler

import json

__version__ = '0.1.0'


outputFrame = None
lock = Lock()

#Setup flask, cus uh we  need it :)
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
from .utils import deviceInfo, getWifiList, wireless

manager = Manager(app)

loginManager = LoginManager()
loginManager.init_app(app)

#Setup Databases
db = SQLAlchemy(app)
from .models import User, Config, Stat

#Authentication config and stuff
wifiNetworks = [(ssid, ssid) for ssid in getWifiList()]
access_point = pyaccesspoint.AccessPoint(wlan=wireless.interfaces()[0], ssid=app.config['WIFI_SSID'], password=app.config['WIFI_PASSWORD'])

#Setup logging
logging.basicConfig(filename=app.config['LOG_PATH'],level=logging.INFO)

#Start multiprocess video
from .feed import VideoCamera
video = VideoCamera()
video.start()

def register_blueprints():
  from .install import install_blueprint
  app.register_blueprint(install_blueprint)

  from .api import api_blueprint
  app.register_blueprint(api_blueprint)

  from .auth import auth_blueprint
  app.register_blueprint(auth_blueprint)

def videoGen():
  while True:
    frame = video.frame
    print(frame)
    yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#Routes
@app.route('/')
@login_required
def home():
  dInfo = deviceInfo()

  today = datetime.today()
  offset = (today.weekday() + 1) % 7
  last_sunday = today - timedelta(days=offset)

 # app.logger.info(datetime.timestamp(last_sunday))
  statInfo = Stat.query.filter(Stat.date > datetime.timestamp(last_sunday)).order_by(Stat.date.desc()).limit(7).all()
  return render_template('index.html', deviceData=dInfo, statData=statInfo)

@app.route('/feed')
@login_required
def feed():
  return render_template("feed.html")


@app.route('/video_feed')
@login_required
def video_feed():
     return Response(videoGen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.before_request
def before_request():
  app.permanent_session_lifetime = timedelta(minutes=30)

#Default config
_config_defaults = {
    'LOG_PATH': None,
    'DEBUG': False,
    'TESTING': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///catchall.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': 'ABCDEFGHIJKLMNOP123',
    'WIFI_SSID': 'CatchAll Doorbell',
    'WIFI_PASSWORD': 'cAtchAll'
}

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

#Get config 
def config_setting(key):
    if key in app.config:
        return app.config[key]
    else:
        if key in _config_defaults:
            return _config_defaults[key]
        else:
            app.logger.error(
                'Tried to lookup missing config setting: %s' % key)
            return None

class CustomStart(Server):

  if not db.session.query(Config.query.filter_by(name='default').exists()).scalar() or not Config.query.filter_by(panelInstalled=False):
    try:
      access_point.start()
      app.logger.info(" * Wireless access point started.")
    except Exception as e:
      app.logger.error(" * Failed to start wireless access point! Cannot continue. {}".format(e))



  def __call__(self, app, *args, **kwargs):
    return Server.__call__(self, app, *args, **kwargs)

manager.add_command('runserver', CustomStart())
