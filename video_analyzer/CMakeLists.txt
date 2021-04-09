cmake_minimum_required(VERSION 3.15)
project(video_analyzer LANGUAGES CXX VERSION 0.0.1)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED yes)

#add_custom_target(video_analyzer main.cc)

add_library(
        FrameReader STATIC
        ./lib/FrameReader/FrameReader.cpp
)

target_link_libraries(
        FrameReader
        avcpp::avcpp
        debug_cpp
        eigen
)

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
  video_analyzer ppm_frames raw_frames
)
set(${AV_BUILD_EXAMPLES} BOOL 0)

add_subdirectory(./lib/avcpp/)
add_subdirectory(./lib/debug_cpp/)
include_directories(./lib/debug_cpp/)
include_directories(./lib/FrameReader/)
add_subdirectory(./lib/eigen/)

set(CMAKE_CXX_FLAGS "-O3 -march=native")
set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS}")

add_executable(video_analyzer main.cc )
add_executable(ppm_frames split_into_ppm.cpp)
add_executable(raw_frames split_into_raw.cpp)

foreach(target ${TARGETS})

  target_link_libraries(
    ${target}
    FrameReader
  )
  target_link_libraries(
    ${target}
    debug_cpp
  )
  # Copy example avi file to out folder
  add_custom_command(
          TARGET ${target} POST_BUILD
          COMMAND ${CMAKE_COMMAND} -E copy_if_different
          "${PROJECT_SOURCE_DIR}/files/example_short.avi"
          $<TARGET_FILE_DIR:${target}>
  )

endforeach()

