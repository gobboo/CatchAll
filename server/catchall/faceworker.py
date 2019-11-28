
import face_recognition
import cv2
import numpy as np

from .faceserver import logging

class FaceWorker():
  def __init__ (self):
    self.queue = []
    self.loaded_encodings = []
    self.loaded_names = []
    logging.info(' * FaceWorker class initalized')

  def load(self, id):
    return

  def detect(self, frame):
    logging.debug(' * Detecting faces')
    face_locations = face_recognition.face_locations(frame, number_of_times_to_upsample=0, model="cnn")
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    #Check if this data is in the database, if not save it so we can get it from cache next time

    face_names = []
    for face_encoding in face_encodings:
      matches = face_recognition.compare_faces(self.loaded_encodings, face_encoding)
      logging.debug(' * Found ' + str(len(matches)) + " Face matches")
      name = "Unknown"

      if(len(matches) > 0):
        face_distances = face_recognition.face_distance(self.loaded_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            logging.debug(" * Found match.")
            name = self.loaded_names[best_match_index]
      
      face_names.append(name)
    logging.debug(' * Detected ' + str(len(face_encodings)) + ' Faces.')

    return face_names, face_locations

  def cache(self, frame):
    return

