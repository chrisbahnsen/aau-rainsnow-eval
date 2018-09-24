import json
import os
from pycocotools import coco
import numpy as np
import cv2

def generateSplitSequenceTranslator(inputJson, translatorFile):
    jsonFile = None
    splitSequenceTranslator = dict()
    
    with open(inputJson, 'r') as f:
        jsonFile = json.load(f)

    if jsonFile:
        interval = 100
        sequences = range(0, 2200, interval)    

        for sequenceStart in sequences:
             if isinstance(jsonFile, dict): # GT 
                segmentJson = dict()
                
                if 'images' in jsonFile:
                    segImages = []

                    for image in jsonFile['images']:
                        splitSequenceTranslator[int(image['id'])] = image['file_name'].split('/')[0:2]

    with open(translatorFile, 'w') as f:
        json.dump(splitSequenceTranslator, f)

def constrainImageRange(inputJson):

    
    with open(inputJson, 'r') as f:
        method = json.load(f)
    
    excludedImageIds = {200, 300, 301, 324, 400, 401, 698, 699, 799, 1197, 1198, 1598, 1599, 1798, 1799, 1898, 2098, 2197}
    results = []

    for result in method:
        number = int(result['image_id'])
        
        if number not in excludedImageIds:
            results.append(result)

    with open(inputJson.replace('.json', '-imgRange.json'), 'w') as f:
        json.dump(results, f)



def removeIgnoredCategories(inputJson, ignoreFile):
    ignoredClassLabels = dict()

    with open(inputJson, 'r') as f:
        cocoJson = json.load(f)

    with open(ignoreFile) as f:
        for line in f:
            entries = line.split(';')

            if len(entries) >= 2:
                ignoredClassLabels[int(entries[0])] = entries[1].replace('\n', '')

    if isinstance(cocoJson, list): # Results
        filteredJson = []

        for result in cocoJson:
            if 'category_id' in result:
                if result['category_id'] not in ignoredClassLabels:
                    filteredJson.append(result)
                else:
                    print('Ignored category id ' + str(results['category_id']) + ", " + ignoredClassLabels[results['category_id'] ])

        if filteredJson:
            with open(inputJson.replace('.json', '-ignore.json'), 'w') as f:
                json.dump(filteredJson, f)



def splitJsonSequences(inputJson, outputFolder):
    interval = 100
    sequences = range(0, 2200, interval)

    cocoJson = None

    with open(inputJson, 'r') as jsonFile:
        cocoJson = json.load(jsonFile)

    baseName = os.path.basename(inputJson)

    if cocoJson:
        for sequenceStart in sequences:
            segmentJson = None

            if isinstance(cocoJson, dict): # GT 
                segmentJson = dict()

                if 'info' in cocoJson:
                    segmentJson['info'] = cocoJson['info']

                if 'licenses' in cocoJson:
                    segmentJson['licenses'] = cocoJson['licenses']
                
                if 'images' in cocoJson:
                    segImages = []

                    for image in cocoJson['images']:
                        if (image['id'] >= sequenceStart 
                            and image['id'] < sequenceStart + interval):
                            segImages.append(image)
                    segmentJson['images'] = segImages

                if 'annotations' in cocoJson:
                    segAnnotations = []

                    for annotation in cocoJson['annotations']:
                        if (annotation['image_id'] >= sequenceStart 
                            and annotation['image_id'] < sequenceStart + interval):
                            segAnnotations.append(annotation)
                    segmentJson['annotations'] = segAnnotations
            elif isinstance(cocoJson, list): # Results
                segmentJson = []

                for result in cocoJson:
                    if 'image_id' in result:
                        if (result['image_id'] >= sequenceStart 
                            and result['image_id'] < sequenceStart + interval):
                            segmentJson.append(result)

            if segmentJson:
                with open(os.path.join(outputFolder, 
                                       baseName.replace('.json', '-' + 
                                       str(sequenceStart) + '.json')), 'w') as f:
                    json.dump(segmentJson, f)

def removeInstancesInsideDontCare(annotationsPath, inputJson, splitSequenceTranslator, outputFolder):
    with open(inputJson, 'r') as jsonFile:
        print('Opening ' + inputJson)
        cocoJson = json.load(jsonFile)

    baseName = os.path.basename(inputJson)
    dontCareJson = None

    dontCareMasks = dict()

    for key, sceneSequence in splitSequenceTranslator.items():
        sceneSequencePath = '/'.join(sceneSequence)
        if sceneSequencePath not in dontCareMasks:
            maskPath = os.path.join(annotationsPath, sceneSequence[0], 
                                    sceneSequence[1] + '-mask.png')
            dontCareMask = cv2.imread(maskPath, cv2.IMREAD_GRAYSCALE)
            dontCareMasks[sceneSequencePath] = dontCareMask

    if isinstance(cocoJson, dict): # GT 
        COCO = coco.COCO(inputJson)
        dontCareJson = cocoJson
        images = cocoJson['images']

        if 'annotations' in cocoJson:
            dontCareAnnotations = []

            for annotation in cocoJson['annotations']:                
                if len(annotation['segmentation']) > 0:
                    segMask = COCO.annToMask(annotation)
                    imageId = str(annotation['image_id'])
                    sceneSequencePath = '/'.join(splitSequenceTranslator[imageId])
                    dontCareMask = dontCareMasks[sceneSequencePath]

                    if not maskInsideMask(segMask, dontCareMask): 
                        dontCareAnnotations.append(annotation)

            dontCareJson['annotations'] = dontCareAnnotations
            
    elif isinstance(cocoJson, list): # Detections
        dontCareJson = []

        for detection in cocoJson:
            # Convert Runlength encoded mask (RLE) into OpenCV-compatible
            # mask    
            decodedMask = mask.decode(detection['segmentation'])
            imageId = str(detection['image_id'])
            sceneSequencePath = '/'.join(splitSequenceTranslator[imageId])
            dontCareMask = dontCareMasks[sceneSequencePath]

            # Check if detection mask overlay with the 'care'-section of the 
            # don't care mask. If so, copy the mask
            if not maskInsideMask(decodedMask, dontCareMask): 
                dontCareJson.append(detection)

    baseName = os.path.basename(inputJson)
    outputFile = os.path.join(outputFolder, baseName.replace('.json', '-dontCare.json'))

    if dontCareJson is not None:
        with open(outputFile, 'w')  as jsonFile:
            json.dump(dontCareJson, jsonFile)
                        
def bboxInsideMask(xULC, yULC, xLRC, yLRC, mask):
    bboxMask = np.zeros(mask.shape, dtype="uint8")
    cv2.rectangle(bboxMask, (int(xULC+0.5), int(yULC+0.5)), 
                 (int(xLRC + 0.5), int(yLRC + 0.5)), (255, 255, 255), -1)

    return maskInsideMask(mask, bboxMask)


def maskInsideMask(inputMask, dontCareMask):
    
    # 255-valued pixels in the don't care mask are indications of the 
    # area that we actually care about.
    # 0-valued pixels, on the other hand, indicate don't care pixels
    absDiff = float(np.multiply(inputMask, dontCareMask).sum() / 255)

    inputMaskPixels = float(inputMask.sum())
    percentageInsideCareZone = 0
    if inputMaskPixels > 0:
        percentageInsideCareZone = (absDiff) / inputMaskPixels * 100.
    #print(str(absDiff) + ' - ' + str(inputMaskPixels) + ' - ' + str(percentageInsideCareZone))


    if absDiff > 0 and percentageInsideCareZone > 50:
        # If the bounding box is partially inside the care-mask, (more than 50 %)
        # 
        return False
    else:
        # cv2.imshow("bbox", bboxMask)
        # cv2.imshow("don't care", mask)
        # cv2.waitKey(0)
        return True


#resultsFile = '/home/chris/shared/PixelLevelAnnotations/annotations.json'
resultsFile = '/home/chris/shared/PixelLevelAnnotations/Results/test/aaurainsnow/generalized_rcnn/segmentations_aaurainsnow_results.json'
# Dont care mask depends on the sequence
#dontCareMask = cv2.imread()

#removeIgnoredCategories(resultsFile, './Evaluate/detectionsIgnoreList.csv')
#splitJsonSequences(resultsFile.replace('.json','-ignore.json'), '/home/chris/shared/PixelLevelAnnotations/Results/split')
#generateSplitSequenceTranslator('/home/chris/shared/PixelLevelAnnotations/annotations.json', 'splitSequenceTranslator.json')