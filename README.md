# Collection of scripts and programs for DIMS project

## How to run?

Every subproject has an `run.sh` and optionaly `test.sh` scripts making it easy

## Dependencies

### C++

_Always_

1. CMAKE
1. make
1. some recent c++ compiler

_For running OpenCL_

1. OpenCL headers

_For running video_analyzer_

1. FFmpeg >= 2.0

_with following versions of FFMpeg libs_

- libavformat >= 54.x.x
- libavcodec >= 54.x.x
- libavfilter >= 3.x.x
- libavutil >= 51.x.x
- libswscale >= 2.x.x
- libswresample >= 0.x.x
- libpostproc >= 52.x.x

### Python

_Normal_

1. Python3
1. Numpy
1. Matplotlib
1. Jupyter Notebook

_Testing_

1. pytest
1. pylint
