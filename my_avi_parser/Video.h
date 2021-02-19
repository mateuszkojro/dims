//
// Created by mateusz on 06.02.2021.
//

#ifndef AVI_PARSER_VIDEO_H
#define AVI_PARSER_VIDEO_H

#include "Matrix.h"
struct Pixel {
    int R;
    int G;
    int B;
};
using Frame = Matrix<Pixel>;


class Video {
public:
    size_t get_n_frames();


private:
    std::vector<Frame> frames_;
};


#endif//AVI_PARSER_VIDEO_H
