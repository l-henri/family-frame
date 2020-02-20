import email
import getpass, imaplib
import os
import sys
## Sur mac:
##    sys.path.append("/usr/local/lib/python2.7/site-packages")
from PIL import Image, ExifTags
import time
import numpy as np
import json


##### Program variables
pictureDirectory = "pics"
archiveDirectory = "archive"
detach_dir = 'photos/'
maxPic = 40
picDisplayTime = 60*60*24*14
# picDisplayTime = 10


###### Functions
# Removing older files
def cleanFile():
    print("################# Starting file cleaning routine")
    fileList = os.listdir(detach_dir+pictureDirectory)
    pictureNumber = len(fileList)
    print("There are %s pictures in %s folder" % (pictureNumber, pictureDirectory))
    removedPics = 0 
    
    # Retrieving name and date of creation of pictures
    timestampsList = []
    # print(fileList)
    for pictureName in fileList:
        picturePath = detach_dir + pictureDirectory  + "/" +  pictureName
        pictureBirth = os.path.getmtime(picturePath)
        timestampsList.append(pictureBirth)
        # print(pictureName, pictureBirth)

    # Formatting for numpy
    arrayBase = [(timestampsList[i], fileList[i]) for i in range(0, len(timestampsList))]
    # print("arrayBase")
    # print(arrayBase)
    dtype = [('timestamp', float), ('filename', 'S150')]
    arrayBaseNp = np.array(arrayBase, dtype=dtype)
    # print("arrayBaseNp")
    # print(arrayBaseNp)

    # Sorting using timestamp
    arrayBaseOrderedNp = np.sort(arrayBaseNp, order='timestamp')
    # print(arrayBaseOrderedNp)
    arrayBaseOrder = arrayBaseOrderedNp.tolist()
    # print(arrayBaseOrder)

    # Extracting as a list
    orderedFilesList = []
    for pictureInfo in arrayBaseOrder:
        orderedFilesList.append(pictureInfo[1].decode("utf-8") )

    # Going through file list to clean
    for pictureName in orderedFilesList:
        # Checking that minimum amount of pictures is present
        picturesLeft = pictureNumber - removedPics
        # if picturesLeft <= maxPic:
        #     print("%s pictures left. We want at least %s pictures, not removing any" % (picturesLeft, maxPic))
        #     break

        print("There are enough pictures, we can remove an older one. Checking if this one is old enough.")
        #### Checking if any older picture can be remove
        picturePath = detach_dir + pictureDirectory  + "/" +  pictureName
        pictureBirth = os.path.getmtime(picturePath)
        if pictureBirth < time.time() - picDisplayTime:
            print("Picture " + pictureName + " will be moved")
            print(pictureBirth)
            newPicturePath =  detach_dir + archiveDirectory  + "/" +  pictureName
            os.rename(picturePath, newPicturePath)
            removedPics = removedPics + 1
        else:
            print("Picture %s was added not too long ago, we leave it there" % pictureName)

def checkOrientation(filepath):
    try:
        image=Image.open(filepath)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                # print "Breaking here"
                break
        exif=dict(image._getexif().items())

        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
            print("Rotation 180")
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
            print("Rotation 270")
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)
            print("Rotation 90")
        image.save(filepath)
        image.close()

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

def retrieveNewPhotos():
    userData = loadSecretData()
    userName = userData['username']
    passwd = userData['password']
    try:
        print("Connecting to imap server")
        imapSession = imaplib.IMAP4_SSL('mail.register.eu')
        print("Opening session")
        typ, accountDetails = imapSession.login(userName, passwd)
        if typ != 'OK':
            print('Not able to sign in!')
            raise
        print("Selecting emails")
        imapSession.select('INBOX')
        # typ, data = imapSession.search(None, 'ALL')
        deadline = time.time() - picDisplayTime
        requestTime = time.strftime('%d-%b-%Y', time.localtime(deadline))
        print("Searching inbox for emails after " + str(requestTime))

        typ, data = imapSession.search(None, '(SINCE ' + requestTime+ ')')
        
        if typ != 'OK':
            print('Error searching Inbox.')
            raise
        print ("Iterating over all emails")
        # Iterating over all emails
        for msgId in data[0].split():
            typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
            if typ != 'OK':
                print ('Error fetching mail.')
                raise

            emailBody = messageParts[0][1]
            mail = email.message_from_string(emailBody)
            for part in mail.walk():

                if part.get_content_maintype() == 'multipart':
                    # print part.as_string()
                    continue
                if part.get('Content-Disposition') is None:
                    # print part.as_string()
                    continue
                fileName = part.get_filename()
                # Checking if a file is attached
                if bool(fileName):
                    filePath = os.path.join(detach_dir, 'pics', fileName)
                    if not os.path.isfile(filePath) :
                        print("File %s has been found" % fileName)
                        # print filePath
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        checkOrientation(filePath)
        imapSession.close()
        imapSession.logout()
    except :
        print('Not able to download all attachments.')

def loadSecretData():
    with open("secretData.json") as json_file:
        return json.load(json_file)

####### Program
def main():
    # Checking if data dirs are here
    if detach_dir[0:len(detach_dir)-1] not in os.listdir('.'):
        os.mkdir(detach_dir)
    if pictureDirectory not in os.listdir(detach_dir):
        os.mkdir(detach_dir+pictureDirectory)
    if archiveDirectory not in os.listdir(detach_dir):
        os.mkdir(detach_dir+archiveDirectory)

    retrieveNewPhotos()   
    cleanFile()

if __name__ == '__main__':
    main()
