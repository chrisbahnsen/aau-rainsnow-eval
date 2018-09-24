
#include "FeatureTrackingAccuracy.h"

using namespace cv;
using namespace std;

bool fileExists(const string& path) {
    ifstream f(path.c_str());
    return f.is_open();
}

FeatureTrackingAccuracy::FeatureTrackingAccuracy(const string & framesPath, 
    const string & statFilePath,
    const string & temporalFileDir,
    const int trackerInterval,
    const int trackingDuration)
{
    this->framesPath = framesPath;
    this->statFilesPath = statFilePath;
    this->temporalFileDir = temporalFileDir;
    this->trackerInterval = trackerInterval;
    this->trackingDuration = trackingDuration;

    range.start = 0;
    range.end = 0;
}

void FeatureTrackingAccuracy::measureTrackingAccuracy()
{
    std::vector<float> maxTrackingError{ 1, 5 };

    for (auto error : maxTrackingError)
    { 
        FeatureStatistics stat;
        stat.maxPixelError = error;
        stat.featureCount = 0;
        aggregatedStats.push_back(stat);
    }

    


    for (auto i = range.start; i <= range.end; ++i)
    {
        cv::Mat frame = imread(binaryFrame(i));

        if (frame.empty())
        {
            continue;
        }

        if (i % trackerInterval == 0)
        {
            // Create a new tracker every trackerInterval frames
            AccuracyMeasurement newMeasurement;

            newMeasurement.measurer = make_shared<AccuracyMeasurer>(maxTrackingError, trackingDuration);
            newMeasurement.startFrame = i;

            runningMeasurements.push_back(newMeasurement);
        }

        auto it = runningMeasurements.begin();
        
        while(it != runningMeasurements.end())
        {
            it->measurer->processFrame(frame);

            if (it->measurer->isFinished())
            {
                vector<FeatureStatistics> stats = it->measurer->getFeatureStatistics();

                for (auto j = 0; j < stats.size(); ++j)
                {
                    TemporalFeatureStatistics tempStat;
                    tempStat.featureCount = stats[j].featureCount;
                    tempStat.maxPixelError = stats[j].maxPixelError;
                    tempStat.startFrame = it->startFrame;
                    temporalStats.push_back(tempStat);

                    // Update the aggregated statistics
                    if (aggregatedStats.size() > j && 
                        stats[j].maxPixelError == aggregatedStats[j].maxPixelError)
                    {
                        aggregatedStats[j].featureCount += stats[j].featureCount;
                    }
                }


                // We have finished processing this measurement. Erase it to free it from memory
                it = runningMeasurements.erase(it);
            }
            else
            {
                it++;
            }
        }

    }

}

void FeatureTrackingAccuracy::readTemporalFile() {
    const string filePath = temporalFileDir + "temporalROI.txt";
    ifstream f(filePath.c_str());
    if (f.is_open()) {
        if (f.good()) {
            string line;
            getline(f, line);

            uint from, to;
            istringstream iss(line);
            iss >> from >> to;

            range = cv::Range(from, to);
        }
        f.close();
    }
    else {
        throw string("Unable to open the file : ") + temporalFileDir + "temporalROI.txt";
    }
}

void FeatureTrackingAccuracy::save()
{
    // Get name of the current method of framesPath

    string methodName = framesPath;
    methodName =  methodName.replace(0, statFilesPath.size(), string());

    auto foundSlash = methodName.find_last_of("/");

    if (foundSlash != string::npos)
    {
        methodName.replace(foundSlash, 1, "");
    }

    // Create aggregated statistics file
    string statFile = statFilesPath + "featureStats.txt";

    cout << "Creating file " << statFile << endl;
    ofstream f(statFile.c_str(), ios::out | ios::app);
    if (f.is_open()) {
        string statText = methodName + ";" + to_string(trackingDuration) + ";";

        for (auto aggStat : aggregatedStats)
        {
			statText.append(to_string(aggStat.maxPixelError) + "; " + to_string(aggStat.featureCount) + "; ");
        }

        f << statText << endl;
        f.close();
    }
    else {
        throw string("Unable to open the file : ") + statFilesPath;
    }

    // Create detailed statistics file for every instance of an AccuracyMeasurer

    string detailedStatFile = statFilesPath + "detailedFeatureStats.txt";

    cout << "Creating file " << detailedStatFile << endl;
    ofstream dF(detailedStatFile.c_str(), ios::out | ios::app);
    if (dF.is_open()) {
        for (auto stat : temporalStats)
        {
            string statText = methodName + ";" +
				to_string(trackingDuration) + ";" +
                to_string(stat.startFrame) + ";" +
                to_string(stat.maxPixelError) + ";" +
                to_string(stat.featureCount) + ";";
            dF << statText << endl;
        }
        
        dF.close();
    }
    else {
        throw string("Unable to open the file : ") + statFilesPath;
    }
}

const std::string FeatureTrackingAccuracy::toFrameNumber(const uint idx) const {
    ostringstream oss;
    oss << setfill('0') << setw(5) << idx;
    return oss.str();
}

const string FeatureTrackingAccuracy::binaryFrame(const long idx) const {
    return framesPath + "" + toFrameNumber(idx) + binaryExtension;
}

void FeatureTrackingAccuracy::setExtension() {
    string extensions[] = { ".png", ".jpg", ".jpeg", ".bmp", ".ppm" };
    vector<string> exts(extensions, extensions + 5);

    const string firstBinaryFrame = binaryFrame(range.start);


    for (auto it = exts.begin(); it < exts.end(); ++it) {
        const string &ext = *it;
        if (fileExists(framesPath + "" + toFrameNumber(range.start) + ext)) {
            binaryExtension = ext;
            return;
        }
    }
    throw string("You must use png or jp[e]g extension. Reading " + firstBinaryFrame);
}