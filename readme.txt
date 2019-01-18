<Project> High-throughput multi-target fly tracer and sleep analyser:
  <integrated sleep program>
    [Dependencies]
      cv2.pyd, numpy, matplotlib;
      opencv_core2413.lib, opencv_highgui2413.lib, opencv_imgproc2413.lib, opencv_ffmpeg2413_x64.lib
    [Content]
      including fly tracer binary programs, configuration tools
      main entry: launch.py
      based on Python-2.7, which gather all programs in pipeline togather
  <autodetect>
    [Dependencies]
      opencv_core2413.lib, opencv_highgui2413.lib, opencv_imgproc2413.lib, opencv_ffmpeg2413_x64.lib
    [Content]
      <autodetect> pretrained ANN parameters, involving in semi-auto detection of tubes containing traced flies.
      <autodetect/glasstubes - pixels> Scripts that build model network and create dataset during model training.
  

Other notes:
白色胶条：5孔（含边界）=44mm
