import os
import shutil
import time
import datetime
from exif import Image
from functools import reduce

sourceDirectories = [  # '/home/justin/.gvfs/Justin \xe3\x81\xae iPhone/DCIM/100APPLE',
    # '/home/justin/.gvfs/Justin \xe3\x81\xae iPhone/DCIM/101APPLE',
    '/media/justin/NEW VOLUME',
    '/media/justin/FC30-3DA9',
    '/home/justin/temp/PhotoDump',
    '/home/justin/Drives/2.3TB/downloads/photos']

mediaDirectory = "/home/justin/Drives/2.3TB/Pictures"


def exif_date(path):
	"""
	Given the path of a file returns the exif datetime of a file
	"""

    with open(path, 'rb') as image_file:
        my_image = Image(image_file)

    if my_image.has_exif:
        date = datetime.datetime.strptime(my_image.datetime, "%Y:%m:%d %H:%M:%S")
		print("exif date", path, date)
        return date
    
    return False

def getDate(file):
    "returns the date of creation for a file in yyyy-mm-dd"

	date = exif_date(file)
	if not date:
    	date = time.strptime(time.ctime(os.path.getmtime(file)))

    # some code to deal with photos in a different time zone:
#	date = datetime.datetime(date[year], date[month], date[day], date[hour], date[minute])
#	timedelta = datetime.timedelta(0,16*60*60) #16 hours for Canada
#	date = date - timedelta
#	date = (date.year, date.month, date.day)

    dateStr = date.strftime("%Y_%m_%d")
    return dateStr


def getDirectoryList(path):
    """returns a list of directories in a path"""
    dirList = ["/".join([path, object]) for object in os.listdir(path)]
    dirList = [object for object in dirList if os.path.isdir(object)]
    return dirList


def getMediaFileList(path):
    """returns a list of media files in a path,returns a list of JPG and MOV files"""

    fileTypes = ("jpg", "mov", "mp4")
    dirList = ["/".join([path, object]) for object in os.listdir(path)]
    fileList = [object for object in dirList if os.path.isfile(object)]
    fileList = [file for file in fileList if file.split(".")[1].lower() in fileTypes]

    # for the new canon camera, ther are some .Trash and trashinfo files, want to ignore them
    fileList = [file for file in fileList if "trash" not in file and "Trash" not in file]
    return fileList


def getMountedMediaDirectories():
    validDirectories = [directory for directory in sourceDirectories if os.path.exists(directory)]
    return validDirectories


def getMediaFiles(path):
    """function to get list of JPG and .mov files, recursively checks paths"""
    fileList = getMediaFileList(path)
    dirList = getDirectoryList(path)

    results = map(getMediaFiles, dirList)

    for result in results:
        fileList = fileList + result

    return fileList


def makeDirs(directories):
    """creates directories as necessary for pictures"""
    createList = [directory for directory in directories if not os.path.exists(directory)]
# 	map(os.mkdir, createList)
    for directory in createList:
        os.mkdir(directory)


def copyMedia(source, target):
    """copies media to the media directory from the dateDict"""
    if not os.path.exists(target):
        print("copying source,target:", source, target)
        shutil.copy2(source, target)


if __name__ == "__main__":
    # getting list of files
    directories = getMountedMediaDirectories()
    def combine(x, y): return x + y
    mediaFileList = reduce(combine, map(getMediaFiles, directories))

    # getting a dateList
    dateList = map(getDate, mediaFileList)
    targetDirectories = ["/".join([mediaDirectory, date]) for date in dateList]

    # make directories
    makeDirs(set(targetDirectories))

    # convert targetDirectories to copy targets to copy files
    def getFilename(f): return f.split("/")[-1]
    copyTargetList = ["/".join([targetDir, getFilename(mediaFile)])
                      for targetDir, mediaFile in zip(targetDirectories, mediaFileList)]

    errors = []
    for source, target in zip(mediaFileList, copyTargetList):
        try:
            copyMedia(source, target)
        except OSError:
            errors.append(source)
            print("error transferring", source)
