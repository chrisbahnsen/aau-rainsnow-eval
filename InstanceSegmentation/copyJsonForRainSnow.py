import json
import os
import copy

from Evaluate import cocoTools

sourceJsonPath = './rainSnowGt.json'
destDir = ''

with open('./splitSequenceTranslator.json') as f:
    splitSequenceTranslator = json.load(f)

# List rain removal methods here
methods = ['baseline',
           'Fu2017',
           'GargNayar/Median',
           'GargNayar/STCorr',
           'IDCGAN',
           'Kang2012',
           'Kim2015-blur']

with open(sourceJsonPath, 'r') as f:
    sourceGt = json.load(f)

for method in methods:
    methodGt = copy.deepcopy(sourceGt)

    removedImageIds = dict()

    if 'images' in methodGt:
        images = []
        imageList = methodGt['images']

        for image in imageList:
            methodImage = image

            imageNumber = image['file_name'].split('-')[-1]

            number = int(imageNumber.replace('.png',''))
            
            if number >= 40 and number <= 5990:
                scene = image['file_name'].split('/')[0]
                sequence = image['file_name'].split('/')[1]

                if 'baseline' not in method:
                    newMethodPath = os.path.join(destDir, 
                                                scene, 
                                                sequence, 
                                                method,
                                                imageNumber)
                    methodImage['file_name'] = newMethodPath
                images.append(methodImage)
            else:
                removedImageIds[image['id']] = image['id'] # Does't really matter what the entry is, only interested in key

        if 'annotations' in methodGt:
            annotations = []

            for annotation in methodGt['annotations']:
                if annotation['image_id'] not in removedImageIds:
                    annotations.append(annotation)
                else:
                    print("Removed annotation " + str(annotation['id']) + ' for image ' + str(annotation['image_id']))
                
        methodGt['images'] = images
        methodGt['annotations'] = annotations

        # Also make sure to remove the annotations at the removed image ID's

        outputPath = os.path.join(destDir, method.replace('/', '-') + '.json')

        with open(os.path.join(destDir, method.replace('/', '-') + '.json'), 'w') as f:
            json.dump(methodGt, f)

        cocoTools.removeInstancesInsideDontCare('P:/Private/Traffic safety/Data/RainSnow/PixelLevelAnnotationsOriginal',
                                                outputPath, 
                                                splitSequenceTranslator, 
                                                destDir)


