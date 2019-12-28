
from wifi import Cell

import psutil
from datetime import datetime, time
from wireless import Wireless
from catchall import app
import traceback

wireless = Wireless()

def getWifiList():
  app.logger.info(' * Getting wireless device(s)')
  interfaces = wireless.interfaces() # Get only wireless adapters
  if len(interfaces) < 1:
      return jsonify(error="You have no compatible wireless interfaces, please contact support!") 
  
  app.logger.info(' * Collecting nearby wireless networks...')
  available_networks = [cell for cell in Cell.all(interfaces[0]) if cell.ssid != ""] # Get all networks

  app.logger.info(' * Got all networks, Example: ', available_networks[0])
  return available_networks

def connect2Network(ssid, password):
  try:
    return wireless.connect(ssid, password)
  except Exception as e:
    exception = traceback.format_exception()
    app.logger.error("Error trying to connect to {}, {}".format(ssid, exception))
    return False

def deviceInfo():
  info = {}
  try:
    info["cpu"] = psutil.cpu_percent(interval=1)
    
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    info["boot"] = boot_time

    uptime = (datetime.now() - boot_time)
    info["uptime"] = str(uptime).split('.')[0]

    
  except Exception as e:
    info["error"] = "Couldn't get device information."

  return info


#Start wireless access point if there is no configuration or none that is installed

