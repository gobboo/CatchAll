import socket, pickle, logging

from threading import Thread
from socketserver import ThreadingMixIn

logging.basicConfig(filename='logs/logs.log', level=logging.DEBUG, format='%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logging
logging.getLogger().addHandler(console)
from .faceworker import FaceWorker

class FaceServer():
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((self.host, self.port))
    self.worker = FaceWorker()
    logging.info(" * Started new Server on " + self.host + ":" + str(self.port))

  def listen(self):
    self.sock.listen(5)
    while True:
        client, address = self.sock.accept()
        client.settimeout(60)
        Thread(target = self.listenToClient,args = (client,address)).start()
        logging.info(" * New client connected from " + str(address))

  def listenToClient(self, client, address):
    size = 1000000
    HEADERSIZE = 10
    while True:
      try:
        full_data = b''
        new_msg = True
        while True:
          data = client.recv(size)
          if data:
            if new_msg:
              data_length = int(data[:HEADERSIZE])
              new_msg = False

            full_data += data

            if len(full_data)-HEADERSIZE == data_length:
              data = (pickle.loads(full_data[HEADERSIZE:]))
              names, locations = self.worker.detect(data)

              data = pickle.dumps([locations, names])
              data = bytes(f"{len(data):<{HEADERSIZE}}", 'utf-8')+data
              client.send(data)
              logging.debug(' * Sent back data to client')
              new_msg = True
              full_data = b""
          else:
              logging.info('Client disconnected: ' + str(address))
              raise error('Client disconnection')
      except:
        client.close()
        return False
  
  def stop(self):
    #TODO Stop server safely
    logging.info(" * Closing socket, KeyboardInterrupt")
    self.socket.close()
    return