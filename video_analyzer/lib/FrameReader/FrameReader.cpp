//
// Created by mateusz on 3/8/21.
//

#include "FrameReader.h"

void mk::FrameReader::init(const std::string &path) {
    av::init();

    //av::setFFmpegLoggingLevel(AV_LOG_DEBUG);


    format_context_.openInput(path, ec_);
    TRUE_OR_PANIC((bool) !ec_, "Can't open a file");

    LOG("No of streams: " + std::to_string(format_context_.streamsCount()));

    // check if any stream in file
    format_context_.findStreamInfo(ec_);
    TRUE_OR_PANIC((bool) !ec_, "No data streams in a file");

    // find the 1 stream in a file containing a video
    for (size_t i = 0; i < format_context_.streamsCount(); ++i) {
        auto st = format_context_.stream(i);
        if (st.mediaType() == AVMEDIA_TYPE_VIDEO) {
            video_stream_id_ = i;
            stream_ = st;
            break;
        }
    }

    LOG("Video stream id: " + std::to_string(video_stream_id_));

    // check if the video stream empty
    TRUE_OR_PANIC(!stream_.isNull(), "Video stream not found");

    // detect the format of the video stream
    if (stream_.isValid()) {
        decoder_context_ = av::VideoDecoderContext(stream_);
        av::Codec codec = av::findDecodingCodec(decoder_context_.raw()->codec_id);
        decoder_context_.setCodec(codec);
        decoder_context_.setRefCountedFrames(true);
        decoder_context_.open({{"threads", "8"}}, av::Codec(), ec_);
        // vdec.open(ec);
        TRUE_OR_PANIC((bool) !ec_, "Cannot open this codec");
    }
}

void mk::FrameReader::end() {
    LOG("Starting flushing frames");
    while (true) {
        av::VideoFrame frame = decoder_context_.decode(av::Packet(), ec_);
        TRUE_OR_PANIC((bool) !ec_, "Error: " + ec_.message());
        if (!frame)
            break;
        auto ts = frame.pts();

        //            clog << "  Frame: " << frame.width() << "x" <<
        //            frame.height() << ", size=" << frame.size() << ", ts=" << ts
        //                 << ", tm: " << ts.seconds() << ", tb: " <<
        //                 frame.timeBase() << ", ref=" << frame.isReferenced() <<
        //                 ":"
        //                 << frame.refCount() << endl;
        LOG("Frame: " + std::to_string(frame.width()) + "x" +
            std::to_string(frame.height()) + ", size= " +
            std::to_string(frame.size()) + ", ts=" + std::to_string((double) ts) +
            ", ref: " + std::to_string(frame.isReferenced()) + ":" +
            std::to_string(frame.refCount()));
    }

    // NOTE: stream decodec must be closed/destroyed before
    // ictx.close();
    // vdec.close();

}

void mk::FrameReader::read_packets() {
    while (av::Packet stream_packet = format_context_.readPacket(ec_)) {

        TIME_START(frame_ffmpeg);

        TRUE_OR_PANIC((bool) !ec_, "Packet reading error: " + ec_.message());

        if (stream_packet.streamIndex() != video_stream_id_) {
            continue;
        }

        auto timestamp = stream_packet.ts();
        //            clog << "Read packet: " << timestamp << " / " <<
        //            timestamp.seconds() << " / " << stream_packet.timeBase() <<
        //            " / st: "
        //                 << stream_packet.streamIndex() << endl;

        LOG("Read packet: " + std::to_string((double) timestamp) + " / " +
            "time base" +
            " index: " + std::to_string(stream_packet.streamIndex()));

        // calculate time needed to decode current frame - i needed to check
        current_frame_info_ = decoder_context_.decode(stream_packet, ec_);


        // check if frame is correct
        TRUE_OR_PANIC((bool) !ec_, "Error: " + ec_.message());

        if (!current_frame_info_) {
            ERR("Empty frame");
            continue;
        }



        // We are specifing stride here to ignore values that are nor grayscale channel
        current_frame_data_ = Eigen::Map<Eigen::Matrix<uint8_t, Eigen::Dynamic, Eigen::Dynamic>, 0, Eigen::InnerStride<3>>(
                current_frame_info_.data(), current_frame_info_.height(), current_frame_info_.width());
        TIME_STOP(frame_ffmpeg,"Frame eigen: ");

        on_frame(current_frame_data_);



    }
}

void mk::FrameReader::on_start() {
    // show some info about the frame
    LOG("Start from base");
}

void mk::FrameReader::on_frame(FrameData &) {
    // show some info about the frame
    LOG("Frame readed from base");
}