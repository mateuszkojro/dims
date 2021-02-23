
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

#include "audioresampler.h"
#include "av.h"
#include "avutils.h"
#include "codec.h"
#include "ffmpeg.h"
#include "packet.h"
#include "videorescaler.h"

// API2
#include "codec.h"
#include "codeccontext.h"
#include "format.h"
#include "formatcontext.h"

using namespace std;
using namespace av;

#define SAVE_FRAMES 0

int main(int argc, char **argv) {
  if (argc < 2) {
    std::cerr << "Give a path to file as 1st arg" << std::endl;
    return 1;
  }

  av::init();
  av::setFFmpegLoggingLevel(AV_LOG_DEBUG);

  string path{argv[1]};

  ssize_t video_stream_id = -1;
  VideoDecoderContext decoder_context;
  Stream stream;
  error_code ec;

  int count = 0;

  {

    FormatContext format_context;

    format_context.openInput(path, ec);
    if (ec) {
      cerr << "Can't open input\n";
      return 1;
    }

    cerr << "Streams: " << format_context.streamsCount() << endl;

    // check if any stream in file
    format_context.findStreamInfo(ec);
    if (ec) {
      cerr << "Can't find streams: " << ec << ", " << ec.message() << endl;
      return 1;
    }

    // find the 1 stream in a file containing a video
    for (size_t i = 0; i < format_context.streamsCount(); ++i) {
      auto st = format_context.stream(i);
      if (st.mediaType() == AVMEDIA_TYPE_VIDEO) {
        video_stream_id = i;
        stream = st;
        break;
      }
    }

    cerr << video_stream_id << endl;

    // check if the video stream empty
    if (stream.isNull()) {
      cerr << "Video stream not found\n";
      return 1;
    }

    // detect the format of the video stream
    if (stream.isValid()) {
      decoder_context = VideoDecoderContext(stream);

      Codec codec = findDecodingCodec(decoder_context.raw()->codec_id);

      decoder_context.setCodec(codec);
      decoder_context.setRefCountedFrames(true);

      decoder_context.open({{"threads", "8"}}, Codec(), ec);
      // vdec.open(ec);
      if (ec) {
        cerr << "Can't open codec\n";
        return 1;
      }
    }

    size_t sum = 0;

    // loop through all the frames
    while (Packet stream_packet = format_context.readPacket(ec)) {
      if (ec) {
        clog << "Packet reading error: " << ec << ", " << ec.message() << endl;
        return 1;
      }

      if (stream_packet.streamIndex() != video_stream_id) {
        continue;
      }

      auto ts = stream_packet.ts();
      clog << "Read packet: " << ts << " / " << ts.seconds() << " / "
           << stream_packet.timeBase()
           << " / st: " << stream_packet.streamIndex() << endl;

      // calculate time neeaded to decode current frame - i neded to check
      auto start = std::chrono::high_resolution_clock::now();
      VideoFrame frame = decoder_context.decode(stream_packet, ec);
      auto stop = std::chrono::high_resolution_clock::now();

      auto time =
          std::chrono::duration_cast<std::chrono::microseconds>(stop - start)
              .count();
      std::clog << "Czas: " << time << std::endl;

      // sum times to calculate avg
      sum += time;

      // check if frame is correct
      if (ec) {
        cerr << "Error: " << ec << ", " << ec.message() << endl;
        return 1;
      } else if (!frame) {
        cerr << "Empty frame\n";
        // continue;
      }

#if SAVE_FRAMES

      uint8_t *buff = (uint8_t *)malloc(frame.bufferSize() * sizeof(uint8_t));
      buff = frame.data();

      std::fstream f;

      std::string name = "./frames/frame" + std::to_string(count);
      f.open(name, std::ios::out | std::ios::binary);

      for (int i = 0; i < frame.bufferSize(); i++) {
        f << buff[i];
      }

#endif

      // i am only reading first 100 frames then i am stoping and showing the
      // average
      count++;
      if (count > 10) {
        std::cout << "Average decoding time: " << sum / 100 << std::endl;
        break;
      }

      ts = frame.pts();

      // show some info about the frame
      clog << "  Frame: " << frame.width() << "x" << frame.height()
           << ", size=" << frame.size() << ", ts=" << ts
           << ", tm: " << ts.seconds() << ", tb: " << frame.timeBase()
           << ", ref=" << frame.isReferenced() << ":" << frame.refCount()
           << endl;
    }

    clog << "Flush frames;\n";
    while (true) {
      VideoFrame frame = decoder_context.decode(Packet(), ec);
      if (ec) {
        cerr << "Error: " << ec << ", " << ec.message() << endl;
        return 1;
      }
      if (!frame)
        break;
      auto ts = frame.pts();
      clog << "  Frame: " << frame.width() << "x" << frame.height()
           << ", size=" << frame.size() << ", ts=" << ts
           << ", tm: " << ts.seconds() << ", tb: " << frame.timeBase()
           << ", ref=" << frame.isReferenced() << ":" << frame.refCount()
           << endl;
    }

    // NOTE: stream decodec must be closed/destroyed before
    // ictx.close();
    // vdec.close();
  }
}
