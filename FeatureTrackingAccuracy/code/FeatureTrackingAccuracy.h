#ifndef FEATURETRACKINGACCURACY_H
#define FEATURETRACKINGACCURACY_H

#include <fstream>
#include <iomanip>
#include <list>
#include <memory>
#include <sstream>
#include <string>
#include <opencv2\opencv.hpp>

#include "AccuracyMeasurer.h"

struct AccuracyMeasurement {
    std::shared_ptr<AccuracyMeasurer> measurer;
    long startFrame;
};

struct TemporalFeatureStatistics {
    float maxPixelError;
    long featureCount;
    long startFrame;
};

class FeatureTrackingAccuracy
{
public:
    FeatureTrackingAccuracy(const std::string& framesPath, const std::string& statFilePath, 
        const std::string& temporalFileDir, const int trackerInterval, 
        const int trackingDuration);

    void measureTrackingAccuracy();
    void save();

    void setExtension();
    void readTemporalFile();


private:
    const std::string toFrameNumber(const uint idx) const;
    const std::string binaryFrame(const long idx) const;


    std::list<AccuracyMeasurement> runningMeasurements;

    std::vector<TemporalFeatureStatistics> temporalStats;
    std::vector<FeatureStatistics> aggregatedStats;

    std::string framesPath;
    std::string statFilesPath;
    std::string temporalFileDir;
    std::string binaryExtension;

    cv::Range range;

    int trackerInterval;
    int trackingDuration;
};


#endif