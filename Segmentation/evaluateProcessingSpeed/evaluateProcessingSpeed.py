#MIT License
#
#Copyright (c) [2016] [Aalborg University]
#Chris Bahnsen, November 2016
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
import locale

# http://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except
def RepresentsFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False


def evaluateProcessingSpeed(baseFolder):
    """
    Traverses the base folder and its subfolders for rain removed frames
    and measures the mean processing time of each rain removal algorithm. 
    These measures are written to csv-files
    """

    #processingSpeeds = getProcessingSpeedsFromSubFolder(baseFolder)

    #pickle.dump(processingSpeeds, open('processingSpeeds.p', 'wb'))

    allStats = pickle.load(open('processingSpeeds.p', 'rb'))
    


    writeStatTables(allStats)



def getProcessingSpeedsFromSubFolder(folder):

    processingSpeeds = {}
    subFolderProcessingSpeeds = {}

    print('Investigating folder {}'.format(folder))

    if isRainRemovalAlgorithm(folder):
        processingSpeeds = computeProcessingSpeed(folder)
        print('Found rainRemoval algorithm...')

        if processingSpeeds > 0:
            return processingSpeeds
        else:
            return None

    for dir in os.listdir(folder):
        if path.isdir(os.path.join(folder, dir)):
            newProcessingSpeeds = getProcessingSpeedsFromSubFolder(os.path.join(folder, dir))
                
            if newProcessingSpeeds and "RainRemoval" not in dir:
                subFolderProcessingSpeeds[dir] = newProcessingSpeeds
                print('Found rainRemoval algorithm in subfolders of {}'.format(folder))
            elif newProcessingSpeeds:
                subFolderProcessingSpeeds = newProcessingSpeeds

    if subFolderProcessingSpeeds:
        return subFolderProcessingSpeeds
    else:
        return processingSpeeds

def isRainRemovalAlgorithm(folderName):
    if '-BG' in folderName:
        return False

    if 'Kang2012' in folderName or 'Kim2015' in folderName:
        return True

    if 'IDCGAN' in folderName or 'Fu2017' in folderName:
        return True

    parentDir = os.path.dirname(folderName)

    if 'GargNayar' in parentDir and path.isdir(folderName):
        return True

    return False

def computeProcessingSpeed(folderPath):
    """ 
    Read the time of creation of each file and compute the mean 
    processing time of each file
    """

    meanProcessingTime = 0;
    totalProcessingTime = 0;
    numberOfFiles = 0;
    lastProcessedFrameTime = 0;
    fileList = os.listdir(folderPath)
    fileList.sort(key=lambda x: os.path.getmtime(os.path.join(folderPath, x)))

    for file in fileList:
        if path.isfile(os.path.join(folderPath, file)):
            currentFrameTime = os.path.getmtime(os.path.join(folderPath, file))

            diff = currentFrameTime - lastProcessedFrameTime

            if (diff < 14400 and diff > 0):
                # If the processing time is below 4 hours, proceed
                numberOfFiles += 1
                totalProcessingTime += diff

            lastProcessedFrameTime = currentFrameTime
    
    if numberOfFiles is 0:
        return -1;


    return totalProcessingTime / numberOfFiles

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

    allFileHandler = open('processingSpeed-all.csv', 'w', newline='')
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


    firstRowText = [''] + [''] + allMethods
    statFileAll.writerow(firstRowText)

    
   
    for categoryKey, category in allStats.items():
        for subCategoryKey, subCategory in category.items():

            rows = [categoryKey] + [subCategoryKey];

            for subSubCategoryKey, subSubCategory in subCategory.items():

                if isinstance(subCategory[subSubCategoryKey], (list, tuple, dict)):
                    for methodKey, value in subSubCategory.items():
                        rows = rows + [float(value)]
                else:
                    rows = rows + [float(subSubCategory)]

            statFileAll.writerow(rows)

    allFileHandler.close()
                    


    return




parser = argparse.ArgumentParser(description='Aggregates statistics from subfolders and produces a number of overview files', epilog='Measures the creating time of every file in a folder')
parser.add_argument('-f', dest='baseFolder')

args = parser.parse_args()

if args.baseFolder:
    baseFolder = args.baseFolder

    evaluateProcessingSpeed(baseFolder)
