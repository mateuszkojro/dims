cmake_minimum_required(VERSION 3.15)
project(avi_parser)
set(CMAKE_CXX_COMPILER "g++")
set(CMAKE_CXX_STANDARD 17)

#find_package(PkgConfig REQUIRED)
#pkg_check_modules(LIBAV REQUIRED IMPORTED_TARGET
#        libavformat
#        libavcodec
#        libavutil
#        )


add_executable(avi_parser main.cpp Video.cpp Video.h Matrix.cpp Matrix.h Avi.cpp Avi.h IO.cpp IO.h)
#
#target_link_libraries(${PROJECT_NAME}
#        PkgConfig::LIBAV
#        )