//===========================
//====>  MTestGpu
//===========================
#include "MMacros.h"
using namespace std;
using namespace cv;

#ifndef _MTESTGPU_HPP_
#define _MTESTGPU_HPP_

namespace MTestGpu {
	void printGpuNumber() {
		cout << "Cuda Enabled Gpu number = " << gpu::getCudaEnabledDeviceCount() << endl;
	}

	void testGpuAdd() {
		Mat I1 = Mat::zeros(250, 310, CV_8UC3);
		Mat I2 = Mat::zeros(250, 310, CV_8UC3);
		circle(I1, Point(60, 60), 50, Scalar(0, 0, 255));
		rectangle(I2, Rect(100,100,100,100), Scalar(0, 255));
		gpu::GpuMat gI1(I1);
		gpu::GpuMat gI2(I2);
		gpu::GpuMat gIAdd;
		gpu::add(gI1, gI2, gIAdd);
		Mat IAdd;  gIAdd.download(IAdd);
		Mat IReport = IAdd.clone();
		IReport.push_back(I1);
		IReport.push_back(I2);
		IReport = IReport.t();
		imshow("test", IReport);
		waitKey(2000);

	}

}
#endif
