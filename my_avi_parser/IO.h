//
// Created by mateusz on 06.02.2021.
//

#ifndef AVI_PARSER_IO_H
#define AVI_PARSER_IO_H

#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>

typedef uint32_t DWORD;
typedef uint8_t BYTE;
typedef uint16_t WORD;
typedef std::array<BYTE, 4> Fourcc;


void log(const Fourcc& fcc);
void log(size_t value);

class IO {
public:
    static DWORD get_dword(std::fstream &);
    static WORD get_word(std::fstream &);
    static BYTE get_byte(std::fstream &);
    static Fourcc get_fourcc(std::fstream &);
    static void skip(std::fstream &, size_t);
};


#endif//AVI_PARSER_IO_H
