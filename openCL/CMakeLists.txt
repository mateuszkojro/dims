cmake_minimum_required(VERSION 3.15)
project(openCL CXX)

set(CMAKE_CXX_STANDARD 17)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBAV REQUIRED IMPORTED_TARGET
        OpenCL
        )


add_executable(openCL
        #main.c
        main.cpp
        OpenclProgram.cpp OpenclProgram.h)


target_link_libraries(${PROJECT_NAME}
        PkgConfig::LIBAV
        )
