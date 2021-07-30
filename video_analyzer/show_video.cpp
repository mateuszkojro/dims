

#include "FrameReader.h"
#include "SImpleShow.h"

using namespace mk;

class ShowVideo : public FrameReader {

public:
    ShowVideo() = default;

    SimpleShow show{1920,1080};

    void on_frame(FrameData &data) override {
        show.imshow(data.data(), data.cols(), data.rows());
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

    ShowVideo showVideo;

    showVideo.init(path);
    showVideo.read_packets();
    showVideo.end();

}