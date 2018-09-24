#MIT License
#
#Copyright (c) 2017 Aalborg University
#Chris H. Bahnsen, September 207
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import argparse
import csv
import fileinput
from os import path
import pickle
import os
import string
import cv2

publishedSequenceTranslator = {'Egensevej/Egensevej-2': 'Egensevej-2',
                            'Egensevej/Egensevej-1' : 'Egensevej-1',
                            'Egensevej/Egensevej-4' : 'Egensevej-4',
                            'Egensevej/Egensevej-5' : 'Egensevej-5',
                            'Egensevej/Egensevej-3' : 'Egensevej-3',
                            'Ostre/Ostre-2' : 'Ostre-2',
                            'Ostre/Ostre-3' : 'Ostre-3',
                            'Ostre/Ostre-4' : 'Ostre-4',
                            'Ostre/Ostre-1' : 'Ostre-1',
                            'cdNet-badWeather/skating' : 'badWeather/skating',
                            'cdNet-badWeather/wetSnow' : 'badWeather/wetSnow',
                            'cdNet-badWeather/blizzard' : 'badWeather/blizzard',
                            'cdNet-badWeather/snowFall' : 'badWeather/snowFall',
                            'Hobrovej/Hobrovej-1' : 'Hobrovej-1',
                            'Hadsundvej/Hadsundvej-1' : 'Hadsundvej-1',
                            'Hadsundvej/Hadsundvej-2' : 'Hadsundvej-2',
                            'Hjorringvej/Hjorringvej-2' : 'Hjorringvej-2',
                            'Hjorringvej/Hjorringvej-4' : 'Hjorringvej-4',
                            'Hjorringvej/Hjorringvej-1' : 'Hjorringvej-1',
                            'Hjorringvej/Hjorringvej-3' : 'Hjorringvej-3',
                            'Ringvej/Ringvej-2' : 'Ringvej-2',
                            'Ringvej/Ringvej-1' : 'Ringvej-1',
                            'Ringvej/Ringvej-3' : 'Ringvej-3',
                            'Hasserisvej/Hasserisvej-2' : 'Hasserisvej-2',
                            'Hasserisvej/Hasserisvej-1' : 'Hasserisvej-1',
                            'Hasserisvej/Hasserisvej-3' : 'Hasserisvej-3'}



def evaluateObjectSize(baseFolder):
    """
    Traverses the base folder and its subfolders for rain removed frames
    and measures the mean processing time of each rain removal algorithm. 
    These measures are written to csv-files
    """

    #objectSizes = getObjectSizesFromSubFolder(baseFolder)

    #pickle.dump(objectSizes, open('objectSizes.p', 'wb'))
    objectSizes = pickle.load(open('objectSizes.p', 'rb'))
  
    writeStatTables(objectSizes)

def evaluateObjectsPerFrame(baseFolder):
    """
       
    """

    #objectsPerFrame = getObjectsPerFrameFromSubFolder(baseFolder)

    #pickle.dump(objectsPerFrame, open('objectsPerFrame.p', 'wb'))
    objectsPerFrame = pickle.load(open('objectsPerFrame.p', 'rb'))
  
    writeStatTables(objectsPerFrame)



def getObjectSizesFromSubFolder(folder):

    objectSizes = {}
    subFolderObjectSizes = {}

    print('Investigating folder {}'.format(folder))

    if isGroundTruth(folder):
        objectSizes = computeObjectSize(folder)
        print('Found rainRemoval algorithm...')

        if objectSizes > 0:
            return objectSizes
        else:
            return None

    for dir in os.listdir(folder):
        if path.isdir(os.path.join(folder, dir)):
            newObjectSizes = getObjectSizesFromSubFolder(os.path.join(folder, dir))
                
            if newObjectSizes and "RainRemoval" not in dir:
                subFolderObjectSizes[dir] = newObjectSizes
                print('Found rainRemoval algorithm in subfolders of {}'.format(folder))
            elif newObjectSizes:
                subFolderObjectSizes = newObjectSizes

    if subFolderObjectSizes:
        return subFolderObjectSizes
    else:
        return objectSizes

def getObjectsPerFrameFromSubFolder(folder):

    objectsPerFrame = {}
    subFolderObjectsPerFrame = {}

    print('Investigating folder {}'.format(folder))

    if isGroundTruth(folder):
        objectsPerFrame = computeObjectAppearance(folder)
        print('Found rainRemoval algorithm...')

        if objectsPerFrame > 0:
            return objectsPerFrame
        else:
            return None

    for dir in os.listdir(folder):
        if path.isdir(os.path.join(folder, dir)):
            newObjectsPerFrame = getObjectsPerFrameFromSubFolder(os.path.join(folder, dir))
                
            if newObjectsPerFrame and "RainRemoval" not in dir:
                subFolderObjectsPerFrame[dir] = newObjectsPerFrame
                print('Found rainRemoval algorithm in subfolders of {}'.format(folder))
            elif newObjectsPerFrame:
                subFolderObjectsPerFrame = newObjectsPerFrame

    if subFolderObjectsPerFrame:
        return subFolderObjectsPerFrame
    else:
        return objectsPerFrame

def isGroundTruth(folderName):
    if '-BG' in folderName:
        return False

    if 'groundtruth' in folderName:
        return True

    return False

def computeObjectSize(folderPath):
    """ 
    Go through the annotation files of each folder and compute the average object size
    """
    
    pixelCount = 0
    objectCount = 0
    numberOfFiles = 0

    for file in os.listdir(folderPath):
        if path.isfile(os.path.join(folderPath, file)):
            img = cv2.imread(os.path.join(folderPath, file))

            #cv2.imshow("Raw image", img)
            grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            maskedImg = cv2.inRange(grayImg, 171, 255)
            #cv2.imshow("Masked image", maskedImg)
            #cv2.waitKey(20)

            tmpPixelCount = cv2.countNonZero(maskedImg)
            pixelCount += tmpPixelCount

           
            im2, contours, hierarchy = cv2.findContours(maskedImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            tmpObjectCount = len(contours)
            objectCount += tmpObjectCount
            numberOfFiles += 1

            #if tmpPixelCount > 0 and tmpObjectCount > 0:
                #print("Average object size frame " + file + ": " + str(tmpPixelCount/tmpObjectCount))

            if tmpObjectCount == 0 and tmpPixelCount > 0:
                print("Something is wrong at frame " + file)
                        

    
    if numberOfFiles is 0:
        return -1;


    return pixelCount / objectCount

def computeObjectAppearance(folderPath):
    """ 
    Go through the annotation files of each folder and compute the average number of objects per frame
    """
    
    objectCount = 0
    numberOfFiles = 0

    for file in os.listdir(folderPath):
        if path.isfile(os.path.join(folderPath, file)):
            img = cv2.imread(os.path.join(folderPath, file))

            #cv2.imshow("Raw image", img)
            grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            maskedImg = cv2.inRange(grayImg, 171, 255)
           
            im2, contours, hierarchy = cv2.findContours(maskedImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            tmpObjectCount = len(contours)
            objectCount += tmpObjectCount
            numberOfFiles += 1                        

    
    if numberOfFiles is 0:
        return -1;


    return objectCount / numberOfFiles

def writeStatTables(allStats):
    """
    Writes overview tables of the aggregated statistics in .csv-format.

    The overview tables come in two different flavours:
    1) Overview, containing summarised numbers of the entire category, for each method
    2) All, containing performance of single sequences/folders, for each method

    The .csv-files are created using the following structure:
    EXAMPLE ----- all.csv ----- EXAMPLE
    
                    ; Method1; Method2, Method2; ...            
    SequenceName1   ; 
    SequenceName2   ; 
    SequenceName3   ; 
    ...             ;
    ...             ;
    """

    # Create all stats 

    allFileHandler = open('objectSize-all.csv', 'w', newline='')
    statFileAll = csv.writer(allFileHandler, delimiter=';')

    allMethods = [];

    for categoryKey, category in allStats.items():
        for subCategoryKey, subCategory in category.items():
            for subSubCategoryKey, subSubCategory in subCategory.items():

                if isinstance(subCategory[subSubCategoryKey], (list, tuple, dict)):
                    for methodKey, value in subSubCategory.items():
                        combinedKey = subSubCategoryKey + '-' + methodKey;

                        if combinedKey not in allMethods:
                            allMethods.append(combinedKey)
                elif subSubCategoryKey not in allMethods:
                    allMethods.append(subSubCategoryKey)


    firstRowText = [''] + allMethods
    statFileAll.writerow(firstRowText)

    
   
    for categoryKey, category in allStats.items():
        for subCategoryKey, subCategory in category.items():

            rows = [publishedSequenceTranslator[categoryKey + '/' + subCategoryKey]];

            for subSubCategoryKey, subSubCategory in subCategory.items():

                if isinstance(subCategory[subSubCategoryKey], (list, tuple, dict)):
                    for methodKey, value in subSubCategory.items():
                        rows = rows + ['{:g}'.format(value)]
                else:
                    rows = rows + ['{:g}'.format(subSubCategory)]

            statFileAll.writerow(rows)

    allFileHandler.close()
    convertCommaInFile('objectSize-all.csv')  


    return




def getStats(cm):
    """Return the usual stats for a confusion matrix."""

    measures = {}

    measures['recall'] = cm['TP'] / (cm['TP'] + cm['FN'])
    measures['specificity'] = cm['TN'] / (cm['TN'] + cm['FP'])
    measures['FPR'] = cm['FP'] / (cm['FP'] + cm['TN'])
    measures['FNR'] = cm['FN'] / (cm['TP'] + cm['FN'])
    measures['PBC'] = 100.0 * (cm['FN'] + cm['FP']) / (cm['TP'] + cm['FP'] + cm['FN'] + cm['TN'])
    measures['precision'] = cm['TP'] / (cm['TP'] + cm['FP'])
    measures['f-measure'] = 2.0 * (measures['recall'] * measures['precision']) / (measures['recall'] + measures['precision'])
    
    return measures


def convertCommaInFile(file):
    newFileName = file.replace('.csv', '-a.csv')
    newF = open(newFileName, 'w')#, newline='')

    with open(file, 'r') as f:
        for line in f:
            newLine = line.replace('.',',')
            newF.write(newLine)


parser = argparse.ArgumentParser(description='Gets the average object size from each folder', epilog='')
parser.add_argument('-f', dest='baseFolder')

args = parser.parse_args()

if args.baseFolder:
    baseFolder = args.baseFolder

    #evaluateObjectSize(baseFolder)
    evaluateObjectsPerFrame(baseFolder)
