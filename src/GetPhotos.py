import os
import shutil
import time
import datetime
from exif import Image
from functools import reduce

# using cable to connect to iphone is unreliable -- better to just sync to a server and then
# categorize the photos after
sourceDirectories = [  # '/home/justin/.gvfs/Justin \xe3\x81\xae iPhone/DCIM/100APPLE',
    # '/home/justin/.gvfs/Justin \xe3\x81\xae iPhone/DCIM/101APPLE',
    # '/media/justin/NEW VOLUME',
    # '/home/justin/temp/PhotoDump',
    '/home/justin/ownCloud/IphoneMedia',
    ]

mediaDirectory = "/home/justin/Drives/2.3TB/Pictures"


def exif_date(path):
    """
    Returns the exif date of an image file
    """

    # gets the exif data for jpg files
    ext = path.split(".")[-1].lower()
    if ext != "jpg":
        return False

    with open(path, "rb") as image_file:
        my_image = Image(image_file)

    if my_image.has_exif:
        try:
            date = datetime.datetime.strptime(my_image.datetime, "%Y:%m:%d %H:%M:%S")
            print("exif date", path, date)
        except AttributeError:
            print("attribute error on", path)
            return False
        return date

    return False


def getDate(file):
    "returns the date of creation for a file in yyyy-mm-dd"
    year = 0
    month = 1
    day = 2

    date = exif_date(file)

    if not date:
        date = time.strptime(time.ctime(os.path.getmtime(file)))
        date = datetime.date(date[year], date[month], date[day])

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
    fileList = []
    for base_dir, dirs, files in os.walk(path):
        fileList.extend([os.path.join(base_dir, f) for f in files if f.split(".")[1].lower() in fileTypes])

    # for the new canon camera, ther are some .Trash and trashinfo files, want to ignore them
    fileList = [file for file in fileList if "trash" not in file and "Trash" not in file]
    return fileList


def getMountedMediaDirectories():
    validDirectories = [directory for directory in sourceDirectories if os.path.exists(directory)]
    return validDirectories


def getMediaFiles(path):
    """function to get list of JPG and .mov files, recursively checks paths"""
    fileList = getMediaFileList(path)
    # dirList = getDirectoryList(path)

    # results = map(getMediaFiles, dirList)

    # for result in results:
    #     fileList = fileList + result

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
