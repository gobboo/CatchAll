from flask import render_template, redirect, jsonify, request, Blueprint, flash
from flask_wtf import FlaskForm

from catchall import app, db, wifiNetworks, access_point
from .models import User, Config

from wtforms import (
    Form, widgets, validators,
    StringField, BooleanField,
    SelectField, ValidationError, SelectMultipleField)

from .utils import getWifiList, connect2Network
import time
import subprocess
install_blueprint = Blueprint('install', __name__)

class InstallForm(FlaskForm):
  #Step 1
  deviceName = StringField('Device Name', validators=[validators.DataRequired(), validators.Regexp(r'^[\w.@+-]+$'), validators.Length(min=4, max=12)])
  adminUsername = StringField('Admin Username', validators=[validators.DataRequired(), validators.Regexp(r'^[\w.@+-]+$'), validators.Length(min=4)])
  adminPassword = StringField('Admin Password', validators=[validators.DataRequired(), validators.Length(min=8)])
  
  #Step 2
  resolutionSelect = SelectField('Camera Resolution ( The higher the slower feedback )', choices=[('1280x720', '720p HD'), ('640x480', '480p ( Recommended )'), ('480x240', '240p')])
  requiresAuth = BooleanField('Feed requires Authentication?')

  networkSelection = SelectField('Network Selection')
  networkPassword = StringField('Network Password', validators=[validators.DataRequired()])


#Routing
@install_blueprint.route('/install', methods=['GET', 'POST'])
def install():
  if db.session.query(Config.query.filter_by(name='default').exists()).scalar() or Config.query.filter_by(panelInstalled=True).first():
      return redirect('/')

  form = InstallForm()
  form.networkSelection.choices = wifiNetworks

  if request.method == 'POST':
    #TODO
    #Setup new user, add new options to a config file, attempt to get connection from camera
    if form.validate_on_submit():
      if access_point.stop():
        time.sleep(4)
      #First lets try connect to the new wifi
      #If successfull update database, install stuff idk
      #Redirect user to new IP
        app.logger.info(' * Attempting to connect to network')
        if connect2Network(form.networkSelection.data, form.networkPassword.data):
          defaultCfg = Config(name="default", panelInstalled=True, active=True)
          db.session.add(defaultCfg)

          #Create a new user
          user = User()
          user.hash_password(form.adminPassword.data)
          user.createUser(username=form.adminUsername.data)

          #Update hostname
          #subprocess.call("hostname -b " + form.deviceName, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          db.session.commit()
        else:
          app.logger.info(' * Failed to connect to network')
          flash("There was an issue connecting to the network, please try again in the configuration tab.")
        
      return redirect('/')
    else:
      flash('Some inputs have invalid data, keep input alphanumeric.')
      return render_template(
        'install.html', form=form)
  else:
    return render_template(
          'install.html', form=form)