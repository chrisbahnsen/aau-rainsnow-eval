#MIT License
#
#Copyright (c) [2016] [Aalborg University]
#Chris Bahnsen, June 2016
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

    if os.path.exists(path.join(folder, 'stats.txt')):
        allStats, overviewStats = readStatFile(path.join(folder, 'stats.txt'))

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



def readStatFile(filePath):
    """ 
    Read stat file generated from CDNet and returns a list of tuples representing the data
    The tuples represents:
    (folderName, recall, specificity, FPR, FNR, PBC, precision, f-measure)
    """
    f = open(filePath, 'r')

    allStats = {}
    overviewStats = {}
    category = ''
    folder = ''
    method = ''

    for line in f:
        # Check if the line contains the 'cm' character and thus provides information of the specific folder
        if 'cm' in line:
            words = line.split()

            for word in words:
                if '/' in word:
                    # All processed folder has either a /MoG or /SubSENSE folder. Exploit this to get the filename
                    category = os.path.basename(os.path.dirname(os.path.dirname(os.path.normpath(filePath))))
                    folder = os.path.basename(os.path.dirname(os.path.normpath(filePath)))
                    method = word

                    # Get the raw FP, TN, etc. count
                    folderNumbers = {'TP': words[4], 'FP': words[5], 'FN': words[6], 'TN': words[7],
                                     'ErrorShadow': words[8]}
                    overviewStats[method] = folderNumbers


        # CHeck if line is not empty, does not contain certain characters, and that the folder has been found
        if '#' not in line and 'cm' not in line and line and folder and '\n' != line and method:
            measures = line.split()

            isRealMeasure = True

            for measure in measures:
                if not RepresentsFloat(measure):
                    isRealMeasure = False
                    break


            if len(measures) == 7 and isRealMeasure:
                folderStats = {'recall': measures[0], 'specificity': measures[1], 'FPR': measures[2], 'FNR': measures[3], 
                              'PBC': measures[4], 'precision': measures[5], 'f-measure': measures[6]}
                allStats[method] = folderStats

                method = ''

    return allStats, overviewStats

def writeStatTables(allStats, overviewStats):
    """
    Writes overview tables of the aggregated statistics in .csv-format.

    The following tables are provided:
    recall, specificity, FPR, FNR, PBC, precision, f-measure 

    in two different flavours:
    1) Overview, containing summarised numbers of the entire category, for each method
    2) All, containing performance of single sequences/folders, for each method

    The .csv-files are created using the following structure:
    EXAMPLE ----- fmeasure-all.csv ----- EXAMPLE
    
                    ; Method1; Method2, Method2; ...            
    SequenceName1   ; 
    SequenceName2   ; 
    SequenceName3   ; 
    ...             ;
    ...             ;
    """

    # Create all stats 
    statFileHandlers = {}
    statFiles = {}
    measures =  ['recall', 'specificity', 'FPR', 'FNR', 'PBC', 'precision', 'f-measure']

    for measure in measures:
        statFileHandlers[measure] = open(measure + '-all.csv', 'w', newline='')
        statFiles[measure] = csv.writer(statFileHandlers[measure], delimiter=';')
    
    firstRowText = ''
    allMethods = []

    for categoryKey, category in allStats.items():

        # Check the number of subSubCategories inside the subCategories and issue a warning
        # if the count of subSubCategories for different subCategories does not match

        for subCategoryKey, subCategory in category.items():
            for subSubCategoryKey, subSubCategory in subCategory.items():
                if subSubCategoryKey not in allMethods:
                    allMethods.append(subSubCategoryKey)


    firstRowText = [''] + allMethods
        
    for measure in measures:
        statFiles[measure].writerow(firstRowText)
            

    for categoryKey, category in allStats.items():
        for subCategoryKey, subCategory in category.items():

            rows = {'recall': [categoryKey + '/' + subCategoryKey], 'specificity' : [categoryKey + '/' + subCategoryKey], 'FPR' : [categoryKey + '/' + subCategoryKey], 'FNR' : [categoryKey + '/' + subCategoryKey], 'PBC' : [categoryKey + '/' + subCategoryKey], 'precision' : [categoryKey + '/' + subCategoryKey], 'f-measure': [categoryKey + '/' + subCategoryKey]}
            for method in allMethods:

                if method in subCategory:
                    if isinstance(subCategory[method], (list, tuple, dict)):
                        for methodKey, value in subCategory[method].items():
                            rows[methodKey] = rows[methodKey] + [float(value)]
                    else:
                        print('Error')
                else:
                    for measure in measures:
                        rows[measure] = rows[measure] + [''] # Write empty entry at this column


            for measure in measures:
                statFiles[measure].writerow(rows[measure])

    for statFileHandlerKey, statFileHandler in statFileHandlers.items():
        statFileHandler.close()

    # 1) Overview, containing summarised numbers of the entire category, for each method
    # From the overview stats, summarise by method and folder
    overallRawStats = {} # Overall stats, summarised by method, i.e. Kim2015-no-blur
    siteRawStats = {} # Stats for each method, summarised by folder, i.e. Kim2015-no-blur/Egensevej

    for siteKey, site in overviewStats.items():
        if categoryKey not in siteRawStats:
            siteRawStats[siteKey] = {}

        for sequenceKey, sequence in site.items():
            if len(subCategory.items()) > 1:

                for methodKey, method in sequence.items():
                    if methodKey not in siteRawStats[siteKey]:
                        siteRawStats[siteKey][methodKey] = {}
                        
                    if methodKey not in overallRawStats:
                        overallRawStats[methodKey] = {}

                    for statKey, stat in method.items():
                        if statKey not in siteRawStats[siteKey][methodKey]:
                            siteRawStats[siteKey][methodKey][statKey] = float(stat)
                        else:
                            siteRawStats[siteKey][methodKey][statKey] += float(stat)


                        if statKey not in overallRawStats[methodKey]:
                            # Just add it
                            overallRawStats[methodKey][statKey] = float(stat)
                        else:
                            # Otherwise add to list
                            overallRawStats[methodKey][statKey] += float(stat)
    
    overallStatHandler = open('overallStats.csv', 'w', newline='')
    overallStatFile = csv.writer(overallStatHandler, delimiter=';')        
    siteStatHandler = open('statsPerSite.csv', 'w', newline='')
    siteStatFile = csv.writer(siteStatHandler, delimiter=';')

    # Write the header row
    subSubCategoryHeader = [''] + [''] + measures
    overallStatFile.writerow(subSubCategoryHeader)
    siteStatFile.writerow([''] + subSubCategoryHeader)

    # Get the recall, specificity and other measures from the summarised numbers and write them to the stat files
    for methodName, rawStats in overallRawStats.items():
        stats = getStats(rawStats)

        names = methodName.split('/')
        row = names

        for measure in measures:
            row = row + ['{:f}'.format(stats[measure])]

        overallStatFile.writerow(row)


    for siteName, methodStats in siteRawStats.items():

        for methodName, rawStats in methodStats.items():
            stats = getStats(rawStats)

            row = [siteName] + methodName.split('/')

            for measure in measures:
                row = row + ['{:f}'.format(stats[measure])]

            siteStatFile.writerow(row)
    
    overallStatHandler.close();
    siteStatHandler.close();

    # Convert the commas from "." to "," to allow processing in Excel
    convertCommaInFile('overallStats.csv')
    convertCommaInFile('statsPerSite.csv')

    for measure in measures:
        convertCommaInFile(measure + '-all.csv')


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
    newF = open(newFileName, 'w', newline = '')

    with open(file, 'r') as f:
        for line in f:
            newLine = line.replace('.',',')
            newF.write(newLine)
    


parser = argparse.ArgumentParser(description='Aggregates statistics from subfolders and produces a number of overview files', epilog='Searches for stat files produced by FeatureTrackingAccuracy.cpp')
parser.add_argument('-f', dest='baseFolder')

args = parser.parse_args()

if args.baseFolder:
    baseFolder = args.baseFolder

    statAggregator(baseFolder)
