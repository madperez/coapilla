#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 13:49:34 2020

@author: nautica
"""

import face_recognition
import cv2
import numpy as np
import glob
import os
import logging
import anvil.server
from PIL import Image
from io import BytesIO
from ocr_ife import ocr_ife


IMAGES_PATH = './images'  # put your reference images in here
VIDEOS_PATH='./videos'
VALIDATIONS_PATH='./validations'
IFES_PATH='./ife'
IFE_PATH='./ife/'
CAMERA_DEVICE_ID = 0
MAX_DISTANCE = 0.6  # increase to make recognition less strict, decrease to make more strict

def get_face_embeddings_from_image(image, convert_to_rgb=False):
    """
    Take a raw image and run both the face detection and face embedding model on it
    """
    # Convert from BGR to RGB if needed
    if convert_to_rgb:
        image = image[:, :, ::-1]

    # run the face detection model to find face locations
    face_locations = face_recognition.face_locations(image)

    # run the embedding model to get face embeddings for the supplied locations
    face_encodings = face_recognition.face_encodings(image, face_locations)

    return face_locations, face_encodings
def setup_database():
    """
    Load reference images and create a database of their face encodings
    """
    database = {}

    for filename in glob.glob(os.path.join(IFES_PATH, '*.png')):
        # load image
        image_rgb = face_recognition.load_image_file(filename)

        # use the name in the filename as the identity key
        identity = os.path.splitext(os.path.basename(filename))[0]

        # get the face encoding and link it to the identity
        locations, encodings = get_face_embeddings_from_image(image_rgb)
        database[identity] = encodings[0]

    return database
def setup_database_vida():
    """
    Load reference images and create a database of their face encodings
    """
    database = {}

    for filename in glob.glob(os.path.join(IFES_PATH, '*.png')):
        # load image
        image_rgb = face_recognition.load_image_file(filename)

        # use the name in the filename as the identity key
        identity = os.path.splitext(os.path.basename(filename))[0]

        # get the face encoding and link it to the identity
        locations, encodings = get_face_embeddings_from_image(image_rgb)
        database[identity] = encodings[0]

    return database
def paint_detected_face_on_image(frame, location, name=None):
    """
    Paint a rectangle around the face and write the name
    """
    # unpack the coordinates from the location tuple
    top, right, bottom, left = location

    if name is None:
        name = 'Unknown'
        color = (0, 0, 255)  # red for unrecognized face
    else:
        color = (0, 128, 0)  # dark green for recognized face

    # Draw a box around the face
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

    # Draw a label with a name below the face
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
def run_face_recognition(database,video):
    """
    Start the face recognition via the webcam
    """
    # Open a handler for the camera
    video_capture = cv2.VideoCapture(video)
    print(video.ulr)
    #video_capture=video
    #video_capture = cv2.VideoCapture(CAMERA_DEVICE_ID)

    # the face_recognitino library uses keys and values of your database separately
    known_face_encodings = list(database.values())
    known_face_names = list(database.keys())
    
    while video_capture.isOpened():
        # Grab a single frame of video (and check if it went ok)
        ok, frame = video_capture.read()
        if not ok:
            logging.error("Could not read frame from camera. Stopping video capture.")
            break

        # run detection and embedding models
        face_locations, face_encodings = get_face_embeddings_from_image(frame, convert_to_rgb=True)

        # Loop through each face in this frame of video and see if there's a match
        for location, face_encoding in zip(face_locations, face_encodings):

            # get the distances from this encoding to those of all reference images
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            # select the closest match (smallest distance) if it's below the threshold value
            if np.any(distances <= MAX_DISTANCE):
                best_match_idx = np.argmin(distances)
                name = known_face_names[best_match_idx]
            else:
                name = None

            # put recognition info on the image
            print(name)
            paint_detected_face_on_image(frame, location, name)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
def run_face_recognition_vida(database):
    """
    Start the face recognition via the webcam
    """
    # Open a handler for the camera
    
    video_capture = cv2.VideoCapture(VIDEOS_PATH+'/pic.mp4')
    #video_capture=video
    #video_capture = cv2.VideoCapture(CAMERA_DEVICE_ID)

    # the face_recognitino library uses keys and values of your database separately
    known_face_encodings = list(database.values())
    known_face_names = list(database.keys())
    
    while video_capture.isOpened():
        # Grab a single frame of video (and check if it went ok)
        ok, frame_temp = video_capture.read()
        frame=cv2.rotate(frame_temp,cv2.ROTATE_180)
        if not ok:
            logging.error("Could not read frame from camera. Stopping video capture.")
            break

        # run detection and embedding models
        face_locations, face_encodings = get_face_embeddings_from_image(frame, convert_to_rgb=True)

        # Loop through each face in this frame of video and see if there's a match
        for location, face_encoding in zip(face_locations, face_encodings):

            # get the distances from this encoding to those of all reference images
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            # select the closest match (smallest distance) if it's below the threshold value
            if np.any(distances <= MAX_DISTANCE):
                best_match_idx = np.argmin(distances)
                name = known_face_names[best_match_idx]
            else:
                name = None

            # put recognition info on the image
            print(name)
            paint_detected_face_on_image(frame, location, name)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
#database = setup_database()
#run_face_recognition(database)


anvil.server.connect("VWJJR3IQJL33IXWPJLZDMBZN-TJLJJRNF2KMJQU54")

@anvil.server.callable
def analisis_ife(media_image):
    estatus,nombre=ocr_ife(media_image)
    return estatus,nombre

@anvil.server.callable
def say_hello(name):
  print("Hello from the uplink, %s!" % name)

@anvil.server.callable
def save_ife(photo,clave_elector):
    #pil_image=Image.open(BytesIO(media_image.get_bytes()))
    pil_image=Image.open(BytesIO(photo.get_bytes()))
    pil_image.save(IFE_PATH+clave_elector+'.png',"png")
    print('hola mundo')
@anvil.server.callable
def save_video(video):
    # Open and write the returned media object to a binary file ("wb" for write binary)
    with open(VIDEOS_PATH+"/pic.mp4", "wb") as fp:
        fp.write(video.get_bytes())
@anvil.server.callable
def process_video():
    print('creating database')
    database=setup_database_vida()
    print('processing video')
    run_face_recognition_vida(database)
@anvil.server.callable
def identify_video(link):
    """
    Load reference images and create a database of their face encodings
    """
    print('procesando video')
    anvil.media.download(link)
    database = setup_database()
    run_face_recognition(database,video)

    return database
anvil.server.wait_forever()
