//
// Created by mateusz on 4/10/21.
//

#include "FrameReader.h"

using namespace mk;

class SaveFramesBinary : public FrameReader {
public:
    SaveFramesBinary() = default;

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

    SaveFramesBinary video;

    video.out_path_ = "./frames/";

    video.init(path);
    video.read_packets();
    video.end();

}