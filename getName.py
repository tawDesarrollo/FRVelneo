from face_recognition import face_encodings, compare_faces
from datetime import datetime
from cv2 import VideoCapture
from random import shuffle
from cv2 import imread
import pickle
import time
import json
import os
import re

#-------------Log_Variables-----------------
start = time.time()
version = "1.0.0"
today = datetime.now()
today = today.strftime(r"%d-%m-%Y %H:%M:%S")
status = {'unknownPerson':'No identificado', 'moreThanOnePerson': 'Muchas personas en la imagen', 'noPersonsFound': 'No se encontraron personas'}
global log
log = {}
#--------------------------------------------

#-------------Rute_Variables-----------------
global inputFolder, dbFolder
localDir = '/home/MLP/FRVelneo/'
inputFolder = localDir+'DatasetLogIn/'
dbFolder = localDir+'DatasetUser/Output'
#--------------------------------------------

def recognize(img, dbPath: str) -> str:
    '''
    img: image to compare
    dbPath: str rute to the database of all known faces
    --------------------------------------------------------------------------------------------------
    It takes the given image and compares it by iterating in random order the existing files in the database
    Returns the name in db when it finds a match with an error less than 0.5 (in Euclidean distance), unkownPerson when it is not a match and finally noPersonsFounds when it finds no face in the image.
    If there is more than one person fund in the img, it will return moreThanOnePerson

    return str nameOfKnownPerson | unknownPerson | noPersonsFound | moreThanOnePerson
    '''
    embeddignsUnkown = face_encodings(img)
    if len(embeddignsUnkown) == 0:
        return 'noPersonsFound'
    elif len(embeddignsUnkown) > 1:
        return 'moreThanOnePerson'
    else:
        embeddignsUnkown = embeddignsUnkown[0]

    dbDir = os.listdir(dbPath)
    shuffle(dbDir)
    match = False
    j = 0
    while not match and j < len(dbDir):
        path_ = os.path.join(dbPath, dbDir[j])
        file = open(path_, 'rb')
        embeddings = pickle.load(file) 
        match = compare_faces([embeddings], embeddignsUnkown, tolerance=0.5)[0]
        j+=1

    if match:
        return dbDir[j - 1].split("_")[0]
    else:
        return 'unknownPerson'

def isPhoto(photos: list):
    '''
    photos: list(str) list of strings with all the files names
    inputFolder: str rute with all files to compare
    dbFolder: str rute to the database of all known faces
    ----------------------------------------------------------------
    first filter out all photos containing the same indicator name
    Then compares the photos one by one with the database to obtain the most repeated name
    '''
    for photo in photos:
        img = imread(inputFolder+photo)
        fr = recognize(img, dbFolder)
        log.update({f'{fr}': log[f'{fr}']+1}) if fr in log.keys() and fr != "noPersonsFound" else log.update({f'{fr}': 1})
        #os.remove(inputFolder+photo)

def isVideo(video: str):
    '''
    video: str file name of the video to read
    inputFolder: str rute with all files to compare
    dbFolder: str rute to the database of all known faces
    ----------------------------------------------------------------
    First reads the video via cv2 and gets the frames 
    Then compares the frames one by one with the database to obtain the most repeated name
    '''

    cap = VideoCapture(inputFolder+video) 
    b = 0 

    while b < 5: #Max number of frames to compare
        success, img = cap.read()
        if not success:
            break
        try:
            val = face_encodings(img)[0]
            b +=1
        except:
            pass
        fr = recognize(img, dbFolder).split("_")[0]
        log.update({f'{fr}': log[f'{fr}']+1}) if fr in log.keys() and fr != "noPersonsFound" else log.update({f'{fr}': 1})

    #os.remove(inputFolder+video)

def getUserName(Session_ID):
    files = os.listdir(inputFolder)
    if len(files) == 0: return{'message': '404 no se encuentran imagenes para inicio de sesion'}
    reg = re.compile(fr'{Session_ID}(?:_[0-9]{{1,2}})?.{files[0].split(".")[1]}')
    files = list(filter(reg.match, files))
    if len(files) == 0: return {'message': '404 no se encuentran imagenes de dicha sesion para procesar'} 
    isPhoto(files) if files[0].split(".")[1] in ['jpg', 'png', 'jpeg'] else isVideo(files[0])

    end = time.time()-start

    data = {'FR_ID': max(log, key=log.get), 'version': version, 'fecha': today, 'tiempoDeInferencia': end, 'message': '200 Proceso ejecutado de forma adecuada', 'status': 'Identificado' if max(log, key=log.get) not in status.keys() else status[max(log, key=log.get)]}
    with open(f'{localDir}Logs/Inferencia/{files[0].split("_")[0]}.json', 'w') as newfile:
        newfile.write(json.dumps(data))
    return data
