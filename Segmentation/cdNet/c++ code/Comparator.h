
#pragma once

#include <opencv2\opencv.hpp>

#include "types.h"
#include "VideoFolder.h"

class Comparator
{
	public:
		Comparator(const VideoFolder &videoFolder, string roiFile);

		void compare();
		void save() const;

	private:
		typedef BinaryFrame ROIFrame;
		typedef BinaryConstIterator ROIIterator;

		const VideoFolder &videoFolder;
		const ROIFrame ROI;

		uint tp, fp, fn, tn;
		uint nbShadowErrors;

		void compare(const BinaryFrame& binary, const GTFrame& gt);
};
