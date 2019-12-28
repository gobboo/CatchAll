from flask import Blueprint, request, jsonify, g

from .models import User, Config
from catchall import app, db

from .utils import getWifiList, connect2Network

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/wifi', methods=['GET'])
def wifiConnect():  
  available_networks = getWifiList()
  if(len(available_networks) < 1): # Check if its empty or not
    return jsonify(error="There are no available networks :(")

  return jsonify(available_networks)