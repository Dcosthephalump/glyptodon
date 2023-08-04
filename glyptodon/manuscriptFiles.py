# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_manuscriptFiles.ipynb.

# %% auto 0
__all__ = ['createManuscriptDirectory', 'dictToList', 'directoryNameClean', 'saveImages', 'saveTranscripts', 'currentManuscripts',
           'zipManuscript', 'updateMetadata', 'manuscriptImages']

# %% ../nbs/01_manuscriptFiles.ipynb 3
import os
import io
import cv2
import re
import numpy as np
import base64
from PIL import Image

# %% ../nbs/01_manuscriptFiles.ipynb 5
def createManuscriptDirectory(metadata:dict):
    # This function creates a directory and metadata file for a new manuscript and returns the new manuscript root directory
    
    # Establishing the baseDirectory the web app is running in
    baseDirectory = os.getcwd()
    os.chdir('manuscripts')
    allManuscriptsDirectory = os.getcwd()

    # Creating the root directory for a new manuscript
    title = directoryNameClean(metadata['Work'])
    print(title)
    manuscriptDirectory = os.path.join(allManuscriptsDirectory,title)
    os.mkdir(manuscriptDirectory)
    
    # Creating directories
    imagesDirectory = os.path.join(manuscriptDirectory,'images')
    os.mkdir(imagesDirectory)
    statesDirectory = os.path.join(manuscriptDirectory,'states')
    os.mkdir(statesDirectory)
    exportTranscriptDirectory = os.path.join(manuscriptDirectory,'exportTranscripts')
    os.mkdir(exportTranscriptDirectory)
    importTranscriptDirectory = os.path.join(manuscriptDirectory,'importTranscripts')
    os.mkdir(importTranscriptDirectory)
    
    # Creating metadata file as config file
    os.chdir(manuscriptDirectory)
    f = open(title + '.cfg', 'w')
    
    # Writes relevant metadata to file
    printable = dictToList(metadata)
    for data in printable:
        f.write(data + '\n')
    
    # Moves into 'states' directory to add line and bbox folders
    os.chdir(statesDirectory)
    linesDirectory = os.path.join(statesDirectory, 'lines')
    os.mkdir(linesDirectory)
    bboxesDirectory = os.path.join(statesDirectory, 'bboxes')
    os.mkdir(bboxesDirectory)
    
    os.chdir(baseDirectory)
    
    return manuscriptDirectory

# %% ../nbs/01_manuscriptFiles.ipynb 8
def dictToList(thisdict:dict):
    # This function turns a dictionary into a list of printable strings
    keys = []
    for key in thisdict.keys():
        keys.append(key)

    values = []
    for value in thisdict.values():
        values.append(value)
    
    printable = []
    for i in range(len(keys)):
        printable.append(str(keys[i]) + ':' + str(values[i]))
    
    return printable

# %% ../nbs/01_manuscriptFiles.ipynb 11
def directoryNameClean(string):
    # This breaks a string down into individual words and
    words = string.split()
    upperWords = []
    for word in words:
        if word[0].isupper():
            upperWords.append(word)
        elif word.isalpha() == False:
            upperWords.append(word)
    
    string = ''
    for word in upperWords:
        string = string + word
    
    # This loop removes any of the illegal characters for directories
    # It also removes periods as a stylistic choice (file extensions are found at periods)
    illegalChars = ['\\','#','%','&','{','}','<','>','*','?','/',' ','$','!',"'",'"',':','@','+','`','|','=','.']
    for char in illegalChars:
        removalCount = 0
        numChars = len(string)
        for i in range(len(string)):
            if string[i] == char:
                string = string[:i] + string[i+1:]
                removalCount = removalCount + 1

            if numChars - removalCount - 1 == i:
                break
    
    # This loop removes any vowels in an overly long string
    vowels = ['a','e','i','o','u']
    if len(string) > 26:
        for char in vowels:
            removalCount = 0
            numChars = len(string)
            for i in range(len(string)):
                if string[i] == char:
                    while string[i] == char:
                        string = string[:i] + string[i+1:]
                        removalCount = removalCount + 1
                
                if numChars - removalCount - 1 == i:
                    break
    
    if len(string) > 26:
        string = string[0:26]
    
    return string.lower()

# %% ../nbs/01_manuscriptFiles.ipynb 16
def saveImages(contents, filenames, targetDirectory):
    # This function saves content from memory into storage using the keys in the passed files dict (from a FileUpload widget)
    # This
    baseDirectory = os.getcwd()
    os.chdir(os.path.join(targetDirectory, "images"))
    
    if type(contents) != list:
        contents = [contents]
        filenames = [filenames]
    
    for i in range(0, len(contents)):
        string64 = contents[i].encode("utf8").split(b";base64,")[1]
        imdata = base64.b64decode(string64)
        pilImage = Image.open(io.BytesIO(imdata))
        cv2Image = cv2.cvtColor(np.array(pilImage), cv2.COLOR_BGR2RGB)
        cv2.imwrite("test" + filenames[i], cv2Image)
    
    os.chdir(baseDirectory)

# %% ../nbs/01_manuscriptFiles.ipynb 19
def saveTranscripts(contents, filenames, targetDirectory):
    baseDirectory = os.getcwd()
    os.chdir(os.path.join(targetDirectory, "importTranscripts"))
    
    if type(contents) != list:
        contents = [contents]
        filenames = [filenames]
    
    for i in range(0, len(contents)):
        string64 = contents[i].encode("utf8").split(b";base64,")[1]
        message = base64.b64decode(string64).decode('utf-8')
        f = open(filenames[i], 'w')
        f.write(message)
    
    os.chdir(baseDirectory)

# %% ../nbs/01_manuscriptFiles.ipynb 23
def currentManuscripts():
    # If this is run on any computer, it will have a unique file structure. This implementation works with that file structure.
    baseDirectory = os.getcwd()
    manuscriptDirectory = os.path.join(baseDirectory,'manuscripts')
    
    # This is necessary to keep directories accessible. Without os.path.join, we can't keep a full directory name and access files inside specific directories
    directories = []
    for path in os.listdir(manuscriptDirectory):
        directories.append(os.path.join(manuscriptDirectory,path))
    
    # This is necessary to store metadata from .cfg files
    manuscriptMetadata = []
    
    # This is necessary to search each directory in the manuscripts folder
    for directory in directories:
        # This looks through each file in a given directory
        for file in os.listdir(directory):
            # This opens config files and reads metadata from them
            if file.endswith('.cfg'):
                fileDirectory = os.path.join(directory,file)
                f = open(fileDirectory, 'r')
                metadata = {}

                for line in f:
                    key, value = line.split(':')
                    metadata[key] = value[:-1]

                manuscriptMetadata.append((directory, metadata))
    
    os.chdir(baseDirectory)
    return manuscriptMetadata

# %% ../nbs/01_manuscriptFiles.ipynb 26
def zipManuscript(directoryOptions: list, manuscriptDirectory, name: str):
    import zipfile
    # standard call here to avoid getting the system lost in directories
    baseDirectory = os.getcwd()
    
    lowerOptions = []
    for option in directoryOptions:
        lowerOptions.append(option.lower())
    
    files = []
    for path in os.listdir(manuscriptDirectory):
        # this deletes any currently zipped folder
        if path.endswith(".zip"):
            os.remove(os.path.join(manuscriptDirectory, path))
        
        # this collects all the files inside option folders
        if path in lowerOptions:
            if path == "states":
                tempDirectoryStates = os.path.join(manuscriptDirectory, path)
                for statesPath in os.listdir(tempDirectoryStates):
                    if statesPath in ["bboxes","lines"]:
                        tempDirectory = os.path.join(tempDirectoryStates, statesPath)
                        for file in os.listdir(tempDirectory):
                            files.append(os.path.join(tempDirectory, file))
            else:
                tempDirectory = os.path.join(manuscriptDirectory, path)
                for file in os.listdir(tempDirectory):
                    files.append(os.path.join(tempDirectory, file))
    
    # this zips the collected files
    os.chdir(manuscriptDirectory)
    for file in files:
        zipfile.ZipFile(
            file=name + ".zip",
            mode="a",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=3,
        ).write(file)
    
    # standard call here to move back to the application's main directory
    os.chdir(baseDirectory)

    return os.path.join(manuscriptDirectory, name + ".zip")

# %% ../nbs/01_manuscriptFiles.ipynb 29
def updateMetadata(directory, information):
    baseDirectory = os.getcwd()
    
    for file in os.listdir(directory):
        if file.endswith('.cfg'):
            os.chdir(directory)
            f = open(file, 'w')
            printable = dictToList(information)
            for data in printable:
                f.write(data + '\n')
    
    os.chdir(baseDirectory)

# %% ../nbs/01_manuscriptFiles.ipynb 32
def manuscriptImages(targetDirectory):
    baseDirectory = os.getcwd()
    # Now, getting a relative pathway to the manuscript
        # The slice removes an annoying slash from the string at the first index
    relativeToManuscript = re.sub(baseDirectory, "", targetDirectory)[1::]
    relativeToImages = os.path.join(relativeToManuscript, 'images')
    
    # Now we pull out every file in the directory into a list
    files = []
    for file in os.listdir(relativeToImages):
        files.append(file)
        
    # We sort the list alphanumerically
    files.sort()
    
    # Then we join each file to the relative pathway to the images folder
    # It also keeps an index that can be accessed by the dropdown
    relativePaths = []
    for file in files:
        relativePaths.append(os.path.join(relativeToImages, file))
    
    return relativePaths
