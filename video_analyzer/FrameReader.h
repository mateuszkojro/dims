//
// Created by mateusz on 3/8/21.
//

#ifndef VIDEO_ANALYZER_FRAMEREADER_H
#define VIDEO_ANALYZER_FRAMEREADER_H

// AvCpp
#include <formatcontext.h>
#include <codeccontext.h>


#include "av.h"

#include "Logger.h"

// Eigen
#include <Eigen/Dense>


namespace mk {

    typedef Eigen::Matrix<uint8_t, Eigen::Dynamic, Eigen::Dynamic> FrameData;

    /// class to make working on frames of a video easy
    class FrameReader {

    public:
        virtual void init(const std::string &path) final;

        virtual void on_start();

        virtual void read_packets() final;

        //virtual void on_packet(av::Packet&);

        virtual void on_frame(FrameData &);

        virtual void end() final;

    protected:
        av::FormatContext format_context_;
        av::Stream stream_;
        av::VideoDecoderContext decoder_context_;
        av::Codec codec_;
        ssize_t video_stream_id_;
        std::error_code ec_;
        av::VideoFrame current_frame_info_;
        FrameData current_frame_data_;


    private:

    };

};


#endif //VIDEO_ANALYZER_FRAMEREADER_H
