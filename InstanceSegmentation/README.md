Run the instance segmentation method of choice on the AAU RainSnow dataset. We recommend using a framework that is compatible with the COCO API - this makes things a whole lot easier
We have set up Facebooks Mask R-CNN using the 'setUpDetectionDatasets.sh' and '*.yaml'-scrips. We use the provided docker image at https://github.com/facebookresearch/Detectron/tree/master/docker to run the network.


After running the instance segmentation algorithms on the AAU RainSnow dataset, run the python scripts in the following order. You might need to change some paths in the scripts such that they point to the AAU RainSnow dataset and the results of your instance segmentation algorithms

1. For every sequence, we use the first 40 frames to warm up any rain removal algorithm. Furthermore, we should not count annotations in the ground truth that are within the don't care zone indicated in the masks. In order to process these changes on the ground truth data, run the script 'copyJsonForRainSnow.py'
2. Use the script 'Evaluate/parseResults.py' to remove detections within the don't care zone and remove categories that we have chosen not to annotate, e.g. traffic lights. 
3. Use the script 'Evaluate/summarizeParsedResults.py' to evaluate the detections using the AAU RainSnow ground truth. This file is specifically tailored to format the results of MS FCIS and Facebook Mask R-CNN detectors. The script 'summarizeParsedResults-sequenceAverage.py' does the same thing but averages for all scenes in a sequence, e.g. reporting an average value for Egensevej-1-5. 
4. The script 'boxPlotFromResults.py' will deliver box plots as shown in Figure 6 in the paper 'Rain Removal in Traffic Surceillance: Does it Matter?'. The file 'allResultsCombined.csv' is just a file - with all the percentual differences from instance segmentation, feature tracking, and segmentation algorithms combined.
