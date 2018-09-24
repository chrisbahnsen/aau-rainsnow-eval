#MIT License
#
#Copyright (c) 2016 Aalborg University
#Chris H. Bahnsen, November 2016
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
from collections import namedtuple
import copy
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

TrackingParams = namedtuple('TrackingParams', ['method', 'trackingDuration', 'maxPixelError'])



def statAggregator(baseFolder):
    """
    Traverses the basefolder and its subfolders for stat files produced by 
    the changedetection.net framework, and presents these stat files in 
    a number of overview files
    """

    allStats, overviewStats = getStatsFromSubfolder(baseFolder)

    pickle.dump(allStats, open('allStats.p', 'wb'))
    pickle.dump(overviewStats, open('overviewStats.p', 'wb'))

    allStats = pickle.load(open('allStats.p', 'rb'))
    overviewStats = pickle.load(open('overviewStats.p', 'rb'))


    writeStatTables(allStats, overviewStats)



def getStatsFromSubfolder(folder):

    allStats = {}
    overviewStats = {}
    subFolderAllStats = {}
    subFolderOverviewStats = {}

    print('Investigating folder {}'.format(folder))

    if (os.path.exists(path.join(folder, 'featureStats.txt')) 
        and os.path.exists(path.join(folder, 'detailedFeatureStats.txt'))):
        overviewStats = readBasicStatFile(path.join(folder, 'featureStats.txt'))
        allStats = readDetailedStatFile(path.join(folder, 'detailedFeatureStats.txt'))

        print('Found stats file...')

    for dir in os.listdir(folder):
        if path.isdir(os.path.join(folder, dir)):
            newAllStats, newOverviewStats = getStatsFromSubfolder(os.path.join(folder, dir))
                
            if newAllStats and newOverviewStats and "RainRemoval" not in dir:
                subFolderAllStats[dir] = newAllStats
                subFolderOverviewStats[dir] = newOverviewStats
                print('Found stats file in subfolders of {}'.format(folder))
            elif newAllStats and newOverviewStats:
                subFolderAllStats = newAllStats;
                subFolderOverviewStats = newOverviewStats

    if subFolderAllStats and subFolderOverviewStats:
        return subFolderAllStats, subFolderOverviewStats
    else:
        return allStats, overviewStats



def readBasicStatFile(filePath):
    """ 
    Read stat file generated from FeatureTrackingAccuracy  
    """
    f = open(filePath, 'r')

    overviewStats = {}

    for line in f:
        entries = line.split(';')

        if len(entries) > 5:
            m = entries[0]
            dur = int(entries[1])

            for i in range(2, len(entries), 2):
                if (i + 1) < len(entries):
                    mPE = float(entries[i])
                    featureCount = int(entries[i + 1])

                    singleStat = TrackingParams(method=m, trackingDuration=dur, maxPixelError=mPE)
                    overviewStats[singleStat] = featureCount
                



    return overviewStats

def readDetailedStatFile(filePath):
    """ 
    Read stat file generated from FeatureTrackingAccuracy  
    """
    f = open(filePath, 'r')

    allStats = {}

    prevParams = []
    startFrames = {}
    featureCounts = {}

    for line in f:
        entries = line.split(';')

        if len(entries) > 5:
            m = entries[0]
            dur = int(entries[1])
            startFrame = int(entries[2])
            mPE = float(entries[3])
            featureCount = int(entries[4])

            currentParams = TrackingParams(method=m, trackingDuration=dur, maxPixelError=mPE)

            if (currentParams not in prevParams):
                # We are now entering a new set of coordinates (method, trackingDuration) 
                # that we have not encountered previously. Save the previous statistics
                # and prepare for a new set of measures
               
                # We assume that we have two sets of parameters in the file to be 
                # analysed
                if len(prevParams) > 1:
                    for param in prevParams:
                        if (param.maxPixelError in startFrames and 
                            param.maxPixelError in featureCounts):
                            frameNumbers = startFrames[param.maxPixelError]
                            counts = featureCounts[param.maxPixelError]
                            zipped = zip(frameNumbers, counts)

                            allStats[param] = zipped

                    prevParams = []
                    startFrames = {}
                    featureCounts = {}

                prevParams.append(currentParams)
                startFrames[mPE] = [startFrame]
                featureCounts[mPE] = [featureCount]
            else:
                # Append to existing lists
                startFrames[mPE].append(startFrame)
                featureCounts[mPE].append(featureCount)
                              



    return allStats



def writeStatTables(allStats, overviewStats):
    """
    Writes overview tables of the aggregated statistics in .csv-format.

    One file per (trackingDuration, maximumPixelError) pair is created, 
    in two different flavours:
    
    1) Overview, containing summarised numbers of the entire category, for each site and method.
       This is based on overviewStats
    2) Detailed, containing performance of each time instance

    The .csv-files are created using the following structure:
    EXAMPLE ----- fmeasure-all.csv ----- EXAMPLE
    
                    ; Method1; Method2, Method2; ...            
    SequenceName1   ; 
    SequenceName2   ; 
    SequenceName3   ; 
    ...             ;
    ...             ;
    """

    # Create overview statistics files
    statFileHandlers = {}
    statFiles = {}
    durationMPEPairs = []

    for siteKey, site in overviewStats.items():
        for dateTimeKey, dateTime in site.items():
            mPE = 0
            trackingDuration = 0

            if isinstance(site[dateTimeKey], (list, tuple, dict)): # Dig deeper
                for paramsKey, featureCount in dateTime.items():
                    mPE = paramsKey.maxPixelError
                    trackingDuration = paramsKey.trackingDuration

                    if (mPE, trackingDuration) not in durationMPEPairs:
                        durationMPEPairs.append((mPE, trackingDuration))
            else:
                mPE = dateTimeKey.maxPixelError
                trackingDuration = dateTimeKey.trackingDuration

                if (mPE, trackingDuration) not in durationMPEPairs:
                    durationMPEPairs.append((mPE, trackingDuration))

    rowPairs = {}

    for durationMPEPair in durationMPEPairs:
        statFileHandlers[durationMPEPair] = open('overview-maxPixelError-' + str(durationMPEPair[0]) 
                                                 + '-trackingDuration-' + str(durationMPEPair[1]) +
                                                 '.csv', 'wb')
        statFiles[durationMPEPair] = csv.writer(statFileHandlers[durationMPEPair], delimiter=';')
        rowPairs[durationMPEPair] = {}
    
    # Create a suitable header that includes all methods
    firstRowText = ''
    allMethods = []

    for siteKey, site in overviewStats.items():
        for dateTimeKey, dateTime in site.items():
            method = ''

            if isinstance(site[dateTimeKey], (list, tuple, dict)): # Dig deeper
                for paramsKey, featureCount in dateTime.items():
                    if paramsKey.method not in allMethods:
                        allMethods.append(paramsKey.method)
            else:
                if dateTimeKey.method not in allMethods:
                    allMethods.append(dateTimeKey.method)

    allMethods.sort()
    firstRowText = ['', ''] + allMethods
        
    for durationMPEPair in durationMPEPairs:
        statFiles[durationMPEPair].writerow(firstRowText)
            
    # Start writing the actual data
    for siteKey, site in overviewStats.items():

        rows = copy.deepcopy(rowPairs)

        for dateTimeKey, dateTime in site.items():
            if isinstance(site[dateTimeKey], (list, tuple, dict)): # Dig deeper
                rows = copy.deepcopy(rowPairs)

                for paramsKey, featureCount in dateTime.items():
                    mPE = paramsKey.maxPixelError
                    trackingDuration = paramsKey.trackingDuration

                    rows[(mPE, trackingDuration)][paramsKey.method] = featureCount

                for durationMPEPair in durationMPEPairs:
                    line = [siteKey] + [dateTimeKey]
                
                    for method in allMethods:
                        if method in rows[durationMPEPair]:
                            line.append(rows[durationMPEPair][method])
                        else:
                            line.append('')

                    statFiles[durationMPEPair].writerow(line)
                    line = []
                rows = None
            else:               
                mPE = dateTimeKey.maxPixelError
                trackingDuration = dateTimeKey.trackingDuration

                rows[(mPE, trackingDuration)][dateTimeKey.method] = dateTime

        if rows:
            for durationMPEPair in durationMPEPairs:   
                line = [siteKey] + ['']
                
                for method in allMethods:
                    if method in rows[durationMPEPair]:
                        line.append(rows[durationMPEPair][method])
                    else:
                        line.append('')

                statFiles[durationMPEPair].writerow(line)
                line = []
            rows = None

    for statFileHandlerKey, statFileHandler in statFileHandlers.items():
        statFileHandler.close()     

    # We currently don't write the detailed stats to files. 
    # The level of detail that these files would provide are not needed right now

    return



def convertCommaInFile(file):
    newFileName = file.replace('.csv', '-a.csv')
    newF = open(newFileName, 'w', newline = '')

    with open(file, 'r') as f:
        for line in f:
            newLine = line.replace('.',',')
            newF.write(newLine)
    


parser = argparse.ArgumentParser(description='Aggregates statistics from subfolders and produces a number of overview files', epilog='Searches for stat files produced by FeatureTrackingAccuracy')
parser.add_argument('-f', dest='baseFolder')

args = parser.parse_args()

if args.baseFolder:
    baseFolder = args.baseFolder

    statAggregator(baseFolder)
