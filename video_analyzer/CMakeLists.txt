cmake_minimum_required(VERSION 3.15)
project(video_analyzer LANGUAGES CXX VERSION 0.0.1)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED yes)

#add_custom_target(video_analyzer main.cc)


find_package(PkgConfig REQUIRED)
pkg_check_modules(
  LIBAV REQUIRED IMPORTED_TARGET
  libavformat
  libavcodec
  libavutil
  libavdevice
)

set(
  TARGETS
  video_analyzer
)
set(${AV_BUILD_EXAMPLES} BOOL 0)

add_subdirectory(./lib/avcpp/)
add_subdirectory(./lib/debug_cpp/)
include_directories(./lib/debug_cpp/)
add_subdirectory(./lib/eigen/)


add_executable(video_analyzer main.cc FrameReader.cpp FrameReader.h)

foreach(target ${TARGETS})

  target_link_libraries(
    ${target}
    avcpp::avcpp
  )
  target_link_libraries(
    ${target}
    debug_cpp
  )
  target_link_libraries(
    ${target}
    eigen
  )

endforeach()
