from flask import Blueprint, request, jsonify, g

from .models import User, Config
from catchall import app, db

from .utils import getWifiList, connect2Network

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/wifi', methods=['GET'])
def wifiConnect():

  """ 
  First draft, insecure atm, not needed due to Utils.py
  
  if request.method == 'POST':
      
      ssid=request.args.get('ssid')
      passwd = request.args.get('password')

      connectionAttempt = connect2Network(ssid, password)
      app.logger.info(connectionAttempt)
      if connectionAttempt:
          app.logger.info("Device connected to new network: {}".format(ssid))
          return jsonify(success=True, message="Device successfulyl connected to {}".format(ssid))
      else:
          app.logger.error("Could not connect to network: {}".format(ssid))
          return jsonify(success=False, message="Could not connect to that wireless network, check the password and try again!")

      return jsonify(success=False, message="There was an internal error connecting to that wireless device") """
      
  available_networks = getWifiList()
  if(len(available_networks) < 1): # Check if its empty or not
    return jsonify(error="There are no available networks :(")

  return jsonify(available_networks)