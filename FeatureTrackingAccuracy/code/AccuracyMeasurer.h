#ifndef ACCURACYMEASURER_H
#define ACCURACYMEASURER_H

#include <vector>

#include <opencv2/opencv.hpp>


struct FeatureStatistics {
    float maxPixelError;
    long featureCount;
};

class AccuracyMeasurer
{
public:
	AccuracyMeasurer(std::vector<float>& maxTrackingError, int oneWayFramesToProcess);

    bool acceptsFrames();
    bool isFinished();

    void processFrame(cv::Mat nextFrame);
    std::vector<FeatureStatistics> getFeatureStatistics();

private:
    void trackFeatures(cv::Mat prevFrame, cv::Mat currentFrame);
    void goBackwards();
    void computeForwardBackwardTrackingError();

    int retrievedFrameCount;
    bool areComputationsFinished;

    std::vector<cv::Mat> retrievedFrames;

    std::vector<FeatureStatistics> stats;

    // Corners that are currently tracked
    std::vector<std::vector<cv::Point2f>> corners;

    // Originally tracked corners
    std::vector<cv::Point2f> initialCorners;
};

#endif ACCURACYMEASURER_H