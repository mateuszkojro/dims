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
#include "FrameReader.h"
#include "SImpleShow.h"

int pow(int x) {
    return x * x;
}

using namespace mk;


class SaveFramesPPMDifference : public FrameReader {
public:
    SaveFramesPPMDifference() : FrameReader() {};

    SimpleShow show{1920,1080};
    FrameData last_frame;

    std::string out_path_;
    size_t frame_counter = 0;

    void on_frame(FrameData &data) override {
        //TIME_START(convert_to_rgb);
        std::fstream file;
        file.open(out_path_ + std::to_string(frame_counter++) + ".ppm", std::ios::out);

        // write out format
        file << "P2" << std::endl;
        // write out dimentions of the image
        //we have here bad dimentions
        file << data.cols() << " " << data.rows() << std::endl;
        // write out color depth
        file << "255" << std::endl;

        auto copy = data.transpose();
        auto result = copy;
        for (size_t i = 0; i < data.size(); i++) {
            if (last_frame(i) <= copy(i)) {
                result(i) = copy(i) - last_frame(i);
            } else {
                result(i) = 0;
            }
        }

        float max = result.maxCoeff();
        LOG("max: " + std::to_string(max));
        LOG("size: " + std::to_string(result.size()));
        LOG("x*y: " + std::to_string(result.rows() * result.cols()));

        for (size_t i = 0; i < result.size(); i++) {
            result(i) = (uint_fast8_t) (((float) result(i) / max) * 255);
        }

        file << result;

        show.imshow(result.data(), result.cols(), result.rows());

        last_frame = copy;
    }

};

int main(int argc, char **argv) {

    // Initialize my logger library
    mk::Logger::Config config = {.show_line = false,
            .show_file = false,
            .show_func = false,
            .to_file = false,
            .timing = true};

    mk::Logger::init(mk::Logger::all, config);

    TRUE_OR_PANIC(
            argc >= 2,
            "Specify path to a file as a 1st arg and output folder as a second");

    std::string path = argv[1];
    std::string out_dir = argv[2];

    SaveFramesPPMDifference ppmDiff;

    ppmDiff.last_frame = FrameData(1920, 1080).setConstant(0);
    ppmDiff.out_path_ = out_dir;
    ppmDiff.init(path);

    TIME_START(decode);
    ppmDiff.read_packets();
    TIME_STOP(decode, "Decoding took: ");

    ppmDiff.end();

}
