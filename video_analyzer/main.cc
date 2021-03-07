
#include <chrono>
#include <cstddef>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <ratio>
#include <set>
#include <string>

// #include "audioresampler.h"
#include "av.h"
// #include "avutils.h"
// #include "codec.h"
// #include "ffmpeg.h"
// #include "packet.h"
// #include "videorescaler.h"

// API2
#include "codec.h"
#include "codeccontext.h"
#include "format.h"
#include "formatcontext.h"
#include "Logger.h"
#include "debug.h"

using namespace std;
using namespace av;
using namespace mk;

#define SAVE_FRAMES false
#define ANALYZE_FRAME true

int main(int argc, char **argv) {

    // Initialize my logger library
    mk::Logger::Config config = {
            .show_line = false,
            .show_file = false,
            .show_func = true,
            .to_file = false,
            .timing = true
    };

    mk::Logger::init(mk::Logger::all, config);

    av::init();

    av::setFFmpegLoggingLevel(AV_LOG_WARNING);

    TRUE_OR_PANIC(argc >= 3,
                  "Specify path to a file as a 1st arg and output folder as a second");

    std::string path = argv[1];
    std::string out_dir = argv[2];

    ssize_t video_stream_id = -1;
    VideoDecoderContext decoder_context;
    Stream stream;
    error_code ec;

    {

        FormatContext format_context;

        format_context.openInput(path, ec);
        TRUE_OR_PANIC((bool) !ec,
                      "Can't open a file");

        LOG("No of streams: " + std::to_string(format_context.streamsCount()));

        // check if any stream in file
        format_context.findStreamInfo(ec);
        TRUE_OR_PANIC((bool) !ec,
                      "No data streams in a file");

        // find the 1 stream in a file containing a video
        for (size_t i = 0; i < format_context.streamsCount(); ++i) {
            auto st = format_context.stream(i);
            if (st.mediaType() == AVMEDIA_TYPE_VIDEO) {
                video_stream_id = i;
                stream = st;
                break;
            }
        }

        LOG("Video stream id: " + std::to_string(video_stream_id));

        // check if the video stream empty
        TRUE_OR_PANIC(!stream.isNull(), "Video stream not found");

        // detect the format of the video stream
        if (stream.isValid()) {
            decoder_context = VideoDecoderContext(stream);
            Codec codec = findDecodingCodec(decoder_context.raw()->codec_id);
            decoder_context.setCodec(codec);
            decoder_context.setRefCountedFrames(true);
            decoder_context.open({{"threads", "8"}}, Codec(), ec);
            // vdec.open(ec);
            TRUE_OR_PANIC((bool) !ec, "Cannot open this codec");
        }


        size_t frame_count = 0;
        // loop through all the frames
        while (Packet stream_packet = format_context.readPacket(ec)) {
            frame_count++;

            TRUE_OR_PANIC((bool) !ec, "Packet reading error: " + ec.message());

            if (stream_packet.streamIndex() != video_stream_id) {
                continue;
            }

            auto timestamp = stream_packet.ts();
//            clog << "Read packet: " << timestamp << " / " << timestamp.seconds() << " / " << stream_packet.timeBase() << " / st: "
//                 << stream_packet.streamIndex() << endl;

            LOG(
                    "Read packet: " + std::to_string((double) timestamp) + " / " + "time base" + " index: " +
                    std::to_string(stream_packet.streamIndex())
            );

            // calculate time needed to decode current frame - i needed to check
            TIME_START(reading_frame);
            VideoFrame frame = decoder_context.decode(stream_packet, ec);
            TIME_STOP(reading_frame, "Reading frame ");

            // check if frame is correct
            TRUE_OR_PANIC((bool) !ec, "Error: " + ec.message());

            if (!frame) {
                ERR("Empty frame");
                continue;
            }

#if SAVE_FRAMES

            uint8_t *buff;
            buff = frame.data();

            std::fstream f;

            std::string name = out_dir + "frame" + std::to_string(frame_count);
            f.open(name, std::ios::out | std::ios::binary);

            f.write((char *) buff, frame.bufferSize());
            f.close();

#endif

#if ANALYZE_FRAME

            uint8_t* frame_data;

            frame_data = frame.data();



#endif
            timestamp = frame.pts();

            // show some info about the frame
            LOG(
                    "Frame: " +
                    std::to_string(frame.width()) + "x" + std::to_string(frame.height()) +
                    ", size= " + std::to_string(frame.size()) +
                    ", timestamp=" + std::to_string((double) timestamp) +
                    ", ref: " + std::to_string(frame.isReferenced()) + ":" + std::to_string(frame.refCount())
            );
        }

        LOG("Starting flushing frames");
        while (true) {
            VideoFrame frame = decoder_context.decode(Packet(), ec);
            TRUE_OR_PANIC((bool) !ec, "Error: " + ec.message());
            if (!frame)
                break;
            auto ts = frame.pts();

//            clog << "  Frame: " << frame.width() << "x" << frame.height() << ", size=" << frame.size() << ", ts=" << ts
//                 << ", tm: " << ts.seconds() << ", tb: " << frame.timeBase() << ", ref=" << frame.isReferenced() << ":"
//                 << frame.refCount() << endl;
            LOG(
                    "Frame: " +
                    std::to_string(frame.width()) + "x" + std::to_string(frame.height()) +
                    ", size= " + std::to_string(frame.size()) +
                    ", ts=" + std::to_string((double) ts) +
                    ", ref: " + std::to_string(frame.isReferenced()) + ":" + std::to_string(frame.refCount())
            );
        }

        // NOTE: stream decodec must be closed/destroyed before
        // ictx.close();
        // vdec.close();
    }
}
