cmake_minimum_required(VERSION 3.15)

project(video_analyzer LANGUAGES CXX VERSION 0.0.1)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED yes)

#add_custom_target(video_analyzer main.cc)
add_executable(video_analyzer main.cc)

set(
  TARGETS
  video_analyzer
)
set(${AV_BUILD_EXAMPLES} BOOL 0)

add_subdirectory(lib/avcpp/)

foreach(target ${TARGETS})

  target_link_libraries(
    ${target}
    avcpp::avcpp
  )

endforeach()
