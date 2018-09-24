## Feature Tracking Accuracy
This folder and its subfolders contains all the code for running tests on the forward-backward feature tracking accuracy. All the methods are contained inside the Visual Studio sln-file, but you can use the IDE/editor of your choice.

The main workhorses are the C++ files located in the 'code' folder:
- AccuracyMeasurer.cpp: Measures the forward-backward tracking accuracy of the frames provided by the method 'processFrame'. The class is called by the method 'FeatureTrackingAccuracy'
- FeatureTrackingAccuracy.cpp: Handles the input images and deploys a new AccuracyMeasurer class for every n'th frame. It keeps track of the progress of the AccuracyMeasurers and saves the computed feature tracking accuracy in csv-files. 
-- Videos must first be converted to a series of images that follows the naming convention: '00005.png', '00100.png'. FFMPEG script: ffmpeg -i file.mpg -r 1/1 %05d.png. 
-- The temporal region of interest, i.e. the start and end positions of the frames to process, should be set in a 'temporalROI.txt' file. If one wants to process frame 40 to frame 5990, the file should contain one line: '40 5990'
- main.cpp: The entry point of the application. We use this file to provide command-line options to the FeatureTrackingAccuracy class

The file 'main.cpp' should be compiled. Requirements are C++11 and OpenCV 3.x. or greater. The final executable is called from the python scripts 'processFeatureTrackingOwnDataset.py' and 'processFeatureTrackingCDNet.py':
- processFeatureTrackingOwnDataset.py: Called from the command line with two arguments: The root folder of the dataset and the path to the executable that is compiled from main.cpp. If you use the script on the AAU RainSnow database, the RGB and thermal videos should be extracted in the groundtruthRgb and groundtruthT folders, respectively.
- processFeatureTrackingCDNet.py: Does the same thing, except that it is designed to run on the ChangeDetection.net dataset


### Processing the results
- featureStatAggregator.py: When the processing of the feature tracking accuracy has finished, the result files may be processed by the python file 'featureStatAggregator.py'. When running the file, the 'baseFolder' argument should be pointing at the root directory of the (processed) dataset. The file will recursively go through any folders and sub folders inside the baseFolder and aggregate any output from the C++ files. If will summarize the findings in one or more .csv-files.
- statParser.py: Operates on the output files of the 'featureStatAggregator.py' and formats the file into LaTeX tables.


