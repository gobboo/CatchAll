import sys, os
from catchall import faceserver


if __name__ == "__main__":
  try:
    faceserver.FaceServer('0.0.0.0', 20000).listen()
  except KeyboardInterrupt:
    server.stop()
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)
