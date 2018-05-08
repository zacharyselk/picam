extern "C"
{
#include<libavcodec/avcodec.h>
#include<libavformat/avformat.h>
#include<libavutil/mathematics.h>
}
#include<iostream>

int main()
{
  //std::cout << avcodec_find_decoder(AV_CODEC_ID_H264) << '\n';
  AVCodecParserContext *codecContext = av_parser_init(AV_CODEC_ID_H264);
  AVFormatContext *formatContext = avformat_alloc_context();

  avformat_open_input(&formatContext, '../video/', NULL, NULL);
  
  
  return 0;
}
