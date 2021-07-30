//
// Created by mateusz on 4/10/21.
//

#include "FrameReader.h"
#include "SImpleShow.h"


using namespace mk;

const int STANDARD_SIZE = 1036800;

// Clamp out of range values
#define CLAMP(t) (((t)>255)?255:(((t)<0)?0:(t)))

// Color space conversion for RGB
#define GET_R_FROM_YUV(y, u, v) ((298*(y)+409*(v)+128)>>8)
#define GET_G_FROM_YUV(y, u, v) ((298*(y)-100*(u)-208*(v)+128)>>8)
#define GET_B_FROM_YUV(y, u, v) ((298*(y)+516*(u)+128)>>8)


bool YUV422toRGB888(unsigned char *d, unsigned char *s, long size) {
    for (unsigned int i = 0; i < size / 8; ++i) {

        int y0 = *s++ - 16;
        int u0 = *s++ - 128;
        int y2 = *s++ - 16;
        int v = *s++ - 128;

//        LOG(std::to_string(y0) + " " + std::to_string(u0) + " " + std::to_string(y2) + " " + std::to_string(v));

        // RGB
        *d++ = CLAMP(GET_R_FROM_YUV(y0, u0, v));
        *d++ = CLAMP(GET_G_FROM_YUV(y0, u0, v));
        *d++ = CLAMP(GET_B_FROM_YUV(y0, u0, v));

        // RGB
        *d++ = CLAMP(GET_R_FROM_YUV(y2, u0, v));
        *d++ = CLAMP(GET_G_FROM_YUV(y2, u0, v));
        *d++ = CLAMP(GET_B_FROM_YUV(y2, u0, v));
    }
    return true;
}

class SplitPPM : public FrameReader {

public:
    SplitPPM() {
        this->show = new SimpleShow(1920, 1080);
    }

    std::string out_path_;
    size_t frame_counter = 0;

    SimpleShow *show;

    void on_frame(FrameData &data) override {
        //TIME_START(convert_to_rgb);
        std::fstream file;
        file.open(out_path_ + std::to_string(frame_counter++) + ".ppm", std::ios::out);

        auto frame = Eigen::Map<Eigen::Matrix<uint8_t, Eigen::Dynamic, Eigen::Dynamic>>(
                current_frame_info_.data(), current_frame_info_.height(), current_frame_info_.width());


        auto ptr = new uint8_t[1920 * 1080 * 6 / 4];

        LOG("Current frame size: " + std::to_string(current_frame_info_.bufferSize()));

        TRUE_OR_PANIC(
                YUV422toRGB888(current_frame_info_.data(), ptr, 1920 * 1080),
                "Conversion failed"
        );

        auto rgb = Eigen::Map<Eigen::Matrix<uint8_t, Eigen::Dynamic, Eigen::Dynamic>>(
                ptr, current_frame_info_.height(), current_frame_info_.width());

        show->imshow_color(ptr, 1920, 1080);


        // write out format
        file << "P3" << std::endl;
        // write out dimentions of the image
        //we have here bad dimentions
        file << current_frame_info_.width() << " " << current_frame_info_.height() << std::endl;
        // write out color depth
        file << "255" << std::endl;
        // convert YUV422 encoded pixels into RGB encoded pixels and write to file in plain text
        //file << yuv422_to_rgb(data).transpose() << std::endl;
        file << rgb.transpose() << std::endl;
        //TIME_STOP(convert_to_rgb, "converting to rgb took: ");
        delete[] ptr;
    }

};

int main(int argc, char **argv) {

    // Initialize my logger library
    mk::Logger::Config config = {
            .show_line = false,
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

    SplitPPM split_ppm;
    split_ppm.out_path_ = out_dir;
    split_ppm.init(path);
    split_ppm.read_packets();
    split_ppm.end();

}