//
// Created by mateusz on 06.02.2021.
//

#include "Avi.h"
#include <cassert>
#include <fstream>

const Fourcc STRF = {'s', 't', 'r', 'f'};
const Fourcc STRH = {'s', 't', 'r', 'h'};
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
    hrdl->parse(file);
    // parsing hrdl part of the file

    movi->set_id(IO::get_fourcc(file));
    assert(movi->get_id() == LIST);
    movi->set_size(IO::get_dword(file));
    log(movi->get_size());
    movi->parse(file);

    this->data_ = {hrdl, movi};
}
void List::parse(std::fstream &file) {
    this->type_ = IO::get_fourcc(file);
    size_t i = this->get_size();
    while (i) {
        auto fourcc = IO::get_fourcc(file);
        Element *element;
        if (fourcc == LIST) {
            element = new List;
        } else {
            element = new Chunk;
            element->set_id(fourcc);
            //            element->set_id(IO::get_fourcc(file));
        }
        element->set_size(IO::get_dword(file));
        i -= element->get_size();
        element->parse(file);
        data_.push_back(element);
    }
}
void Chunk::parse(std::fstream &file) {
    if (this->get_id() == IDX1) return;
    size_t i = this->get_size();
    RawData *data = new RawData;
    data->set_size(i);
    data->parse(file);
    log(data->get_size());
    log(data->data_.size());
    //    while (i) {
    //        auto fourcc = IO::get_fourcc(file);
    //        Element *element;
    //        if (fourcc == LIST) {
    //            element = new List;
    //        } else {
    //            element = new RawData;
    //            //            element->set_id(IO::get_fourcc(file));
    //        }
    //        element->set_size(IO::get_dword(file));
    //        i -= element->get_size();
    //        element->parse(file);
    //        data_.push_back(element);
    //    }
}
void List::add_child(Element *element) {
    data_.push_back(element);
}
size_t List::get_size() {
    return size_;
}
void List::set_size(size_t size) {
    size_ = size;
}
void List::set_id(const Fourcc &id) {
    type_ = id;
}
Fourcc List::get_id() {
    return this->type_;
}
void Chunk::add_child(Element *element) {
    data_.push_back(element);
}
void Chunk::set_size(size_t size) {
    this->size = size;
}
size_t Chunk::get_size() {
    return this->size;
}
Fourcc Chunk::get_id() {
    return this->id;
}
void Chunk::set_id(const Fourcc &fourcc) {
    this->id = fourcc;
}

void RawData::add_child(Element *element) {
    assert(false);
}
void RawData::parse(std::fstream &file) {
    size_t i = this->get_size();
    while (i) {
        this->data_.push_back(IO::get_byte(file));
        i--;
    }
}
void RawData::set_size(size_t size) {
    this->size_ = size;
}
size_t RawData::get_size() {
    return this->size_;
}
Fourcc RawData::get_id() {
    assert(false);
    return Fourcc();
}
void RawData::set_id(const Fourcc &fourcc) {
    assert(false);
}
