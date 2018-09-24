
#include "AccuracyMeasurer.h"

using namespace std;
using namespace cv;

AccuracyMeasurer::AccuracyMeasurer(std::vector<float>& maxTrackingError, int oneWayFramesToProcess)
{
    for (auto i = 0; i < maxTrackingError.size(); ++i)
    {
        FeatureStatistics stat;
        stat.maxPixelError = maxTrackingError[i];
        stat.featureCount = -1;

        stats.push_back(stat);
    }

    retrievedFrameCount = 0;

    // Resize the retrievedFrames vector to accommodate the future image frames
    retrievedFrames.resize(oneWayFramesToProcess);

    areComputationsFinished = false;

    std::vector<cv::Point2f> tmpCorners1, tmpCorners2;
    corners.push_back(tmpCorners1);
    corners.push_back(tmpCorners2);
}

bool AccuracyMeasurer::acceptsFrames()
{
    if (retrievedFrameCount < retrievedFrames.size())
    {
        return true;
    }
    else {
        return false;
    }
}

bool AccuracyMeasurer::isFinished()
{
    return areComputationsFinished;
}

void AccuracyMeasurer::processFrame(cv::Mat nextFrame)
{
    if (areComputationsFinished)
    {
        return;
    }
    
    Mat inputFrame;
    cvtColor(nextFrame, inputFrame, CV_BGR2GRAY);

    if (retrievedFrameCount >= retrievedFrames.size())
    {
        // We have retrieved all the frames that we need for processing.
        // Now, investigate the features as we go backwards through the 
        // retrieved images
        
        goBackwards();
        computeForwardBackwardTrackingError();
        
        areComputationsFinished = true;
        return;
    }



    retrievedFrames[retrievedFrameCount] = inputFrame.clone();

    if (retrievedFrameCount == 0)
    {
        // This is the first frame. Initialise the tracking features
        goodFeaturesToTrack(inputFrame, corners[0], 200, 0.01, 10, cv::Mat(),
            3, false);
        
        initialCorners = corners[0];

        retrievedFrameCount++;
        return;
    }

    // The number of retrieved frames is above 0. Calculate the new position of the features
    Mat prevFrame = retrievedFrames[retrievedFrameCount - 1];
    Mat currentFrame = retrievedFrames[retrievedFrameCount];

    trackFeatures(prevFrame, currentFrame);

    retrievedFrameCount++;
}





std::vector<FeatureStatistics> AccuracyMeasurer::getFeatureStatistics()
{
    return stats;
}

void AccuracyMeasurer::trackFeatures(cv::Mat prevFrame, cv::Mat currentFrame)
{
    vector<uchar> status;
    vector<float> error;

    calcOpticalFlowPyrLK(prevFrame, currentFrame, corners[0], corners[1],
        status, error, Size(31, 31), 3);

    //Mat displayImage = currentFrame.clone();


    // Perform house-holding on the new corners. 
    for (auto i = 0; i < corners[1].size(); i++)
    {
        if (!status[i])
        {
            // The corresponding corner was not found, or the previous 
            // corner was not found.Set the corner to an invalid position
            corners[1][i] = Point2f(-100, -100);
            continue;
        }

        //circle(displayImage, corners[1][i], 3, Scalar(0, 255, 0), -1, 8);
    }

    // Swap the new and old corners
    std::swap(corners[1], corners[0]);

    /*imshow("LK Demo", displayImage);
    //*/waitKey(1);
}

void AccuracyMeasurer::goBackwards()
{
    // Perform the tracking from the end frame to the start frame. 
    // In perfect tracking scenarios, the tracked points should go exactly to their 
    // original positions

    for (auto i = retrievedFrames.size() - 2; i > 0; --i)
    {
        trackFeatures(retrievedFrames[i + 1], retrievedFrames[i]);
    }
}

void AccuracyMeasurer::computeForwardBackwardTrackingError()
{
    if (initialCorners.size() != corners[0].size())
    {
        return;
    }

    // The dimensions of the vectors are alright.
    // Initialise the statistics

    for (auto i = 0; i < stats.size(); ++i)
    {
        stats[i].featureCount = 0;
    }

    // Measure the tracking error for each of the tracked features
    for (auto i = 0; i < initialCorners.size(); ++i)
    {
        if ((corners[0][i].x >= 0) && corners[0][i].y)
        {
            // The corner has been successfully detected
            // Compute the tracking error in pixels

            float trackingError = cv::norm(initialCorners[i] -
                corners[0][i]);

            for (auto j = 0; j < stats.size(); ++j)
            {
                if (trackingError <= stats[j].maxPixelError)
                {
                    // The tracking error of point i is below 
                    // the allowed threshold. Increment the counter
                    stats[j].featureCount++;
                }
            }
        }
    }
}
