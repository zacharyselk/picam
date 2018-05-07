extern "C"
{
#include<libavcodec/avcodec.h>
#include<libavformat/avio.h>
#include<libavutil/mathematics.h>
}
#include<iostream>

int main()
{
  //std::cout << avcodec_find_decoder(AV_CODEC_ID_H264) << '\n';
  AVCodecParserContext *context = av_parser_init(AV_CODEC_ID_H264);
  av_open_input_file(&context, "test.h264", 0, 0, 0);
  
  
  return 0;
}
