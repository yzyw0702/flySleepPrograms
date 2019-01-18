// createDataset.cpp : �������̨Ӧ�ó������ڵ㡣
//

#include "stdafx.h"
#include "../../classes/MMacros.hpp"
#include "../../classes/MTrainDataset.hpp"

void createOriDataset() {
	MTrainDataset* pDs = new MTrainDataset;
	pDs->initWith(g_fSrcData);
	pDs->create(g_dirDstData, g_wImage, g_hImage);
	pDs->enhance(g_dirDstData, g_wImage, g_hImage);
}

int main(int argc, char** argv)
{
	createOriDataset();
	return 0;
}

