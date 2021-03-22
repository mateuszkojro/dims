#include <chrono>
#include <cstddef>
#include <functional>
#include <iostream>
#include <memory>
#include <ratio>
#include <string>

#include "av.h"

// API2
#include "Logger.h"
//#include "codeccontext.h"
//
//#include <cmath>

#include "FrameReader.h"

using namespace mk;

#define SAVE_FRAMES false

// from https://en.wikipedia.org/wiki/YUV#Y%E2%80%B2UV422_to_RGB888_conversion

void yuv2rgb(uint8_t yValue, uint8_t uValue, uint8_t vValue,
             uint8_t &r, uint8_t &g, uint8_t &b) {

    // we are intentionaly loosing the fractional part becouse colors are whole values
    int rTmp = (int) yValue + (1.370705 * (vValue - 128));
    // or fast integer computing with a small approximation
    // rTmp = yValue + (351*(vValue-128))>>8;
    int gTmp = (int) yValue - (0.698001 * (vValue - 128)) - (0.337633 * (uValue - 128));
    // gTmp = yValue - (179*(vValue-128) + 86*(uValue-128))>>8;
    int bTmp = (int) yValue + (1.732446 * (uValue - 128));
    // bTmp = yValue + (443*(uValue-128))>>8;
    r = std::clamp(rTmp, 0, 255);
    g = std::clamp(gTmp, 0, 255);
    b = std::clamp(bTmp, 0, 255);
}

FrameData yuv422_to_rgb(const FrameData &input) {
    FrameData output(640 * 3, 480);

    int j = 0;

    for (size_t i = 0; i < input.size(); i += 4) {
        int u = input(i + 0);
        int y1 = input(i + 1);
        int v = input(i + 2);
        int y2 = input(i + 3);
        yuv2rgb(y1, u, v, output(j), output(j + 1), output(j + 2));
        yuv2rgb(y2, u, v, output(j + 3), output(j + 4), output(j + 5));
        j += 6;
    }


    return output;
}

/*
 for (size_t i = 0; i < input.size(); i += 4) {
        int u = input(i + 0);
        int y1 = input(i + 1);
        int v = input(i + 2);
        int y2 = input(i + 3);
        yuv2rgb(y1, u, v, output(j), output(j + 1), output(j + 2));
        yuv2rgb(y2, u, v, output(j + 3), output(j + 4), output(j + 5));
        j += 6;
    }
*/



class SaveFramesPPM : public FrameReader {

public:
    SaveFramesPPM() : FrameReader() {};

    std::string out_path_;
    size_t frame_counter = 0;

    void on_frame(FrameData &data) override {
        TIME_START(convert_to_rgb);
        std::fstream file;
        file.open(out_path_ + std::to_string(frame_counter++) + ".ppm", std::ios::out);

        // write out format
        file << "P3" << std::endl;
        // write out dimentions of the image
        //we have here bad dimentions
        file << 640 << " " << 480 << std::endl;
        // write out color depth
        file << "255" << std::endl;
        // convert YUV422 encoded pixels into RGB encoded pixels and write to file in plain text
        //file << yuv422_to_rgb(data).transpose() << std::endl;
        file << data.transpose() << std::endl;
        TIME_STOP(convert_to_rgb, "converting to rgb took: ");
    }

};

class SaveFramesBinary : public FrameReader {
public:
    SaveFramesBinary() : FrameReader() {}

    std::string out_path_;
    size_t frame_counter = 0;


    void on_frame(FrameData &data) override {
        auto file = fopen((out_path_ + std::to_string(frame_counter++) + ".bin").c_str(), "wb");
        LOG("width: " + std::to_string(current_frame_info_.width()));
        LOG("Matrix width: " + std::to_string(data.cols()));
        LOG("height: " + std::to_string(current_frame_info_.height()));
        LOG("Matrix height: " + std::to_string(data.rows()));
        LOG("size: " + std::to_string(current_frame_info_.size()));
        LOG("Matrix size: " + std::to_string(data.size()));
        fwrite(data.data(), data.size(), 1, file);
        fclose(file);
    }

};

class SaveRawVideo : public FrameReader {

    std::fstream out_file;

public:
    SaveRawVideo() : FrameReader() {
        out_file.open("out_video.bin", std::ios::out | std::ios::binary);
    }

    void on_frame(FrameData &data) override {

        auto out = yuv422_to_rgb(data).transpose().data();
        if (out_file.bad())
            ERR("File is bad");
        else
            LOG("File is good");
        out_file.write((char *) this->current_frame_info_.data(),
                       this->current_frame_info_.width() * current_frame_info_.height());
    }
};


int main(int argc, char **argv) {

    // Initialize my logger library
    mk::Logger::Config config = {.show_line = false,
            .show_file = false,
            .show_func = true,
            .to_file = false,
            .timing = true};

    mk::Logger::init(mk::Logger::all, config);

    TRUE_OR_PANIC(
            argc >= 3,
            "Specify path to a file as a 1st arg and output folder as a second");


    std::string path = argv[1];
    std::string out_dir = argv[2];

    SaveFramesPPM reader;

    reader.out_path_ = out_dir;

    reader.init(path);

    reader.read_packets();

    reader.end();

/*
    SaveRawVideo video;

    video.init(path);
    video.read_packets();
    video.end();
*/

}
