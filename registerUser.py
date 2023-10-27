from face_recognition import face_encodings
from datetime import datetime
from cv2 import VideoCapture
from cv2 import imread
import pickle
import shutil
import json
import time
import re
import os

#-------------Log_Variables-----------------
start = time.time()
version = "1.0.0"
today = datetime.now()
today = today.strftime(r"%d-%m-%Y %H:%M:%S")
#--------------------------------------------

#--------------Rute_Variables----------------------
global inputFolder, outputFolder, trainingFolder
localDir = '/home/MLP/FRVelneo/'
inputFolder = localDir+'DatasetUser/Input/'
outputFolder = localDir+'DatasetUser/Output/'
trainingFolder = localDir+'DatasetUser/Training/'
#--------------------------------------------------

def isPhoto(photos, sID):
    '''
    photos: list(str) list of strings with all the files names
    inputFolder: str rute with all files to compare
    ----------------------------------------------------------------
    Loads every photo in the array of photos, tries to get the embedding and, if there is a face, saves the embedding as seraliaze binary (with pickle)
    '''
    j = 0
    for photo in photos:
        img = imread(inputFolder+sID+'/'+photo)
        try:
            emmbeding = face_encodings(img)[0]
            os.makedirs(outputFolder+sID, exist_ok=True)
            file = open(os.path.join(outputFolder, sID,f'{str(photo.split("_")[0])}_{str(photo.split("_")[1])}_{j}'), 'wb')
            pickle.dump(emmbeding, file)
            j += 1
        except:
            pass
    return j

def isVideo(video):
    '''
    video: str file name of the video to read
    inputFolder: str rute with all files to compare
    trainingFolder: str rute to move the file so we can use it later on for training
    ----------------------------------------------------------------
    First reads the video via cv2 and gets the frames 
    Then, see which of those frame are usefull and save it as a serialize binary (with pickle)
    Finally, moves the video to the trainingFolder
    '''
    j = 0

    cap = VideoCapture(str(inputFolder+video))

    shutil.move(inputFolder+video, trainingFolder+video)

    while j<=50:
        success, img = cap.read()
        if not success:
            break
        try:
            embedding = face_encodings(img)[0]
            file = open(os.path.join(outputFolder, f'{str(video.split(".")[0])}_{j}'), 'wb')
            pickle.dump(embedding, file)
            j += 1
        except:
            pass
        return j

def registerNewUser(Session_ID):
    '''
    Session_ID: str identifier of wihch session is trying to register a new user
    ------------------------------------------------------------------------------
    Load all the files in the folder of the input
    Filters only the ones which contain 
    '''
    sID = Session_ID.split('_')[0]
    files = os.listdir(inputFolder+sID)
    reg = re.compile(fr'{Session_ID}(?:_[0-9]{{1,2}})?.(jpg|png|jpeg|mp4)')
    files = list(filter(reg.match, files))

    if len(files) == 0: return {'message': '404 No hay fotos para hacer el registro'}

    j = isPhoto(files, sID) if files[0].split(".")[1] in ['jpg', 'png', 'jpeg'] else isVideo(files[0])

    end = time.time()-start

    data = {'numeroDeFotosGuardadas': j, 'version': version, 'fecha': today, 'tiempoDeInferencia': end, 'message': '200 Proceso ejecutado con exito'}
    with open(f'{localDir}/Logs/Alta/{files[0].split("_")[0]}Foto.json', 'w') as newfile:
        newfile.write(json.dumps(data))
    return data
