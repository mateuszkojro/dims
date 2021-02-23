//
// Created by mateusz on 06.02.2021.
//

#include "Avi.h"
#include <cassert>
#include <cstddef>
#include <fstream>
#include <iostream>
#include <ostream>
#include <string>

// some names of chunks
const Fourcc STRF = {'s', 't', 'r', 'f'};
const Fourcc STRH = {'s', 't', 'r', 'h'};
const Fourcc JUNK = {'J', 'U', 'N', 'K'};
const Fourcc AVIH = {'a', 'v', 'i', 'h'};
const Fourcc LIST = {'L', 'I', 'S', 'T'};
const Fourcc IDX1 = {'I', 'D', 'X', '1'};

void Avi::parse(std::fstream &file) {
  auto riff = IO::get_fourcc(file);
  log(riff);
  this->size_ = IO::get_dword(file);
  log(this->size_);
  auto avi = IO::get_fourcc(file);
  log(avi);
  List *hrdl = new List;
  List *movi = new List;

  // parsing info headers of a file

  hrdl->set_id(IO::get_fourcc(file));
  assert(hrdl->get_id() == LIST);
  hrdl->set_size(IO::get_dword(file));
  log(hrdl->get_size());
  std::cout << "Begin parsing" << std::endl;
  hrdl->parse(file);

  // parsing hrdl part of the file

  movi->set_id(IO::get_fourcc(file));
  movi->set_size(IO::get_dword(file));
  log(movi->get_size());
  movi->parse(file);

  this->data_ = {hrdl, movi};
}

void List::parse(std::fstream &file) {

  this->type_ = IO::get_fourcc(file);

  long int left = this->get_size();

  while (left > 0) {
    auto fourcc = IO::get_fourcc(file);

    Element *element;

    // list packet have "LIST" fourcc everything else is a CHUNK
    if (fourcc == LIST) {
      element = new List;
    } else {
      element = new Chunk;
      element->set_id(fourcc);

      // "JUNK" means some padding in binary file we can skip it completly
      if (element->get_id() == JUNK) {
        size_t skip_size = IO::get_dword(file);
        IO::skip(file, skip_size);
        continue;
      }
    }

    // get the size of the next element and set it
    element->set_size(IO::get_dword(file));

    // decrease number of bytes left to read
    left -= element->get_size();

    // parse next symbol
    element->parse(file);

    data_.push_back(element);
  }
}

void Chunk::parse(std::fstream &file) {
  long int left = this->get_size();
  this->data_.resize(left);

  // read data to the end of the chunk
  // ofc it should be read whole and stored that way
  while (left > 0) {
    this->data_.push_back(IO::get_byte(file));
    left--;
  }
}

/// -----------------------------------------------
/// seters and geters dont need to worry about them
/// ------------------------------------------------

void List::add_child(Element *element) { data_.push_back(element); }

size_t List::get_size() { return size_; }

void List::set_size(size_t size) { size_ = size; }

void List::set_id(const Fourcc &id) { type_ = id; }

const Fourcc &List::get_id() { return this->type_; }

void Chunk::add_child(Element *element) { assert(false); }

void Chunk::set_size(size_t size) { this->size = size; }

size_t Chunk::get_size() { return this->size; }

const Fourcc &Chunk::get_id() { return this->id; }

void Chunk::set_id(const Fourcc &fourcc) { this->id = fourcc; }
