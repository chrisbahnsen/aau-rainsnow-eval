import argparse
import csv

def formatSignificantDigits(q):
    """
    Truncate a float to 2 significant figures, with exceptions for numbers below 1
    Only works for numbers [-100;100]
    Arguments:
      q : a float
    Returns:
    Float with only n s.f. and trailing zeros, but with a possible small overflow.
    """
    
    if abs(q) < 10:
        return '{: 3.2f}'.format(q)
    else:
        return '{: 3.1f}'.format(q)

def computeSceneTotals(filePath, parsedFilePath):
    
    with open(filePath) as inputStat:
        with open(parsedFilePath, 'w') as outputStat:
            
            inputcsv = csv.reader(inputStat, delimiter=';')
            firstLine = None
            sceneTotals = []
            lastScene = ''
            lastSequence = ''

            
            for row in inputcsv:
                outputRows = []


                if not firstLine:
                    firstLine = row
                    
                    outputStat.write(';'.join(row) + '\n')
                    continue
                else:               
                    currentScene = row[0]

                    if currentScene == 'cdNet-badWeather':
                        outputStat.write(';'.join(row) + '\n')
                        continue

                    if currentScene != lastScene:                        
                        # Write the totals of the last scene
                        
                        if lastScene != '':
                            outputRows.append(lastScene)
                            outputRows.append(lastSequence)

                            for total in sceneTotals:
                                outputRows.append(str(total))

                            outputStat.write(';'.join(outputRows) + '\n')

                        # Prepare for a new scene
                        if len(row) >= len(firstLine):
                            lastScene = row[0]
                            lastSequence = row[1]
                            sceneTotals = []
                            
                            for i in range(2, len(row)):
                                if row[i] != '':
                                    sceneTotals.append(float(row[i].replace('\n', '')))
                                else:
                                    sceneTotals.append(0)
                            


                    else:
                        for i in range(2, len(row)):
                            if row[i] != '':
                                sceneTotals[i-2] = sceneTotals[i-2] + (float(row[i].replace('\n', '')))

            outputRows = []
            outputRows.append(lastScene)
            outputRows.append(lastSequence)

            for total in sceneTotals:
                outputRows.append(str(total))

            outputStat.write(';'.join(outputRows) + '\n')


def evaluateProcentualDifference(filepath, parsedFilepath):
    """
    Takes in files as produced by FeatureStatAggregator ("*-all")
    and computes the percentual difference of methods as compared 
    to baseline methods
    """

    filteredColumns = ['Sequence',
                       'FramesRGB',
                       'GargNayar\Median',
                       'GargNayar\STCorr',
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


    with open(filepath) as inputStat:
        with open(parsedFilepath, 'w') as outputLaTeX:
            # Create pretty headers for the tables
            prettyHeader = []             

            for column in filteredColumns:
                if 'MoG' in column:
                    prettyHeader.append(column.replace('/MoG', ''))
                elif 'SubSENSE' in column:
                    prettyHeader.append(column.replace('/SubSENSE', ''))
                else:
                    prettyHeader.append(column)

            outputLaTeX.write(';'.join(prettyHeader) + "\n")

            inputcsv = csv.reader(inputStat, delimiter=';')
            firstLine = None
            indexList = {}
            latexRows = {}
            totalOwnDataset = ["Own dataset average"] + [0.]*(len(filteredColumns)-1)
            totalCdNet = ["badWeather average"] + [0.]*(len(filteredColumns)-1)

            for row in inputcsv:
                filteredRow = [row[0] + '/' + row[1]]

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
                            if filteredColumns[i] == 'FramesRGB': 
                                # If we are operating on the cdNet dataset, the input frames
                                # are called 'input' instead of 'FramesRGB'
                                number = float(row[indexList['input']])
                        
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
                    if 'FramesRGB' in filteredColumns[i]:
                        latexRow.append('{: .0f}'.format(filteredRow[i]))
                        continue                

                    latexRow.append(formatSignificantDigits((filteredRow[i]-filteredRow[1])/filteredRow[1]*100.))
                    
                latexRows[publishedSequenceTranslator[filteredRow[0]]] = latexRow
            
            for translatedSequence, row in sorted(latexRows.items()):
                outputLaTeX.write(';'.join(row) + '\n')
            
            # Calculate the difference totals
            totalRows = [[], []]
            
            totalRows[0].append(totalOwnDataset[0])
            totalRows[1].append(totalCdNet[0])
            totalRows[0].append('{: .0f}'.format(totalOwnDataset[1])) # Show the absolute numbers for the input frames
            totalRows[1].append('{: .0f}'.format(totalCdNet[1]))

            for i in range(2, len(totalOwnDataset)):                 
                totalRows[0].append(formatSignificantDigits((totalOwnDataset[i]-totalOwnDataset[1])/totalOwnDataset[1]*100.))
                totalRows[1].append(formatSignificantDigits((totalCdNet[i]-totalCdNet[1])/totalCdNet[1]*100.))

            outputLaTeX.write(';'.join(totalRows[0]) + '\n')
            outputLaTeX.write(';'.join(totalRows[1]) + '\n')

def combineTwoFiles(file1, file2, combinedFile, file1Str, file2Str):

    input1Rows = []
    input2Rows = []

    with open(file1) as input1:
        input1csv = csv.reader(input1, delimiter='&')

        for row in input1csv:
            input1Rows.append(row)

    with open(file2) as input2:
        input2csv = csv.reader(input2, delimiter='&')

        for row in input2csv:
            input2Rows.append(row)
    
    with open(combinedFile, 'w') as outFile:
        for i in range(0, len(input1Rows)):

            if i == 0:                
                row1Columns = input1Rows[i]
                formattedColumns = row1Columns[0:1]

                for j in range(1, len(row1Columns)-1):
                    formattedColumns.append('\multicolumn{2}{l}{' + row1Columns[j] + '}')
                formattedColumns.append('\multicolumn{2}{l}{' + row1Columns[j+1].replace('\\','') + '}\\\\')
            else:
                row1Columns = input1Rows[i]
                formattedColumns = [row1Columns[0]]
                row2Columns = input2Rows[i]

                if len(row1Columns) != len(row2Columns):
                    print("Error in row lengths, row1: " + input1Rows[i] + "\n; row2: " + input1Rows[i])
                    continue
                
                for j in range(1, len(row1Columns)):
                    formattedColumns.append(row1Columns[j].replace('\\',''))
                    formattedColumns.append(row2Columns[j])
            

            outFile.write('&'.join(formattedColumns) + '\n')


            if (i == 0):
                # Write an additional row that includes the file1Str and file2Str
                extraColumns = ['']                

                for j in range(0, (len(formattedColumns)-1)*2):
                    if j % 2 == 0:
                        extraColumns.append(file1Str)
                    else:
                        extraColumns.append(file2Str)
                outFile.write('&'.join(extraColumns) + '\\\\\\hline\n')
                    
        
def toTex(file):
    newFileName = file.replace('.csv', '.tex')
    newF = open(newFileName, 'w')#, newline='')
    lineNumber = 0

    with open(file, 'r') as f:
        for line in f:
    
            newLine = line.replace(';','&')
            newLine = newLine.replace('\n', '\\\\\n')
            newLine = newLine.replace('FramesRGB', 'Original')
            newLine = newLine.replace('GargNayar\Median','Median')
            newLine = newLine.replace('Kang2012','Kang2012 \cite{kang2012automatic}')
            newLine = newLine.replace('GargNayar\STCorr','Garg2007 \cite{garg2007vision}')
            newLine = newLine.replace('Kim2015-blur','Kim2015 \cite{kim2015video}')
            newLine = newLine.replace('IDCGAN','Zhang2017 \cite{Zhang2017ImageDeraining}')
            newLine = newLine.replace('Fu2017', 'Fu2017 \cite{Fu2017RemovingRF}')

            #if lineNumber > 1:
            #    # We are moving to the actual numbers of the table
            #    columns = newLine.split('&')
                
            #    highest1Value = -100;
            #    highest1Index = -1
            #    highest5Value = -100;
            #    highest5Index = -1

            #    for i in range(2, len(columns)):
            #        strippedColumn = columns[i].replace('\\','').replace('\n','')
                    
            #        if i % 2 == 0:
            #            if float(strippedColumn) > highest1Value:
            #                highest1Index = i
            #                highest1Value = float(strippedColumn)    
            #        else:
            #            if float(strippedColumn) > highest5Value:
            #                highest5Index = i
            #                highest5Value = float(strippedColumn)

            #    if highest1Index != -1:
            #        partitioned = columns[highest1Index].partition('\\')

            #        columns[highest1Index] = '\\textbf{' + partitioned[0] + '}' + ''.join(partitioned[1:])

            #    if highest5Index != -1:
            #        partitioned = columns[highest5Index].partition('\\')

            #        columns[highest5Index] = '\\textbf{' + partitioned[0] + '}' + ''.join(partitioned[1:])
            #        newLine = '&'.join(columns)
            

            #newF.write(newLine)

            #lineNumber += 1

            newF.write(newLine)

def highlightBestResults(file, newFile):
    newFileName = file.replace('.csv', '.tex')
    newF = open(newFile, 'w')#, newline='')
    lineNumber = 0

    with open(file, 'r') as f:
        for line in f:
    
            if lineNumber > 1:
                # We are moving to the actual numbers of the table
                columns = line.split('&')
                
                highest1Value = -100;
                highest1Index = -1
                highest5Value = -100;
                highest5Index = -1

                for i in range(3, len(columns)):
                    strippedColumn = columns[i].replace('\\','').replace('\n','')
                    
                    if i % 2 == 0:
                        if float(strippedColumn) > highest1Value:
                            highest1Index = i
                            highest1Value = float(strippedColumn)    
                    else:
                        if float(strippedColumn) > highest5Value:
                            highest5Index = i
                            highest5Value = float(strippedColumn)

                if highest1Index != -1:
                    partitioned = columns[highest1Index].partition('\\')

                    columns[highest1Index] = '\\textbf{' + partitioned[0] + '}' + ''.join(partitioned[1:])

                if highest5Index != -1:
                    partitioned = columns[highest5Index].partition('\\')

                    columns[highest5Index] = '\\textbf{' + partitioned[0] + '}' + ''.join(partitioned[1:])
                    line = '&'.join(columns)
            

            newF.write(line)

            lineNumber += 1



def convertCommaInFile(file):
    newFileName = file.replace('.csv', '-a.csv')
    newF = open(newFileName, 'w')#, newline='')

    with open(file, 'r') as f:
        for line in f:
            newLine = line.replace('.',',')
            newF.write(newLine)

rawFile = 'overview-maxPixelError-1.0-trackingDuration-240.csv'
filteredFile = 'overview-maxPixelError-1.0-trackingDuration-240-filtered.csv'
totalFile = 'overview-maxPixelError-1.0-trackingDuration-240-sequenceTotals.csv'
totalFilteredFile = 'overview-maxPixelError-1.0-trackingDuration-240-sequenceTotals-filtered.csv'

rawFile2 = 'overview-maxPixelError-5.0-trackingDuration-240.csv'
filteredFile2 = 'overview-maxPixelError-5.0-trackingDuration-240-filtered.csv'
totalFile2 = 'overview-maxPixelError-5.0-trackingDuration-240-sequenceTotals.csv'
totalFilteredFile2 = 'overview-maxPixelError-5.0-trackingDuration-240-sequenceTotals-filtered.csv'

computeSceneTotals(rawFile, totalFile)
computeSceneTotals(rawFile2, totalFile2)

evaluateProcentualDifference(rawFile, filteredFile)
evaluateProcentualDifference(rawFile2, filteredFile2)

evaluateProcentualDifference(totalFile, totalFilteredFile)
evaluateProcentualDifference(totalFile2, totalFilteredFile2)

convertCommaInFile(filteredFile)
convertCommaInFile(filteredFile2)
convertCommaInFile(totalFilteredFile)
convertCommaInFile(totalFilteredFile2)

toTex(filteredFile)
toTex(filteredFile2)
toTex(totalFilteredFile)
toTex(totalFilteredFile2)

combineTwoFiles(filteredFile.replace('.csv', '.tex'), filteredFile2.replace('.csv', '.tex'), 'overview-trackingDuration-240.tex', '1.0', '5.0')
combineTwoFiles(totalFilteredFile.replace('.csv', '.tex'), totalFilteredFile2.replace('.csv', '.tex'), 'overview-trackingDuration-240-sceneAverage.tex', '1.0', '5.0')

highlightBestResults('overview-trackingDuration-240-sceneAverage.tex', 'overviewBest-trackingDuration-240-sceneAverage.tex.tex')