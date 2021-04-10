//
// Created by mateusz on 4/10/21.
//

#include "FrameReader.h"

using namespace mk;

class ShowVideo : public FrameReader {

public:
    ShowVideo() = default;

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
        // convert YUV422 encoded pixels into RGB encoded pixels and write to file in plain text
        //file << yuv422_to_rgb(data).transpose() << std::endl;
        file << data.transpose() << std::endl;
        //TIME_STOP(convert_to_rgb, "converting to rgb took: ");
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
            argc >= 3,
            "Specify path to a file as a 1st arg and output folder as a second");

    std::string path = argv[1];
    std::string out_dir = argv[2];

    ShowVideo ppmDiff;

    ppmDiff.out_path_ = out_dir;

    ppmDiff.init(path);

    TIME_START(decode);

    ppmDiff.read_packets();

    TIME_STOP(decode, "Decoding took: ");


    ppmDiff.end();

}