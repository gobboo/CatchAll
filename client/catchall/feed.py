import cv2
import socket, pickle, time
from threading import Thread
from catchall import app, db
from .models import Stat
from notify_run import Notify
from datetime import datetime

class VideoCamera(object):
    def __init__(self):
        self.video = None
        self.process_this_frame = True
        self.stopped = False
        self.frame = None
        self.resolution = 1
        self.faces = 0
        self.timer = 0
        self.notify = Notify()
        self.ip = '127.0.0.1'
        self.port = 20000
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        self.connected = False
        self.HEADERSIZE = 10
        #First check if we can connect
        self.connect()

    def start(self):
        if self.connected:
            Thread(target=self.get_face, args=()).start()
        return self

    def stop(self):
        self.stopped = True
        self.video.release()
        self.s.close()

    def __del__(self):
        self.video.release()

    def connect(self):
        #self.s.settimeout(5)
        try:
            self.s.connect((self.ip, self.port))
            self.connected = True
        except socket.error as e:
            app.logger.error(" * Could not connect to facial recognition server: " + str(e))
            time.sleep(10)
            self.connect()

    def alert_user(self, name):
        if self.faces < 1:
            return

        #Check distance of faces
        #Check if in distance
        #Check if face has been present for x seconds
        #Alert user
        if time.time() > self.timer:
            app.logger.info("Found " + str(self.faces) + " Faces at the door with the name: " + name)
            self.timer = 999999999999
            
            if name == "Unknown":
                self.notify.send('Somebody unknown is at your door!')
            else:
                self.notify.send(name + " Is at your door !")
            
            #Check to see if there is a value for today
            #If so update to add new total ring and ring by + 1
            #If not then create a new one and use total rings of the last result and set rings to 0
            
            todayQuery = Stat.query.order_by(Stat.date.desc()).limit(1).all()

            if datetime.fromtimestamp(round(float(todayQuery[0].date))).date() == datetime.now().date():
                todayQuery[0].total_rings = todayQuery[0].total_rings + 1
                todayQuery[0].rings = todayQuery[0].rings + 1
                db.session.commit()
            else:
                db.session.add(Stat(total_rings=todayQuery[0].total_rings + 1, rings=1, date=datetime.timestamp(datetime.now())))
                db.session.commit()
            


    def get_face(self):
        if not self.connected:
            self.connect()

        if self.video is None:
            self.video = cv2.VideoCapture(0)

        while True:
            #print("loop")
            # Grab a single frame of video
            ret, frame = self.video.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=1, fy=1)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
            # Only process every other frame of video to save time
            if self.process_this_frame:
                data = pickle.dumps(rgb_small_frame)
                data = bytes(f"{len(data):<{self.HEADERSIZE}}", 'utf-8')+data
                self.s.send(data)

                #Wait for all the data to be recieved then do stuff afterwards
                full_data = b''
                new_msg = True
                while True:
                    data = self.s.recv(1000000)
                    if data:
                        if new_msg:
                            data_length = int(data[:self.HEADERSIZE])
                            new_msg = False

                        full_data += data

                        if len(full_data)-self.HEADERSIZE == data_length:
                            data = pickle.loads(full_data[self.HEADERSIZE:])
                            face_locations, face_names = data
                            new_msg = True
                            full_data = b""
                            break

            self.process_this_frame = not self.process_this_frame
            self.faces = len(face_names)

            if self.faces < 1:
                self.timer = round(time.time() + 10)

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                #print(top, right, bottom, left)
                top *= 1
                right *= 1
                bottom *= 1
                left *= 1

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                font = cv2.FONT_HERSHEY_DUPLEX
                size = cv2.getTextSize(name, font, 1.0, 1)
                
                cv2.rectangle(frame, (left, bottom + size[0][1]), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom + size[0][1]), font, 1.0, (255, 255, 255), 1)                

                self.alert_user(name)
                    
            

            ret, jpeg = cv2.imencode('.jpg', frame)
            self.frame = jpeg.tobytes()
