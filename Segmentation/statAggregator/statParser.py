import argparse
import copy
import csv

def formatSignificantDigits(q,n):
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

def evaluateProcentualDifferenceSceneAverage(filePath, parsedFilePath, metric):

    filteredColumns = ['Sequence',
                       'baselineRGB/MoG',
                       'baselineRGB/SubSENSE',
                       'GargNayar-Median-BG/MoG',
                       'GargNayar-Median-BG/SubSENSE',
                       'GargNayar-STCorr-BG/MoG',
                       'GargNayar-STCorr-BG/SubSENSE',
                       'Kang2012-BG/MoG',
                       'Kang2012-BG/SubSENSE',
                       'Kim2015-blur-BG/MoG',
                       'Kim2015-blur-BG/SubSENSE',
                       'Fu2017-BG/MoG',
                       'Fu2017-BG/SubSENSE',
                       'IDCGAN-BG/MoG',    
                       'IDCGAN-BG/SubSENSE']

    sortedSequenceList = ['Egensevej-Klarupvej', 
                          'Hadsundvej-Humlebakken',
                          'KongChrAlle-Hasserisvej',
                          'Hjorringvej-Sundsholmen',
                          'Hobrovej-NyKaervej',
                          'OstreAlle-DagHammerskjoldsGade',
                          'IndreRingvej-Vesterbrogade',
                          'AAU RainSnow avg.',
                          'cdNet-badWeather']  

    publishedSequenceTranslator = {'Egensevej' : 'Egensevej-1-5',
                             'Ostre' : 'Ostre-1-4',
                             'cdNet-badWeather' : 'BadWeather avg.',
                             'Hobrovej' : 'Hobrovej-1',
                             'Hadsundvej' : 'Hadsundvej-1-2',
                             'Hjorringvej' : 'Hjorringvej-1-4',
                             'Ringvej' : 'Ringvej-1-3',
                             'Hasserisvej' : 'Hasserisvej-1-3', 
                             'AAU RainSnow avg.': 'AAU RainSnow avg.'}

    with open(filePath) as inputStat:
        with open(parsedFilePath, 'w') as outputLaTeX:
            with open(parsedFilePath.replace('.csv', '-percentages.csv'), 'w') as percentagesOutputLatex:

                # Create pretty headers for the tables
                prettyHeader1 = [] 
                prettyHeader2 = [] 

                previousColumn = ""

                templateResultsDir = {}
                allResultsDir = {}

                for column in filteredColumns:
                    methodSegmentation = column.split('/')

                    if len(methodSegmentation) >= 2:
                        if methodSegmentation[0] not in templateResultsDir:
                            templateResultsDir[methodSegmentation[0]] = {}

                        templateResultsDir[methodSegmentation[0]][methodSegmentation[1]] = {}

                    if 'MoG' in column:
                        if previousColumn not in column:
                            method = column.replace('/MoG', '')
                            previousColumn = method
                            prettyHeader1.append('\multicolumn{2}{l}{' + method + '}')
                        prettyHeader2.append('MoG')
                    elif 'SubSENSE' in column:
                        if previousColumn not in column:
                            method = column.replace('/SubSENSE', '')
                            previousColumn = method
                            prettyHeader1.append('\multicolumn{2}{l}{' + method + '}')
                        prettyHeader2.append('SuB')
                    else:
                        prettyHeader1.append(column)
                        prettyHeader2.append('')
                        previousColumn = column

                outputLaTeX.write(';'.join(prettyHeader1) + "\n")
                outputLaTeX.write(';'.join(prettyHeader2) + "\n")

                percentagesOutputLatex.write(';'.join(prettyHeader1) + "\n")
                percentagesOutputLatex.write(';'.join(prettyHeader2) + "\n")

                inputcsv = csv.reader(inputStat, delimiter=';')
                firstLine = None
                indexList = {}
                latexRows = {}

                for row in inputcsv:
                    filteredRow = [row[0]]

                    if not firstLine:
                        firstLine = row

                        for i in range(len(firstLine)):
                            indexList[firstLine[i]] = i
                            print('Added to indexList: ' + firstLine[i])

                        continue

                    if len(row) >= len(firstLine):
                        site = row[0]
                        rainRemovalMethod = row[1]
                        segmentationMethod = row[2]

                        if rainRemovalMethod == 'baseline':
                            rainRemovalMethod = 'baselineRGB'

                        if site not in allResultsDir:
                            allResultsDir[site] = copy.deepcopy(templateResultsDir)
                    
                        for i in range(3, len(row)):        
                            if rainRemovalMethod in allResultsDir[site]:
                                if segmentationMethod in allResultsDir[site][rainRemovalMethod]:
                                    allResultsDir[site][rainRemovalMethod][segmentationMethod][firstLine[i]] = float(row[i])

                # Now, write the results to the file
                for sequenceName in sortedSequenceList:
                    if sequenceName in allResultsDir:
                        rainRemovalMethod = allResultsDir[sequenceName]
                        resultsRow = [publishedSequenceTranslator[sequenceName]]
                        percentagesRow = [publishedSequenceTranslator[sequenceName]]

                        baselines = {}

                        for idx in range(1, len(filteredColumns)):
                            rainRemovalSegmentation = filteredColumns[idx].split('/')
                        
                            if rainRemovalSegmentation[0] in rainRemovalMethod:
                                segmentationMethod = rainRemovalMethod[rainRemovalSegmentation[0]]
                            elif rainRemovalSegmentation[0] == 'baselineRGB' and 'baseline' in rainRemovalMethod:
                                segmentationMethod = rainRemovalMethod['baseline']

                            if rainRemovalSegmentation[0] == 'baselineRGB':
                                percentagesRow.append(formatSignificantDigits(segmentationMethod[rainRemovalSegmentation[1]][metric], 3))

                                baselines[rainRemovalSegmentation[1]] = segmentationMethod[rainRemovalSegmentation[1]][metric]
                            else:
                                # Calculate percentual difference to the baseline results
                                percentagesRow.append(formatSignificantDigits((segmentationMethod[rainRemovalSegmentation[1]][metric] - 
                                                                               baselines[rainRemovalSegmentation[1]]) / 
                                                                               baselines[rainRemovalSegmentation[1]]*100, 3))

                            resultsRow.append(formatSignificantDigits(segmentationMethod[rainRemovalSegmentation[1]][metric], 3))

                        outputLaTeX.write(';'.join(resultsRow) + "\n")
                        percentagesOutputLatex.write(';'.join(percentagesRow) + "\n")
        


def evaluateProcentualDifference(filepath, parsedFilepath):
    """
    Takes in files as produced by StatAggregator ("*-all")
    and computes the percentual difference of methods as compared 
    to baseline methods
    """

    filteredColumns = ['Sequence',
                       'baselineRGB/MoG',
                       'baselineRGB/SubSENSE',
                       'GargNayar-Median-BG/MoG',
                       'GargNayar-Median-BG/SubSENSE',
                       'GargNayar-STCorr-BG/MoG',
                       'GargNayar-STCorr-BG/SubSENSE',
                       'Kang2012-BG/MoG',
                       'Kang2012-BG/SubSENSE',
                       'Kim2015-blur-BG/MoG',
                       'Kim2015-blur-BG/SubSENSE',
                       'Fu2017-BG/MoG',
                       'Fu2017-BG/SubSENSE',
                       'IDCGAN-BG/MoG',    
                       'IDCGAN-BG/SubSENSE']

                       #'GargNayar-Candidate-BG/MoG',
                       #'GargNayar-Candidate-BG/SubSENSE',
                       

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

    with open(filepath) as inputStat:
        with open(parsedFilepath, 'w') as outputLaTeX:
            # Create pretty headers for the tables
            prettyHeader1 = [] 
            prettyHeader2 = [] 

            previousColumn = ""

            for column in filteredColumns:
                if 'MoG' in column:
                    if previousColumn not in column:
                        method = column.replace('/MoG', '')
                        previousColumn = method
                        prettyHeader1.append('\multicolumn{2}{l}{' + method + '}')
                    prettyHeader2.append('MoG')
                elif 'SubSENSE' in column:
                    if previousColumn not in column:
                        method = column.replace('/SubSENSE', '')
                        previousColumn = method
                        prettyHeader1.append('\multicolumn{2}{l}{' + method + '}')
                    prettyHeader2.append('SuB')
                else:
                    prettyHeader1.append(column)
                    prettyHeader2.append('')
                    previousColumn = column

            outputLaTeX.write(';'.join(prettyHeader1) + "\n")
            outputLaTeX.write(';'.join(prettyHeader2) + "\n")

            inputcsv = csv.reader(inputStat, delimiter=';')
            firstLine = None
            indexList = {}
            latexRows = {}

            totalOwnDataset = ["Own dataset average"] + [0.]*(len(filteredColumns)-1)
            totalCdNet = ["badWeather average"] + [0.]*(len(filteredColumns)-1)


            for row in inputcsv:
                filteredRow = [row[0]]

                if not firstLine:
                    firstLine = row

                    for i in range(len(firstLine)):
                        indexList[firstLine[i]] = i
                        print('Added to indexList: ' + firstLine[i])

                    continue

                if len(row) >= len(firstLine):
                    for i in range(1, len(filteredColumns)):
                        number = 0.

                        try:
                            number = float(row[indexList[filteredColumns[i]]])
                        except ValueError:
                            try:
                                if 'baselineRGB/MoG' in filteredColumns[i]:
                                    number = float(row[indexList['baseline/MoG']])
                                elif 'baselineRGB/SubSENSE' in filteredColumns[i]:
                                    number = float(row[indexList['baseline/SubSENSE']])
                                else:
                                    print("Could not extract value from " + row[indexList[filteredColumns[i]]])
                            except ValueError:
                                print("Could not extract value from " + row[indexList[filteredColumns[i]]])
                        
                        if 'cdNet' in row[0]:
                            totalCdNet[i] += number
                        else:
                            totalOwnDataset[i] += number

                        filteredRow.append(number)
                        print(filteredColumns[i])

                # Now that we have acquired the row for the entire sequence, perform some actual 
                # math
                latexRow = [publishedSequenceTranslator[filteredRow[0]]]

                for i in range(1, len(filteredRow)):
                    if 'baseline' in filteredColumns[i]:
                        latexRow.append(formatSignificantDigits(filteredRow[i], 3))
                        continue

                    if 'MoG' in filteredColumns[i]:
                        latexRow.append(formatSignificantDigits((filteredRow[i]-filteredRow[1])/filteredRow[1]*100., 3))
                    elif 'SubSENSE' in filteredColumns[i]:
                        latexRow.append(formatSignificantDigits((filteredRow[i]-filteredRow[2])/filteredRow[2]*100., 3))

                    latexRows[publishedSequenceTranslator[filteredRow[0]]] = latexRow
            
            for translatedSequence, row in sorted(latexRows.items()):
                outputLaTeX.write(';'.join(row) + '\n')

            # Calculate the difference totals
            totalRows = [[], []]
            
            totalRows[0].append(totalOwnDataset[0])
            totalRows[1].append(totalCdNet[0])
            totalRows[0].append(formatSignificantDigits(totalOwnDataset[1] / 22., 3)) 
            totalRows[1].append(formatSignificantDigits(totalCdNet[1] / 4., 3))
            totalRows[0].append(formatSignificantDigits(totalOwnDataset[2] / 22., 3)) # Show the absolute numbers for the input frames
            totalRows[1].append(formatSignificantDigits(totalCdNet[2] / 4., 3))

            for i in range(3, len(totalOwnDataset)):                 
                if 'MoG' in filteredColumns[i]:
                    totalRows[0].append(formatSignificantDigits((totalOwnDataset[i]-totalOwnDataset[1])/totalOwnDataset[1]*100., 3))
                    totalRows[1].append(formatSignificantDigits((totalCdNet[i]-totalCdNet[1])/totalCdNet[1]*100., 3))
                elif 'SubSENSE' in filteredColumns[i]:
                    totalRows[0].append(formatSignificantDigits((totalOwnDataset[i]-totalOwnDataset[2])/totalOwnDataset[2]*100., 3))
                    totalRows[1].append(formatSignificantDigits((totalCdNet[i]-totalCdNet[2])/totalCdNet[2]*100., 3))

            outputLaTeX.write(';'.join(totalRows[0]) + '\n')
            outputLaTeX.write(';'.join(totalRows[1]) + '\n')

def convertCommaInFile(file):
    newFileName = file.replace('.csv', '-a.csv')
    newF = open(newFileName, 'w')#, newline='')

    with open(file, 'r') as f:
        for line in f:
            newLine = line.replace('.',',')
            newF.write(newLine)

def toTex(file):
    newFileName = file.replace('.csv', '.tex')
    newF = open(newFileName, 'w')#, newline='')
    lineNumber = 0

    with open(file, 'r') as f:
        for line in f:
    
            newLine = line.replace(';','&')
            newLine = newLine.replace('\n', '\\\\\n')
            newLine = newLine.replace('baselineRGB', 'Original')
            newLine = newLine.replace('GargNayar-Median-BG','Median')
            newLine = newLine.replace('Kang2012-BG','Kang2012 \cite{kang2012automatic}')
            newLine = newLine.replace('GargNayar-STCorr-BG','Garg2007 \cite{garg2007vision}')
            newLine = newLine.replace('Kim2015-blur-BG','Kim2015 \cite{kim2015video}')
            newLine = newLine.replace('IDCGAN-BG','Zhang2017 \cite{Zhang2017ImageDeraining}')
            newLine = newLine.replace('Fu2017-BG', 'Fu2017 \cite{Fu2017RemovingRF}')

            if lineNumber > 1:
                # We are moving to the actual numbers of the table
                columns = newLine.split('&')
                
                highestMoGValue = -100;
                highestMoGIndex = -1
                highestSuBValue = -100;
                highestSuBIndex = -1

                for i in range(3, len(columns)):
                    strippedColumn = columns[i].replace('\\','').replace('\n','')
                    
                    if i % 2 == 0:
                        if float(strippedColumn) > highestSuBValue:
                            highestSuBIndex = i
                            highestSuBValue = float(strippedColumn)    
                    else:
                        if float(strippedColumn) > highestMoGValue:
                            highestMoGIndex = i
                            highestMoGValue = float(strippedColumn)

                if highestMoGIndex != -1:
                    partitioned = columns[highestMoGIndex].partition('\\')

                    columns[highestMoGIndex] = '\\textbf{' + partitioned[0] + '}' + ''.join(partitioned[1:])

                if highestSuBIndex != -1:
                    partitioned = columns[highestSuBIndex].partition('\\')

                    columns[highestSuBIndex] = '\\textbf{' + partitioned[0] + '}' + ''.join(partitioned[1:])
                    newLine = '&'.join(columns)
            

            newF.write(newLine)

            lineNumber += 1

            #columnNumber = 0
            
            #columns = newLine.split('&')
            #compactLine = []
            #concatenatedColumns = ''
            
            #for column in columns:
            #    if columnNumber % 2 == 1:
            #        concatenatedColumns = column
            #    else: 
            #        if concatenatedColumns is '':
            #            concatenatedColumns += column
            #        else:
            #            concatenatedColumns += ', ' + column
            #        compactLine.append(concatenatedColumns)
            #    columnNumber += 1

            #if lineNumber == 0:
            #    newF.write(newLine.replace('\n', ' \\hline\n'))
            #else:
            #    newF.write('&'.join(compactLine))


            
            
evaluateProcentualDifferenceSceneAverage('statsPerSite.csv', 'statsPerSite-parsed.csv', 'f-measure')
toTex('statsPerSite-parsed-percentages.csv')

#rawFile = 'f-measure-all.csv'
#filteredFile = 'f-measure-all-filtered.csv'

#evaluateProcentualDifference(rawFile, filteredFile)
#convertCommaInFile(filteredFile)
#toTex(filteredFile)
