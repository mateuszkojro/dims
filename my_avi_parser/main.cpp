#include "Avi.h"
#include "IO.h"
#include <array>
#include <fstream>
#include <iostream>

/*
 *  Verry simple AVI parser only for educational purposes 
 *
 *  it mostly works - incoming frames are saved in memory 
 *
 *  but has some bugs - mainly it leaks memory in multiple places 
 *  to be fixed when i have some time 
 */

int main() {
  std::fstream file;
  file.open("./stars.avi", std::ios::in | std::ios::binary);

  std::vector<BYTE> data;

  data.data();

  Avi avi;
  avi.parse(file);

}
