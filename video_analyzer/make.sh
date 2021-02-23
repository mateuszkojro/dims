mkdir build
cd build
cmake -DAV_BUILD_EXAMPLES=0 ..
make -j8 && ./video_analyzer
