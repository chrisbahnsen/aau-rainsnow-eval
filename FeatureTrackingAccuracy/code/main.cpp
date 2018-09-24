//MIT License
//
//Copyright(c) 2016 Aalborg University
//Chris H. Bahnsen, November 2016
//
//Permission is hereby granted, free of charge, to any person obtaining a copy
//of this software and associated documentation files(the "Software"), to deal
//in the Software without restriction, including without limitation the rights
//to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
//copies of the Software, and to permit persons to whom the Software is
//furnished to do so, subject to the following conditions :
//
//The above copyright notice and this permission notice shall be included in all
//copies or substantial portions of the Software.
//
//THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
//AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//SOFTWARE.

#include <iostream>
#include <string>

#include "FeatureTrackingAccuracy.h"

using namespace std;

int main(int argc, char *argv[]) {

    if (argc < 3 || argc > 6) {
        cerr << "Usage : comparator.exe path\\to\\video\\ path\\to\\binaryFolder\\\n groundtruthFolder";
        return 0;
    }

	cout << "Computing feature tracking accuracy...";

	const string framesPath = argv[1];
	const string statFileDir = argv[2];
    const string temporalFileDir = argv[3];
    const string trackerInterval = argv[4];
    const string trackingDuration = argv[5];
	
	cout << "\n  framesPath : " << framesPath
			<< "\n  statFilePath : " << statFileDir << endl;

	bool error = false;
	FeatureTrackingAccuracy featureTrackingAccuracy(framesPath, statFileDir, temporalFileDir,
        stoi(trackerInterval), stoi(trackingDuration));
	try {
        featureTrackingAccuracy.readTemporalFile();
        featureTrackingAccuracy.setExtension();

        featureTrackingAccuracy.measureTrackingAccuracy();
        featureTrackingAccuracy.save();


	} catch (const string &s) {
		error = true;
		cout << "An exception has occurred : " << s << "\n";
	}
	
	return 0;
}
