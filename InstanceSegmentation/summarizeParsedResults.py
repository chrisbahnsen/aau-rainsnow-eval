import json
import os
import cv2

import cocoTools

import copy
from pycocotools import coco
from pycocotools.cocoeval import COCOeval
import numpy as np
import pickle



methods = ['baseline',
           'GargNayar-Median',
           'GargNayar-STCorr',
           'Kang2012',
           'Kim2015-blur',
           'Fu2017',
           'IDCGAN']
           
           

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

methodTranslator = {'baseline': 'Original',
                    'Fu2017': 'Fu2017 \cite{Fu2017RemovingRF}',
                    'GargNayar-Median': 'Median',
                    'GargNayar-STCorr': 'Garg2007 \cite{garg2007vision}',
                    'IDCGAN': 'Zhang2017 \cite{Zhang2017ImageDeraining}',
                    'Kim2015-blur': 'Kim2015 \cite{kim2015video}',
                    'Kang2012': 'Kang2012 \cite{kang2012automatic}'}

orderedSequences = ['Egensevej-1', 
                    'Egensevej-2',
                    'Egensevej-3',
                    'Egensevej-4',
                    'Egensevej-5',
                    'Hadsundvej-1',
                    'Hadsundvej-2',
                    'Hasserisvej-1',
                    'Hasserisvej-2',
                    'Hasserisvej-3',
                    'Hjorringvej-1',
                    'Hjorringvej-2',
                    'Hjorringvej-3',
                    'Hjorringvej-4',
                    'Hobrovej-1',
                    'Ostre-1',
                    'Ostre-2',
                    'Ostre-3',
                    'Ostre-4',
                    'Ringvej-1',
                    'Ringvej-2',
                    'Ringvej-3',
                    'Own dataset average']


def formatSignificantDigits(q, n):
    """
    Truncate a float to n significant figures, with exceptions for numbers below 1
    Only works for numbers [-100;100]
    Arguments:
        q : a float
        n : desired number of significant figures # Hard-coded
    Returns:
    Float with only n s.f. and trailing zeros, but with a possible small overflow.
    """

    if abs(q) < 10:
        return '{: 3.2f}'.format(q)
    else:
        return '{: 3.1f}'.format(q)


def toTex(file):
    newFileName = file.replace('.csv', '.tex')
    newF = open(newFileName, 'w')
    lineNumber = 0

    with open(file, 'r') as f:
        for line in f:
    
            newLine = line.replace(';','&')
            newLine = newLine.replace('\n', '\\\\\n')
            newLine = newLine.replace('baseline', 'Original')
            newLine = newLine.replace('GargNayar-Median','Median')
            newLine = newLine.replace('Kang2012','Kang2012 \cite{kang2012automatic}')
            newLine = newLine.replace('GargNayar-STCorr','Garg2007 \cite{garg2007vision}')
            newLine = newLine.replace('Kim2015-blur','Kim2015 \cite{kim2015video}')
            newLine = newLine.replace('IDCGAN','Zhang2017 \cite{Zhang2017ImageDeraining}')
            newLine = newLine.replace('Fu2017', 'Fu2017 \cite{Fu2017RemovingRF}')

            if lineNumber > 1:
                # We are moving to the actual numbers of the table
                columns = newLine.split('&')
                formattedColumns = copy.deepcopy(columns)
                
                highestMoGValue = -100;
                highestMoGIndex = -1
                highestSuBValue = -100;
                highestSuBIndex = -1

                for i in range(1, 3):
                    partitioned = columns[i].partition('\\')
                    formattedColumns[i] = formatSignificantDigits(float(partitioned[0]), 3) + ''.join(partitioned[1:])

                for i in range(3, len(columns)):
                    partitioned = columns[i].partition('\\')
                    # strippedColumn = columns[i].replace('\\','').replace('\n','')
                    formattedColumns[i] = formatSignificantDigits(float(partitioned[0]), 3) + ''.join(partitioned[1:])
                    
                    if i % 2 == 0:
                        if float(partitioned[0]) > highestSuBValue:
                            highestSuBIndex = i
                            highestSuBValue = float(partitioned[0])    
                    else:
                        if float(partitioned[0]) > highestMoGValue:
                            highestMoGIndex = i
                            highestMoGValue = float(partitioned[0])

                if highestMoGIndex != -1:
                    partitioned = formattedColumns[highestMoGIndex].partition('\\')

                    formattedColumns[highestMoGIndex] = '\\textbf{' + partitioned[0] + '}' + ''.join(partitioned[1:])

                if highestSuBIndex != -1:
                    partitioned = formattedColumns[highestSuBIndex].partition('\\')

                    formattedColumns[highestSuBIndex] = '\\textbf{' + partitioned[0] + '}' + ''.join(partitioned[1:])
                    newLine = '&'.join(formattedColumns)
            
            newF.write(newLine)

            lineNumber += 1

resultsCatalogue = dict()


# Get the parsed results and evaluate using the COCO API
with open('./splitSequenceTranslator.json', 'r') as f:
    splitSequenceTranslator = json.load(f)

for method in methods:
    gtFile = os.path.join('./', method + '-dontCare.json')   
    
    gtCoco = coco.COCO(gtFile)

    methodResults = dict()

    if method == 'baseline':
        msGtFile = 'rainSnowGt.json'

        fbResFile = os.path.join('./Results/parsed/', 
                               'segmentations_aaurainsnow_results-ignore-dontCare.json')
        msResFile = os.path.join('./Results/fcis/', 'detections_annotations_results.json')

        msGtCoco = coco.COCO(msGtFile)
        msMethodRes = msGtCoco.loadRes(msResFile)
    else:
        fbResFile = os.path.join('./Results/parsed/', 
                            'segmentations_aaurainsnow_' +
                            method +
                            '_results-ignore-dontCare.json')
        msResFile = os.path.join('./Results/fcis-parsed/', 
                                 'detections_' + 
                                 method + 
                                 '_results-ignore-dontCare.json')
        msMethodRes = gtCoco.loadRes(msResFile)

    fbMethodRes = gtCoco.loadRes(fbResFile)

    for sequenceNumber in range(0, 2200, 100):
        imgIds = list(range(sequenceNumber, sequenceNumber + 100))

        sceneSequence = splitSequenceTranslator[str(sequenceNumber)]
        sequenceName = sceneSequence[0] + '/' + sceneSequence[1]
        translatedSequence = publishedSequenceTranslator[sequenceName]

        useCats = [True, False]
        useCatResults = dict()
        cnnMethodResults = dict()
        
        for useCat in useCats:
            fbCocoEval = COCOeval(gtCoco, fbMethodRes, 'segm')
            fbCocoEval.params.imgIds = imgIds
            fbCocoEval.params.useCats = useCat
            fbCocoEval.evaluate()
            fbCocoEval.accumulate()
            fbCocoEval.summarize()

            fbStats = fbCocoEval.stats
            useCatResults['FB Category: ' + str(useCat)] = fbStats.tolist()

            if method == 'baseline':
                msCocoEval = COCOeval(msGtCoco, msMethodRes, 'segm')
            else:
                msCocoEval = COCOeval(gtCoco, msMethodRes, 'segm')

            msCocoEval.params.imgIds = imgIds
            msCocoEval.params.useCats = useCat
            msCocoEval.evaluate()
            msCocoEval.accumulate()
            msCocoEval.summarize()

            msStats = msCocoEval.stats
            useCatResults['MS Category: ' + str(useCat)] = msStats.tolist()

        methodResults[translatedSequence] = useCatResults

    # Compute the all sequence average
    useCatResults = dict()

    for useCat in useCats:
        fbCocoEval = COCOeval(gtCoco, fbMethodRes, 'segm')
        fbCocoEval.params.imgIds = range(0, 2200)
        fbCocoEval.params.useCats = useCat
        fbCocoEval.evaluate()
        fbCocoEval.accumulate()
        fbCocoEval.summarize()

        fbStats = fbCocoEval.stats
        useCatResults['FB Category: ' + str(useCat)] = fbStats.tolist()

        if method == 'baseline':
            msCocoEval = COCOeval(msGtCoco, msMethodRes, 'segm')
        else:
            msCocoEval = COCOeval(gtCoco, msMethodRes, 'segm')

        msCocoEval.params.imgIds = range(0, 2200)
        msCocoEval.params.useCats = useCat
        msCocoEval.evaluate()
        msCocoEval.accumulate()
        msCocoEval.summarize()

        msStats = msCocoEval.stats
        useCatResults['MS Category: ' + str(useCat)] = msStats.tolist()
    methodResults['Own dataset average'] = useCatResults

    resultsCatalogue[method] = methodResults

with open('summarizedParsedResults.json', 'w') as f:
    json.dump(resultsCatalogue, f)

# Intermediate dumping of results for fast resuming of the script
pickle.dump(resultsCatalogue, open('resultsCatalogue.p', 'wb'))
resultsCatalogue = pickle.load(open('resultsCatalogue.p', 'rb'))

# Write the results to csv-files 
with open('summarizeParsedResults.csv', 'w') as f:
    with open('summarizedParsedResults-percentages.csv', 'w') as fP:
        firstRow = ['Sequence']
        secondRow = ['']
        for method in methods:
            firstRow.append(method)
            firstRow.append('')
            secondRow.append('FB')
            secondRow.append('MS')

        f.write(';'.join(firstRow) + '\n')
        f.write(';'.join(secondRow) + '\n')
        fP.write(';'.join(firstRow) + '\n')
        fP.write(';'.join(secondRow) + '\n')

        for sequence in orderedSequences:
            row = [sequence]
            percentagesRow = [sequence]

            for method in methods:
                if 'baseline' in method:
                    percentagesRow.append(str(resultsCatalogue[method][sequence]['FB Category: False'][0]))
                    percentagesRow.append(str(resultsCatalogue[method][sequence]['MS Category: False'][0]))
                else:
                    # Compute the percentual difference compared to baseline
                    if resultsCatalogue['baseline'][sequence]['FB Category: False'][0] > 0.:
                        catDiff = ((resultsCatalogue[method][sequence]['FB Category: False'][0] -
                                    resultsCatalogue['baseline'][sequence]['FB Category: False'][0]) /
                                    resultsCatalogue['baseline'][sequence]['FB Category: False'][0] * 100.)
                        percentagesRow.append(str(catDiff))
                    else:
                        percentagesRow.append('-')
                    
                    if resultsCatalogue['baseline'][sequence]['MS Category: False'][0] > 0.:
                        noCatDiff = ((resultsCatalogue[method][sequence]['MS Category: False'][0] -
                                    resultsCatalogue['baseline'][sequence]['MS Category: False'][0]) /
                                    resultsCatalogue['baseline'][sequence]['MS Category: False'][0] * 100.)
                        percentagesRow.append(str(noCatDiff))      
                    else:
                        percentagesRow.append('-')

                row.append(str(resultsCatalogue[method][sequence]['FB Category: False'][0]))
                row.append(str(resultsCatalogue[method][sequence]['MS Category: False'][0]))

            line = ';'.join(row)
            f.write(line + '\n')
            fP.write(';'.join(percentagesRow) + '\n')

# And format these CSV-files such that they fit nicely in a LaTeX paper
toTex('summarizedParsedResults-percentages.csv')
