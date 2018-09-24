import argparse
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

def boxPlotFromResults(csvFile, plotFileName, method1Name, method2Name):
    """
        Produces boxPlot from the parsed results file (csv or tex) 
        on all rain removal methods
    """

    filteredColumns = ['Sequence',
            'baselineRGB/' + method1Name,
            'baselineRGB/' + method2Name,
            'Median/' + method1Name,
            'Median/' + method2Name,
            'Garg2007/' + method1Name,
            'Garg2007/' + method2Name,
            'Kang2012/' + method1Name,
            'Kang2012/' + method2Name,
            'Kim2015/' + method1Name,
            'Kim2015/' + method2Name,
            'Fu2017/' + method1Name,
            'Fu2017/' + method2Name,
            'Zhang2017/' + method1Name,    
            'Zhang2017/' + method2Name]

    with open(csvFile) as inputStat:
        
        delim = ';'
        
        if '.tex' in csvFile:
            delim = '&'

        inputcsv = csv.reader(inputStat, delimiter=delim)

        resultsTable = {}

        rowNumber = -1

        for row in inputcsv:

            rowNumber += 1

            if rowNumber < 2:
                # Ignore the two first lines; they are headers
                continue

            if 'avg' in row[0] or 'average' in row[0]:
                continue
                
            
            if len(row) >= len(filteredColumns):
                # We start the range from the fourth element as we only want to 
                # have percentual difference - and baseline is reported in absolute numbers

                for i in range(3, len(filteredColumns)):

                    split = filteredColumns[i].split('/')

                    if len(split) <= 1:
                        continue
                    
                    rainRemovalMethod = split[0]
                    segmentationMethod = split[1]

                    if rainRemovalMethod not in resultsTable:
                        resultsTable[rainRemovalMethod] = {method1Name: [], method2Name: []}
                    
                    if segmentationMethod in resultsTable[rainRemovalMethod]:
                        parsedColumn = row[i].replace('\n', '').replace('\\', '')
                        resultsTable[rainRemovalMethod][segmentationMethod].append(float(parsedColumn))
                    else:
                        print("Error: " + segmentationMethod + ' not in dict')

    data = []
    overallData = []    
    xticklabels = []
    overallXTickLabels = []

    # We have effectively scraped the method data. Now, create the box plot
    lastRainRemovalMethod = None

    for i in range(3, len(filteredColumns)):

        split = filteredColumns[i].split('/')

        if len(split) <= 1:
            continue

        rainRemovalMethod = split[0]
        segmentationMethod = split[1]
        xticklabels.append(rainRemovalMethod)

        if rainRemovalMethod in resultsTable:
            data.append(resultsTable[rainRemovalMethod][segmentationMethod])

        if lastRainRemovalMethod is not None and lastRainRemovalMethod == rainRemovalMethod:
            overallData[-1] += resultsTable[rainRemovalMethod][segmentationMethod]
        else:
            overallData.append(resultsTable[rainRemovalMethod][segmentationMethod])
            overallXTickLabels.append(rainRemovalMethod)

        lastRainRemovalMethod = rainRemovalMethod

    fig, ax1 = plt.subplots(figsize=(10, 5))
    medianprops = dict(color='red')
    bp = ax1.boxplot(data, 0, '', medianprops=medianprops)
    ax1.set_xticklabels(xticklabels, rotation=45)
    plt.setp(bp['fliers'], color='red', marker='+')

    
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    medianprops2 = dict(color='red')
    bp2 = ax2.boxplot(overallData, 0, '', medianprops=medianprops2)
    ax2.set_xticklabels(overallXTickLabels, rotation=45)
    plt.setp(bp2['fliers'], color='red', marker='+')

    ax1.set_ylabel('Relative improvement to original video')
    ax1.yaxis.grid(True, linestyle='-', which='major', color='silver',
                   alpha=0.5)
    ax1.set_axisbelow(True)

    ax2.set_ylabel('Relative improvement to original video')
    ax2.yaxis.grid(True, linestyle='-', which='major', color='silver',
                   alpha=0.5)
    ax2.set_axisbelow(True)

    boxColors = ['darkkhaki', 'royalblue']
    medians = list(range(len(xticklabels)))
    for i in range(len(xticklabels)):
        box = bp['boxes'][i]
        boxX = []
        boxY = []
        for j in range(5):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
        boxCoords = np.column_stack([boxX, boxY])
        # Alternate between Dark Khaki and Royal Blue
        k = i % 2
        boxPolygon = Polygon(boxCoords, facecolor=boxColors[k])
        ax1.add_patch(boxPolygon)
        # Now draw the median lines back over what we just filled in
        med = bp['medians'][i]
        medianX = []
        medianY = []
        for j in range(2):
            medianX.append(med.get_xdata()[j])
            medianY.append(med.get_ydata()[j])
            ax1.plot(medianX, medianY, 'k')
            medians[i] = medianY[0]

    for i in range(len(overallXTickLabels)):
        box = bp2['boxes'][i]
        boxX = []
        boxY = []
        for j in range(5):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
        boxCoords = np.column_stack([boxX, boxY])
        boxPolygon = Polygon(boxCoords, facecolor=boxColors[0])
        ax2.add_patch(boxPolygon)
        # Now draw the median lines back over what we just filled in
        med = bp2['medians'][i]
        medianX = []
        medianY = []
        for j in range(2):
            medianX.append(med.get_xdata()[j])
            medianY.append(med.get_ydata()[j])

            print('Median: ' + str(medianY))

            ax2.plot(medianX, medianY, 'k')
            medians[i] = medianY[0]


    fig.text(0.15, 0.25, method1Name,
         backgroundcolor=boxColors[0], color='black', weight='roman',
         size='medium', transform=ax1.transAxes)
    fig.text(0.15, 0.19, method2Name,
         backgroundcolor=boxColors[1],
         color='white', weight='roman', size='medium', 
         transform=ax1.transAxes)

    #x1, x2, y1, y2 = plt.axis()
    #plt.axis((x1, x2, -85, y2))

    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, -85, y2))

#    plt.show()
    figName = plotFileName
    fig.savefig(figName, bbox_inches='tight')

    fig2.savefig(figName.replace('.pdf', '-overall.pdf'), bbox_inches='tight')
    
                
            
boxPlotFromResults('summarizedParsedResults-percentages.csv', 'instanceSegmentationBoxPlot.pdf', 'FB Mask R-CNN', 'MS FCIS')
boxPlotFromResults('C:/Code/rainsnoweval/Evaluate/f-measure-all-filtered.csv', 'segmentationBoxPlot.pdf' , 'MoG', 'SubSENSE')
boxPlotFromResults('C:/Code/rainsnoweval/Evaluate/overview-trackingDuration-240.tex', 'featureTrackingBoxPlot.pdf', 'Max error: 1.0 pixels', 'Max error: 5.0 pixels')

boxPlotFromResults('./Evaluate/allResultsCombined.csv', 'allResultsCombined.pdf', 'Max error: 1.0 pixels', 'Max error: 5.0 pixels')
