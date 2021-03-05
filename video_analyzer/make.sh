if [ ! -d "./build" ] 
then
      mkdir build
fi
BUILD=$(pwd)/build
cd $BUILD
cmake -G "CodeBlocks - Unix Makefiles" -DAV_BUILD_EXAMPLES=0 .. 
make -j8 && ./video_analyzer

