---
High-throughput multi-target fly tracer and sleep analyser
---

** features **
	
	1. introduction:
		
		

	2. Pipeline:
	
		   video format convertion
			     v
		tracking of animal coordinates
			     v
		   raw analysis of sleep
			     v
		data cleaning and post-analysis


---
information of files and directories in this project
---

**integrated sleep program**

	[Dependencies]
		cv2.pyd, numpy, matplotlib;
		opencv_core2413.lib, opencv_highgui2413.lib, opencv_imgproc2413.lib, opencv_ffmpeg2413_x64.lib
	[Content]
		including fly tracer binary programs, configuration tools
		main entry: launch.py
		based on Python-2.7, which gather all programs in pipeline togather
		
**autodetect**

	[Dependencies]
    		opencv_core2413.lib, opencv_highgui2413.lib, opencv_imgproc2413.lib, opencv_ffmpeg2413_x64.lib
	[Content]
    		<autodetect> pretrained ANN parameters, involving in semi-auto detection of tubes containing traced flies.
    		<autodetect/glasstubes - pixels> Scripts that build model network and create dataset during model training.
		
**SingleTracer_v4.0**

	[Dependencies]
    		opencv_core2413.lib, opencv_highgui2413.lib, opencv_imgproc2413.lib, opencv_ffmpeg2413_x64.lib
	[Content]
		OpenCV-based multi-thread tracer of fly activities.
		v4.0 is the previous stable version, which is reserved here as a backup.
		
**MSleepSummariser_20160616**

	[Dependencies]
		numpy, matplotlib, pandas, tkinter
	[Content]
		python GUI that summarizes the sleep analysis of a tracing result.
		
**other scripts *.py**

	[Dependencies]
		numpy, matplotlib, cv2.pyd
	[Content]
		> checkDataValid_0909.py: check common bugs hidden in configure or old data - an experience-based debug script.
		> cleanSleepEpisode_0910.py: convert raw sleep episode data into filered summarized data table.
		> clearDavCvt_181018.py: clear dav files that is converted into avi, while email report at specific time interval.
		> compareEpisodes.py && compareSleepLevel.py: calculating differences of sleep episodes and level between two groups.
		> configDeath_1020.py: interactive configuration GUI that filters dead flies and defines time interval to be calculated.
		> configOrder_1020.py: index every fly to its corresponding group, which is further used in statitical comparison task.
		> configTime_1020.py: set the offset time to nearest CT-0, and output a series of time schedule used in a tracing task. 
		> exportActogramSpeed_180604.py: downsampling speed data of tracing, which then could be used in circadian analysis.
		> gatherAllDav.py and grouping.py: path utilities to recursively enumerate and collect all dav files in one path.
		> plotLights.py: based on output from instance defined in MLightMonitor.hpp, it will draw the light condition schedule.
		> readEegEvent_190116.py: input EEG sleep event table, output curves of sleep events, including REM, NREM, and WAKE.
		> speed2wake_181226.py: input tracing speed data, output curve of waking number in every 30min interval
		> statSurvival_180505.py: statistical analyses of survival rate in a starvation resistance or lifspan assay.
		> tracePlayer_v0730.exe && tracePlayer-queue_v0801.exe: replay of tracing coordinates generated from singleFlyTracer, which directly show replay in a window or output a series of labeled images for specified time range, correspondingly.
		
  
---
Other notes 
---
	白色胶条：5孔（含边界）=44mm
