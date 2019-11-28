from flask import redirect, Blueprint, request, render_template, flash
from flask_login import UserMixin, login_required, login_user, logout_user, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, validators


from catchall import app, db, loginManager
from .models import User, Config

auth_blueprint = Blueprint('auth', __name__)

loginManager.login_view = 'login'
loginManager.refresh_view = 'logout'
loginManager.needs_refresh_message = ("Session timedout, please re-login")
loginManager.needs_refresh_message_category = "info"

#Authentication
class Login(FlaskForm):
  username = StringField('Username', validators=[validators.DataRequired()])
  password = StringField('Password', validators=[validators.DataRequired()])

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
  if not db.session.query(Config.query.filter_by(name='default').exists()).scalar() or Config.query.filter_by(name='default').first().panelInstalled == False:
      return redirect('/install')

  form = Login()

  if request.method == "POST":
    username = form.username.data
    password = form.password.data

    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
      flash('Your login details were incorrect.')
      return render_template('login.html', form=form)
    
    login_user(user)
    return redirect('/')

  return render_template('login.html', form=form)

@auth_blueprint.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect('/login')

@loginManager.user_loader
def load_user(id):
  return User.query.get(int(id))

@loginManager.unauthorized_handler
def unauthorized():
  return redirect('/login')