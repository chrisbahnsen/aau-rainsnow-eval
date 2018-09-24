# MIT License
# 
# Copyright(c) 2016 Aalborg University
# Chris H. Bahnsen, November 2016
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


#!/usr/bin/python
# -*- coding: utf-8 -*-

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Nil Goyette
# University of Sherbrooke
# Sherbrooke, Quebec, Canada. April 2012

import os
import shutil
import subprocess
import sys

call = subprocess.call

def main():    
    datasetPath = sys.argv[1]
    binaryRootPath = sys.argv[2]
    
    if not isValidRootFolder(datasetPath):
        print('The folder ' + datasetPath + ' is not a valid root folder.');
        return
    
    processFolder(datasetPath, binaryRootPath)

def processFolder(datasetPath, binaryRootPath):
    """Call your executable for all sequences in all categories."""

    trackingDurations = ["120", "240"]

    for category in getDirectories(datasetPath):
        categoryPath = os.path.join(datasetPath, category)
                
        statFilePath = os.path.join(categoryPath, 'featureStats.txt')
        deleteIfExists(statFilePath)
        statFilePath = os.path.join(categoryPath, 'detailedFeatureStats.txt')
        deleteIfExists(statFilePath)

        if isValidVideoFolder(categoryPath):

            for video in getDirectories(categoryPath):
            
                if video != "groundtruth":
                    framesPath = os.path.join(binaryRootPath, category, video)
                    if isValidFrameFolder(framesPath):
                        computeFeatureTrackingAccuracy(categoryPath, framesPath, trackingDurations)

                    # Check if any subfolders of this folder contains valid frames
                    for subFolder in getDirectories(framesPath):
                        if subFolder != "groundtruth" and subFolder != 'MoG' and subFolder != 'SubSENSE': 
                            
                            subFolderFramesPath = os.path.join(framesPath, subFolder)
                            if isValidFrameFolder(subFolderFramesPath):
                                computeFeatureTrackingAccuracy(categoryPath, subFolderFramesPath, trackingDurations)

                        
def computeFeatureTrackingAccuracy(categoryDir, framesPath, trackingDurations):
    """Compare your binaries with the groundtruth and return the confusion matrix"""

    if not categoryDir.endswith('/'):
        categoryDir += '/'
        
    if not framesPath.endswith('/'):
        framesPath += '/'
    
    for duration in trackingDurations:
        retcode = call([os.path.join('..', 'x64', 'Release', 'FeatureTrackingAccuracy.exe'),
                        framesPath, categoryDir, categoryDir, '30', duration],
                       shell=True)
    
    return


def isValidRootFolder(path):
    """A valid root folder must have the six categories"""
    categories = set(['dynamicBackground', 'baseline', 'cameraJitter', 'intermittentObjectMotion', 'shadow', 'thermal', 'badWeather', 'lowFramerate', 'nightVideos', 'PTZ', 'turbulence'])
    folders = set(getDirectories(path))
    return 1

def isValidVideoFolder(path):
    """A valid video folder must have \\groundtruth, \\input, ROI.bmp, temporalROI.txt"""
    
    # Second check for folders with RGB / thermal
    isValid = os.path.exists(os.path.join(path, 'groundtruth')) and os.path.exists(os.path.join(path, 'input')) and os.path.exists(os.path.join(path, 'ROI.bmp')) and os.path.exists(os.path.join(path, 'temporalROI.txt'))

    return isValid

def isValidFrameFolder(path):
    """A valid results folder must NOT contain \\MoG, \\SubSENSE"""
    isValid = os.path.exists(os.path.join(path, 'MoG')) and os.path.exists(os.path.join(path, 'SubSENSE'))

    return not isValid


def getDirectories(path):
    """Return a list of directories name on the specifed path"""
    return [file for file in os.listdir(path)
            if os.path.isdir(os.path.join(path, file))]

def deleteIfExists(path):
    if os.path.exists(path):
        os.remove(path)


if __name__ == "__main__":
    main()
