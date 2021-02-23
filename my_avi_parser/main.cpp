#include "Avi.h"
#include "IO.h"
#include <array>
#include <fstream>
#include <iostream>
#include <ostream>

/*
 *  Verry simple AVI parser only for educational purposes
 *
 *  it mostly works - incoming frames are saved in memory
 *
 *  but has some bugs - mainly it leaks memory in multiple places
 *  to be fixed when i have some time
 *
 * If performace ever become a prblem with decoding we can skip interpreting all
 * the headers and be maybe it will help - that might be usefull if ffmpeg is to
 * slow and we dont have any more ideas
 */

int main() {
  std::fstream file;
  file.open("./stars.avi", std::ios::in | std::ios::binary);

  std::vector<BYTE> data;

  data.data();

  Avi avi;
  avi.parse(file);

  for (auto data : avi.data_) {
    std::cout << data->get_id().data() << std::endl;
  }
}
