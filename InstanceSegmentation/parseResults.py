import json
import os
import cv2

import cocoTools

originalResultsDir = './Results/fcis'
parsedResultsDir = './Results/fcis-parsed/'

with open('./splitSequenceTranslator.json') as f:
    splitSequenceTranslator = json.load(f)

folders = os.listdir(originalResultsDir)

for folder in folders:
    addPathName = 'generalized_rcnn'

    folderPath = os.path.join(originalResultsDir, folder, addPathName)

    if not os.path.isdir(folderPath):
        continue

    resultFiles = os.listdir(folderPath)

    for resultFile in resultFiles:
        if ('segmentations' in resultFile and '.json' in resultFile
            and 'ignore' not in resultFile):
            # Step 1: Remove ignored categories
            cocoTools.removeIgnoredCategories(os.path.join(folderPath, resultFile),
                                              './Evaluate/detectionsIgnoreList.csv')

            # Step 2: Apply don't care masks
            cocoTools.removeInstancesInsideDontCare(os.path.join(folderPath, 
                                                    resultFile.replace('.json','-ignore.json')), 
                                                    splitSequenceTranslator, 
                                                    parsedResultsDir)

resultFiles = os.listdir(originalResultsDir)

for resultFile in resultFiles:
    if ('detections' in resultFile and '.json' in resultFile
        and 'ignore' not in resultFile):

        # Step 1: Remove ignored categories
        cocoTools.removeIgnoredCategories(os.path.join(originalResultsDir, resultFile),
                                            './Evaluate/detectionsIgnoreList.csv')

        # Step 2: Apply don't care masks
        cocoTools.removeInstancesInsideDontCare(os.path.join(originalResultsDir, 
                                                resultFile.replace('.json','-ignore.json')), 
                                                splitSequenceTranslator, 
                                                parsedResultsDir)