
import face_recognition
import cv2
import numpy as np
import os

from .faceserver import logging

class FaceWorker():
  def __init__ (self):
    self.queue = []
    self.loaded_encodings = []
    self.loaded_names = []
    self.dbPath = "./catchall/face_database/"
    self.cachePath = "./catchall/face_cache/"
    logging.info(' * FaceWorker class initalized')
    self.load()

  def load(self):
    logging.info(" * Loading Database...")
    for person in os.listdir(self.dbPath):
        name = os.listdir(self.dbPath + person)

        if (os.path.exists(self.cachePath + person + ".fe")):
          try:
            cacheData = np.fromfile(self.cachePath + person + ".fe")

            self.loaded_encodings.append(cacheData)
            self.loaded_names.append(person)

            logging.info(self.dbPath + person + " Loaded! ( Through Cached Data )")
          except Exception as e:
            logging.error(' * ERROR: Could not load ' + person + ' from cache!: ' + str(e))
        else:
          for face in name:
              try:
                  img = face_recognition.load_image_file(self.dbPath + person + "/" + face)
                  locations = face_recognition.face_locations(img, number_of_times_to_upsample=0, model="cnn")
                  encodedImg = face_recognition.face_encodings(img, locations)[0]
                  
                  logging.info(" * Caching face Data")
                  encodedImg.tofile(self.cachePath + person + ".fe")

                  self.loaded_encodings.append(encodedImg)
                  self.loaded_names.append(person)
                  logging.info(" * " + self.dbPath + person + "/" + face + " Loaded!")
              except IndexError:
                  logging.error(" * \bCould not find a suitable face in " + self.dbPath + person + ", please use a new image!")

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

