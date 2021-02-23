//
// Created by mateusz on 06.02.2021.
//

#include "IO.h"
#include <iostream>

struct FOURCC {
  BYTE c_1;
  BYTE c_2;
  BYTE c_3;
  BYTE c_4;
};

DWORD IO::get_dword(std::fstream &file) {
  DWORD w;
  file.read((char *)&w, sizeof(w));
  return w;
}
WORD IO::get_word(std::fstream &file) {
  DWORD d;
  file.read((char *)&d, sizeof(d));
  return d;
}
BYTE IO::get_byte(std::fstream &file) {
  BYTE b;
  file.read((char *)&b, sizeof(b));
  return b;
}
Fourcc IO::get_fourcc(std::fstream &file) {
  FOURCC f = {};
  file.read((char *)&f, sizeof(f));
  Fourcc arr;
  arr = {f.c_1, f.c_2, f.c_3, f.c_4};
  log(arr);
  return arr;
}
void IO::skip(std::fstream &file, size_t how_far) {
  file.ignore(how_far);
}
void log(const Fourcc& fcc) {
  std::clog << "Fourcc: "
            << "\"" << fcc[0] << fcc[1] << fcc[2] << fcc[3] << "\""
            << std::endl;
}
void log(size_t value) { std::clog << "value: " << value << std::endl; }
