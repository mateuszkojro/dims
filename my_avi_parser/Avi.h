//
// Created by mateusz on 06.02.2021.
//

#ifndef AVI_PARSER_AVI_H
#define AVI_PARSER_AVI_H
#include "IO.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>

typedef uint32_t DWORD;
typedef uint8_t BYTE;
typedef uint16_t WORD;
typedef std::array<BYTE, 4> Fourcc;

class Element {
public:
  virtual void add_child(Element *) = 0;
  virtual void parse(std::fstream &) = 0;
  virtual void set_size(size_t) = 0;
  virtual size_t get_size() = 0;
  virtual const Fourcc& get_id() = 0;
  virtual void set_id(const Fourcc &) = 0;
};

class Avi {
public:
  void parse(std::fstream &file);

private:
  /// @brief current position inside the loaded file
  size_t position_;
  size_t size_;
  /// @brief Header describing whole avi file
  struct {
    size_t size_;              /// @brief cb from windows docs
    size_t number_of_frames_;  /// @brief number of all the frames i the file
    size_t number_of_streams_; /// @brief how many different streams in file
                               /// (for audio and video - 2)
    size_t
        size_to_contain_largest_chunk_; /// @brief the biggest size we need to
                                        /// allocate to accommodate any chunk
    size_t width_;                      /// @brief width of the frames
    size_t height_;                     /// @brief height of the frames
  } AviMainHeader;

public:
  std::vector<Element *> data_;
};

class List : public Element {
public:
  void add_child(Element *element) override;
  void parse(std::fstream &) override;

  const Fourcc& get_id() override;
  void set_id(const Fourcc &name) override;

private:
  DWORD size_;

public:
  size_t get_size() override;
  void set_size(size_t size) override;

private:
  Fourcc type_;

public:
  std::vector<Element *> data_;
};

class Chunk : public Element {
public:
  void add_child(Element *element) override;
  void parse(std::fstream &) override;

  void set_size(size_t size) override;
  size_t get_size() override;

  const Fourcc& get_id() override;
  void set_id(const Fourcc &fourcc) override;

private:
  Fourcc id;
  /// @brief size of the data in the chunk without the padding, id or size
  DWORD size;
  std::vector<BYTE> data_;
};

/**
 * @brief we are recursively building up our Avi structure no interpreting at
 * this stage
 * @param avi reference to build up obj
 */
void parse_avi(Avi &avi, std::fstream &file);
Chunk parse_chunk(Chunk &chunk);

#endif // AVI_PARSER_AVI_H
