from catchall import app, db
from passlib.apps import custom_app_context as pwd_context

from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(16), unique=True)
  password = db.Column(db.String(128))
  admin = db.Column(db.Integer, default=0)
  
  def hash_password(self, password):
    self.password = pwd_context.encrypt(password)

  def verify_password(self, password):
    return pwd_context.verify(password, self.password)

  def createUser(self, username, admin=0):
    user = User.query.filter_by(username=username).first()
    if user is None:
      user = User(username=username, password=self.password, admin=admin)
      db.session.add(user)
      app.logger.info('Created new user {}'.format(username))

    return user

  def __repr__(self):
    return '<User %r>' % self.id

class Config(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, default="default")
  panelInstalled = db.Column(db.Boolean, default=True)
  active = db.Column(db.Boolean, unique=False, default=False)

  def __repr__(self):
    return '<Config %r>' % self.id

class Stat(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  total_rings = db.Column(db.Integer, default=0)
  rings = db.Column(db.Integer, default=0)
  date = db.Column(db.String, default=datetime.timestamp(datetime.now()))

db.create_all()